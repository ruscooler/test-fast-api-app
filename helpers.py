from decimal import Decimal, ROUND_HALF_UP


format_money = lambda x: x.quantize(Decimal('.01'), ROUND_HALF_UP)

DISCOUNTS = {
    1000: 0.03,
    5000: 0.05,
    7000: 0.07,
    10000: 0.10,
    50000: 0.15,
}
TAXES = {
    "UT": 0.0685,
    "NV": 0.08,
    "TX": 0.0625,
    "AL": 0.04,
    "CA": 0.0825,
}


def get_cost_with_discount(count, price):
    total = count * price
    discounts_lst = list(filter(lambda x: total >= x, DISCOUNTS.keys()))
    if not discounts_lst:
        return total
    return total * (1 - Decimal(DISCOUNTS[discounts_lst[-1]]))


def get_tax(amount, state_code):
    return amount * Decimal(TAXES[state_code])

