from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import re

app = FastAPI()

class OCRLine(BaseModel):
    text: str
    x: float
    y: float
    width: float
    height: float

class OCRRequest(BaseModel):
    lines: List[OCRLine]

@app.post("/parse_menu")
def parse_menu(data: OCRRequest):
    lines = sorted(data.lines, key=lambda l: l.y)  # sort top to bottom
    grouped = []
    current_y = None
    buffer = []

    # Group lines by vertical position (same row)
    for line in lines:
        if current_y is None or abs(line.y - current_y) < 20:
            buffer.append(line)
            current_y = line.y
        else:
            grouped.append(buffer)
            buffer = [line]
            current_y = line.y
    if buffer:
        grouped.append(buffer)

    items = []
    for group in grouped:
        left = []
        right = []
        for line in sorted(group, key=lambda l: l.x):
            if re.search(r"\d", line.text):  # contains a number = price
                right.append(line.text)
            else:
                left.append(line.text)
        name = " ".join(left).strip()
        price = " ".join(right).strip()
        if name:
            items.append({"name": name, "price": price})

    return {"categories": items}
