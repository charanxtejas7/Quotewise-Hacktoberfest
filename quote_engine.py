from collections import defaultdict


def normalize_item_name(name: str) -> str:
    """Normalize item names for basic comparison."""
    return " ".join(name.strip().lower().split())


def compare_quotes(quote_a: list, quote_b: list) -> dict:
    """Compare quotation items using quantity multiplied by unit price."""

    def aggregate(items):
        totals = defaultdict(float)

        for item in items:
            name = normalize_item_name(item["name"])
            quantity = float(item["quantity"])
            unit_price = float(item["unit_price"])

            if not name:
                raise ValueError("Item names cannot be empty.")

            if quantity <= 0:
                raise ValueError("Quantities must be greater than zero.")

            if unit_price < 0:
                raise ValueError("Unit prices cannot be negative.")

            totals[name] += quantity * unit_price

        return dict(totals)

    a = aggregate(quote_a)
    b = aggregate(quote_b)

    all_items = sorted(set(a) | set(b))
    comparison = []

    for name in all_items:
        price_a = round(a.get(name, 0), 2)
        price_b = round(b.get(name, 0), 2)

        if name in a and name in b:
            status = "Both"
        elif name in a:
            status = "Only in Quote A"
        else:
            status = "Only in Quote B"

        comparison.append({
            "item": name.title(),
            "quote_a": price_a,
            "quote_b": price_b,
            "difference": round(price_b - price_a, 2),
            "status": status,
        })

    total_a = round(sum(a.values()), 2)
    total_b = round(sum(b.values()), 2)

    return {
        "items": comparison,
        "total_a": total_a,
        "total_b": total_b,
        "difference": round(total_b - total_a, 2),
        "cheaper_quote": (
            "Quote A"
            if total_a < total_b
            else "Quote B"
            if total_b < total_a
            else "Same total"
        ),
    }