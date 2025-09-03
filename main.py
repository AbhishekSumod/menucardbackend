from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import re

app = FastAPI()

# ✅ Model for a single OCR line (only text, no x,y,width,height)
class OCRLine(BaseModel):
    text: str

# ✅ Request model
class OCRRequest(BaseModel):
    lines: List[OCRLine]

def extract_price(line: str) -> Optional[str]:
    """Extract price if present in line"""
    match = re.search(r"(₹|\$|rs\.?|inr|usd|eur|aed|gbp|£|€)?\s*([0-9]+(?:\.[0-9]{1,2})?)", line, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return None

@app.post("/parse_menu")
def parse_menu(data: OCRRequest):
    items = []
    buffer = ""

    for line in data.lines:
        text = line.text.strip()
        if not text:
            continue

        price = extract_price(text)

        if price:
            # ✅ Case: Price found → flush buffer as food name + price
            name = (buffer + " " + text).replace(price, "").strip()
            items.append({"name": name, "price": price})
            buffer = ""  # reset after pairing
        else:
            # ✅ Case: likely food name → keep buffering
            buffer += " " + text

    # In case leftover food name without price
    if buffer.strip():
        items.append({"name": buffer.strip(), "price": None})

    return {"menu": items}
