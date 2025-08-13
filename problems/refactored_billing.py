# billing.py (refactored)
import random, time, json, urllib.request
TAX_RATE = 0.0825

# ---- Collaborators (wrappers) ----
class FxConverter:
    def convert(self, amount_usd: float, currency_code: str) -> float:
        url = f"https://api.example.com/fx?base=USD&symbols={currency_code}"
        with urllib.request.urlopen(url, timeout=2) as r:
            data = json.loads(r.read().decode("utf-8"))
        return round(amount_usd * data["rates"][currency_code], 2)

class Mailer:
    def send(self, address: str, body: str) -> None:
        print(f"EMAIL to {address}: {body}")

class Clock:
    def now_str(self) -> str:
        return time.ctime()

# Legacy adapter preserved for monkeypatched tests
def usd_to_currency(amount_usd: float, currency_code: str) -> float:
    return FxConverter().convert(amount_usd, currency_code)

def send_email(address: str, body: str) -> None:
    Mailer().send(address, body)

# ---- Sprout Method: pure price computation ----
def compute_total_usd(cart, rng=lambda: random.randint(1, 20), apply_bulk_threshold=100.0):
    subtotal = sum(i["qty"] * i["unit_price_usd"] for i in cart)

    # New rule: bulk only if pre-discount subtotal >= threshold
    if subtotal >= apply_bulk_threshold:
        subtotal *= 0.95

    # New feature: promo codes (-BLACKFRIDAY or -WELCOME10) => -$10 before tax
    has_promo = any(
        i["sku"].endswith("-BLACKFRIDAY") or i["sku"].endswith("-WELCOME10")
        for i in cart
    )
    if has_promo:
        subtotal -= 10.0

    # Remove non-deterministic random promo from core logic (legacy kept off by default)
    # (We keep seam rng for backward compatibility if desired: off by default in caller.)

    subtotal = max(subtotal, 0.0)
    tax = subtotal * TAX_RATE
    total_usd = max(subtotal + tax, 0.0)
    return round(total_usd, 2)

# ---- Public entrypoint preserved; collaborators injectable (seam) ----
def calc_total_and_notify(cart, user_email, currency="USD",
                          fx: FxConverter = None, mailer: Mailer = None, clock: Clock = None,
                          rng=None):
    fx = fx or FxConverter()
    mailer = mailer or Mailer()
    clock = clock or Clock()
    rng = rng or (lambda: random.randint(1, 20))  # currently unused in compute_total_usd

    total_usd = compute_total_usd(cart, rng=rng)

    total = total_usd if currency == "USD" else fx.convert(total_usd, currency)
    mailer.send(user_email, f"Thanks! Your total is {total} {currency} at {clock.now_str()}")
    return total



# How this demonstrates Feathers’ principles
# Characterization tests lock today’s behavior before refactors (you captured the bulk-discount bug and the side-effects).

# Seams via constructor/parameter injection and monkeypatching enable tests without touching production’s call sites.

# Sprout Method (compute_total_usd) isolates pure pricing logic from I/O.

# Humble Object pattern moves non-determinism/time/email out to simple collaborators (Clock, Mailer, FxConverter) that are easy to fake.

# Wrap Class hides the HTTP FX call behind FxConverter, enabling replacement in tests.

# Extract & Override style is simulated with pytest’s monkeypatch on legacy globals and optional parameters.

# Suggested interview scoring rubric (quick)
# 30% Tests first: clear characterization + new-behavior tests.

# 25% Proper seams & DI; no network/time/randomness in the core calc.

# 25% Correctness of new rules (threshold bulk & promo).

# 10% Small safe steps (commit notes), readable code.

# 10% Discussion: how they’d continue (delete dead code, move constants to config, add logging, split modules).

# How a strong candidate would narrate their steps (talk track)
# Pin existing behavior with two characterization tests (bulk bug, email/FX call made).

# Introduce seams (Mailer/Fx/Clock/rng) without changing the signature for current callers.

# Sprout Method for pure computation, redirect entrypoint to it.

# Add TDD tests for new rules; make them pass; keep random promo disabled.

# Clean-ups: clamp negatives, round at boundaries, keep backward-compatible entrypoint.