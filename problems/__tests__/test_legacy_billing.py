# tests/test_billing.py
import types
import billing
import pytest

# --- Test seams / fakes ---

class FxFake:
    def __init__(self, rate=2.0):
        self.rate = rate
    def convert(self, amount_usd, code):
        return round(amount_usd * self.rate, 2)

class MailSink:
    def __init__(self):
        self.sent = []
    def send(self, address, body):
        self.sent.append((address, body))

class ClockFake:
    def now_str(self):
        return "Tue Aug 12 12:00:00 2025"  # stable string

def patch_seams(monkeypatch, fx=None, mail=None, clock=None, rnd=None):
    # Extract & Override seam via monkeypatch: wrap dependencies the function uses
    fx = fx or FxFake()
    mail = mail or MailSink()
    clock = clock or ClockFake()
    rnd = rnd or (lambda: 999)  # never triggers random promo
    monkeypatch.setattr(billing, "usd_to_currency", lambda amt, code: fx.convert(amt, code))
    monkeypatch.setattr(billing, "send_email", lambda addr, body: mail.send(addr, body))
    monkeypatch.setattr(billing.time, "ctime", lambda: clock.now_str())
    monkeypatch.setattr(billing.random, "randint", lambda a, b: rnd())

    return types.SimpleNamespace(fx=fx, mail=mail, clock=clock)

# --- Characterization tests (lock current quirks) ---

def test_characterize_random_promo_disabled_and_bulk_bug(monkeypatch):
    deps = patch_seams(monkeypatch)  # rnd never hits 1
    cart = [{"sku":"A","qty":10,"unit_price_usd":5.0}]  # subtotal=50, bulk shouldn’t apply… but legacy applies (BUG)
    total = billing.calc_total_and_notify(cart, "u@x", currency="USD")
    # Legacy bug: 5% off even though <100
    subtotal = 50 * 0.95
    expected = round(subtotal * (1 + billing.TAX_RATE), 2)
    assert total == pytest.approx(expected)

def test_characterize_fx_call_and_email(monkeypatch):
    deps = patch_seams(monkeypatch, fx=FxFake(rate=3.0))
    cart = [{"sku":"A","qty":1,"unit_price_usd":100.0}]
    total = billing.calc_total_and_notify(cart, "a@b", currency="EUR")
    usd = 100.0 * (1 + billing.TAX_RATE)
    assert total == pytest.approx(round(usd * 3.0, 2))
    assert len(deps.mail.sent) == 1
    assert "Your total is" in deps.mail.sent[0][1]

# --- New desired behavior (TDD specs) ---

def test_bulk_discount_applies_only_when_pre_discount_total_at_least_100(monkeypatch):
    patch_seams(monkeypatch)
    cart = [{"sku":"X","qty":10,"unit_price_usd":5.0}]  # subtotal=50
    total = billing.calc_total_and_notify(cart, "u@x", currency="USD")
    expected = round(50 * (1 + billing.TAX_RATE), 2)  # no 5% off now
    assert total == pytest.approx(expected)

def test_blackfriday_or_welcome10_knocks_10_before_tax(monkeypatch):
    patch_seams(monkeypatch)
    cart = [
        {"sku":"A-BLACKFRIDAY","qty":2,"unit_price_usd":30.0},  # subtotal 60
        {"sku":"B","qty":2,"unit_price_usd":20.0},              # subtotal 40
    ]  # subtotal 100 => bulk applies + promo $10
    # Expected with new rules:
    pre = 100.0
    pre = pre * 0.95  # bulk (>=100)
    pre = max(pre - 10.0, 0.0)  # promo
    expected = round(pre * (1 + billing.TAX_RATE), 2)
    assert billing.calc_total_and_notify(cart, "u@x", "USD") == pytest.approx(expected)

def test_never_negative_after_discounts_and_tax(monkeypatch):
    patch_seams(monkeypatch)
    cart = [{"sku":"CHEAP-WELCOME10","qty":1,"unit_price_usd":5.0}]
    total = billing.calc_total_and_notify(cart, "u@x", "USD")
    assert total >= 0.0
