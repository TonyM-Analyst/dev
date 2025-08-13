# billing.py
import random, time, json, urllib.request

TAX_RATE = 0.0825

def usd_to_currency(amount_usd: float, currency_code: str) -> float:
    # Hit public API (pretend!) – USD base
    url = f"https://api.example.com/fx?base=USD&symbols={currency_code}"
    with urllib.request.urlopen(url, timeout=2) as r:
        data = json.loads(r.read().decode("utf-8"))
    return round(amount_usd * data["rates"][currency_code], 2)

def send_email(address: str, body: str) -> None:
    # Pretend to send
    print(f"EMAIL to {address}: {body}")

def calc_total_and_notify(cart, user_email, currency="USD"):
    """
    cart: list of {"sku": str, "qty": int, "unit_price_usd": float}
    discount_code: sometimes embedded in sku like "SKU-...-BLACKFRIDAY"
    Business rules (some incorrect/outdated):
      - bulk discount: if any item qty >= 10, 5% off entire cart (BUG: applies even when total < 100)
      - random promo: 1 in 20 chance applies extra $5 off (non-deterministic!)
      - tax: TAX_RATE on subtotal after discounts
      - currency conversion after tax
    """
    subtotal = 0.0
    for item in cart:
        subtotal += item["qty"] * item["unit_price_usd"]
    if any(i["qty"] >= 10 for i in cart):
        subtotal *= 0.95
    # Random promo
    if random.randint(1, 20) == 1:
        subtotal -= 5.0
    tax = subtotal * TAX_RATE
    total_usd = max(subtotal + tax, 0.0)

    # feature: promo codes embedded in SKU should knock 10 USD off (BROKEN: not implemented)
    # conversion
    total = total_usd if currency == "USD" else usd_to_currency(total_usd, currency)
    send_email(user_email, f"Thanks! Your total is {total} {currency} at {time.ctime()}")
    return total
