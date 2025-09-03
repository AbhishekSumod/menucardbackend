from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

class MenuText(BaseModel):
    text: str

# Function to extract price from a line
def extract_price(line: str):
    match = re.search(r"(₹|\$|rs\.?|inr|usd|eur|aed|gbp|£|€)?\s*([0-9]+(?:\.[0-9]{1,2})?)", line, re.IGNORECASE)
    if match:
        return match.group(0)
    return None

@app.post("/parse_menu")
def parse_menu(data: MenuText):
    text = data.text
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    items = []

    for line in lines:
        price = extract_price(line)

        if price:
            # remove price from the line and keep the rest as name
            name = line.replace(price, "").strip()
            items.append({"name": name.title(), "price": price})
        else:
            # if no price, still add item
            items.append({"name": line.title(), "price": ""})

    return {"categories": [{"name": "Menu", "items": items}]}
