from decimal import Decimal

import uvicorn
from fastapi import FastAPI, Query, HTTPException

from helpers import format_money, get_cost_with_discount, get_tax, TAXES

app = FastAPI()


@app.get("/get_order_cost/")
async def get_order_cost(
    count: Decimal = Query(..., ge=0, description="Count of goods"),
    price: Decimal = Query(..., ge=0, description="Price of one good"),
    state_code: str = Query(..., description="State code"),
):
    if state_code not in TAXES.keys():
        raise HTTPException(status_code=400, detail="State code not found")

    subtotal = get_cost_with_discount(count, price)
    tax = get_tax(subtotal, state_code)
    return {
        "subtotal": format_money(subtotal),
        "tax": format_money(tax),
        "total": format_money(subtotal + tax),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
