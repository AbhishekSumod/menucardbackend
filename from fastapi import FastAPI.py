from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

class MenuText(BaseModel):
    text: str

# Category keywords
CATEGORY_KEYWORDS = [
    "veg", "non veg", "drinks", "beverages", "mocktails", "juices", "shakes",
    "starters", "appetizers", "tandoor", "main course", "curries", "biryani",
    "rice", "noodles", "bread", "sandwich", "burgers", "pizza", "pasta",
    "seafood", "salads", "soups", "desserts", "breakfast", "thali", "combo"
]

def is_header(line: str) -> bool:
    """Check if line is a category header."""
    clean = line.strip().lower()
    if not clean: 
        return False
    if any(word in clean for word in CATEGORY_KEYWORDS):
        return True
    # if text is in CAPS → likely header
    if clean.isupper() and len(clean.split()) < 5:
        return True
    return False

def extract_price(line: str):
    """Extract price if present."""
    match = re.search(r"(₹|\$|rs\.?|inr|usd|eur|aed|gbp|£|€)?\s*([0-9]+(?:\.[0-9]{1,2})?)", line, re.IGNORECASE)
    if match:
        return match.group(0)
    return None

def extract_quantity(line: str):
    """Extract quantity if present."""
    match = re.search(r"\b(\d+\s?(pcs?|pieces?|plate|half|full|small|large))\b", line, re.IGNORECASE)
    if match:
        return match.group(0)
    return None

@app.post("/parse_menu")
def parse_menu(data: MenuText):
    text = data.text
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    categories = []
    current_category = {"name": "Uncategorized", "items": []}

    for line in lines:
        if is_header(line):
            if current_category["items"]:
                categories.append(current_category)
            current_category = {"name": line.title(), "items": []}
        else:
            price = extract_price(line)
            quantity = extract_quantity(line)
            name = line
            if price:
                name = name.replace(price, "").strip()
            if quantity:
                name = name.replace(quantity, "").strip()
            current_category["items"].append({
                "name": name.title(),
                "price": price,
                "quantity": quantity
            })

    if current_category["items"]:
        categories.append(current_category)

    return {"categories": categories}
