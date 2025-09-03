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
            # Remove detected parts from name
            name = line
            if price:
                name = name.replace(price, "").strip()
            if quantity:
                name = name.replace(quantity, "").strip()
            current_category["items"].append({
                "name": name.title(),
                "price": price or "",
                "quantity": quantity or ""
            })
    if current_category["items"]:
        categories.append(current_category)
    return {"categories": categories}
