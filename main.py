from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Union
import re

app = FastAPI()

# ---------- Models ----------
class OCRLine(BaseModel):
    text: str
    x: Union[float, int]
    y: Union[float, int]
    width: Union[float, int]
    height: Union[float, int]

class OCRRequest(BaseModel):
    lines: List[OCRLine]

# ---------- Helpers ----------
CATEGORY_KEYWORDS = [
    "veg", "non veg", "drinks", "beverages", "mocktails", "juices", "shakes",
    "starters", "appetizers", "tandoor", "main course", "curries", "biryani",
    "rice", "noodles", "bread", "sandwich", "burgers", "pizza", "pasta",
    "seafood", "salads", "soups", "desserts", "breakfast", "thali", "combo"
]

def is_header(line: str) -> bool:
    clean = line.strip().lower()
    if not clean:
        return False
    if any(word in clean for word in CATEGORY_KEYWORDS):
        return True
    if clean.isupper() and len(clean.split()) < 5:
        return True
    return False

def extract_price(text: str):
    match = re.search(r"(₹|\$|rs\.?|inr|usd|eur|aed|gbp|£|€)?\s*([0-9]+(?:\.[0-9]{1,2})?)", text, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return None

# ---------- API ----------
@app.post("/parse_menu")
def parse_menu(data: OCRRequest):
    lines = sorted(data.lines, key=lambda l: (l.y, l.x))  # top-to-bottom, left-to-right
    categories = []
    current_category = {"name": "Uncategorized", "items": []}

    buffer_item = None

    for line in lines:
        text = line.text.strip()

        # Skip empty
        if not text:
            continue

        # Category headers
        if is_header(text):
            if current_category["items"]:
                categories.append(current_category)
            current_category = {"name": text.title(), "items": []}
            continue

        # Price
        price = extract_price(text)

        if price:
            # If previous line is a food name → attach price
            if buffer_item:
                buffer_item["price"] = price
                current_category["items"].append(buffer_item)
                buffer_item = None
            else:
                # Orphan price → skip
                continue
        else:
            # Food name candidate
            if buffer_item:  # push previous without price
                current_category["items"].append(buffer_item)
            buffer_item = {"name": text.title(), "price": None, "quantity": None}

    if buffer_item:
        current_category["items"].append(buffer_item)

    if current_category["items"]:
        categories.append(current_category)

    return {"categories": categories}
