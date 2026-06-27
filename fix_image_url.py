import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

json_path = os.path.join(BASE_DIR, "data", "seed_products.json")

with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

for product in data["products"]:
    slug = product["slug"]
    product["image_url"] = f"/images/{slug}.jpg"

with open(json_path, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print("Berhasil! Semua image_url sudah diganti ke folder static/images.")