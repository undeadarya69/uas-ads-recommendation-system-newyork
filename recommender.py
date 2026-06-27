import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "model",
    "content_based_model_ads_versi7.joblib"
)

_model = None
_load_failed = False


def normalize_slug(text):
    return str(text).strip().lower().replace(" ", "_")


def _load():
    global _model, _load_failed

    if _model is not None or _load_failed:
        return _model

    try:
        import joblib

        _model = joblib.load(MODEL_PATH)

        _model["product_index"] = {
            normalize_slug(k): v
            for k, v in _model["product_index"].items()
        }

        _model["product_names"] = [
            normalize_slug(x)
            for x in _model["product_names"]
        ]

        if "subcategory_map" in _model:
            _model["subcategory_map"] = {
                normalize_slug(k): v
                for k, v in _model["subcategory_map"].items()
            }

        print("[recommender] Model berhasil dimuat.")
        print("[recommender] File model:", MODEL_PATH)
        print("[recommender] Jumlah produk:", len(_model["product_names"]))

    except Exception as e:
        print(f"[recommender] Model tidak dimuat: {e}")
        _load_failed = True
        _model = None

    return _model


def is_available():
    return _load() is not None


def get_category_from_subcategory(subcategory):
    food = [
        "fruit", "vegetable", "dairy",
        "protein", "grain", "beverage",
        "condiment", "snack"
    ]

    cleaning = [
        "cleaning_tools", "cleaning_solution",
        "cleaning_accessories", "paper_products",
        "waste_management", "home_freshener"
    ]

    personal = [
        "hair_care", "oral_care",
        "shaving", "body_care", "hygiene"
    ]

    household = [
        "electrical", "garden", "laundry_tools"
    ]

    if subcategory in food:
        return "food"

    if subcategory in cleaning:
        return "cleaning"

    if subcategory in personal:
        return "personal"

    if subcategory in household:
        return "household"

    return "other"


def get_subcategory(model, slug):
    slug = normalize_slug(slug)
    sub_map = model.get("subcategory_map", {})

    data = sub_map.get(slug, "other")

    if isinstance(data, dict):
        return (
            data.get("subcategory")
            or data.get("SubCategory")
            or data.get("subkategori")
            or "other"
        )

    if isinstance(data, (list, tuple)) and len(data) >= 2:
        return data[1]

    return data or "other"


def recommend(product_slug, n=10):
    model = _load()

    if model is None:
        return []

    product_slug = normalize_slug(product_slug)

    idx = model["product_index"].get(product_slug)

    if idx is None:
        print("[recommender] Produk tidak ditemukan di model:", product_slug)
        return []

    product_names = model["product_names"]
    similarity = model["similarity"]

    base_subcategory = get_subcategory(model, product_slug)
    base_category = get_category_from_subcategory(base_subcategory)

    sim_scores = list(enumerate(similarity[idx]))

    results = []

    for i, score in sim_scores:
        candidate_slug = normalize_slug(product_names[i])

        if candidate_slug == product_slug:
            continue

        if score <= 0:
            continue

        candidate_subcategory = get_subcategory(model, candidate_slug)
        candidate_category = get_category_from_subcategory(candidate_subcategory)

        if candidate_subcategory == base_subcategory:
            priority = 2
            final_score = float(score) + 0.03

        elif candidate_category == base_category:
            priority = 1
            final_score = float(score) + 0.015

        else:
            priority = 0
            final_score = float(score)

        results.append(
            {
                "slug": candidate_slug,
                "similarity": float(score),
                "final_score": final_score,
                "priority": priority,
                "category": candidate_category,
                "subcategory": candidate_subcategory
            }
        )

    results = sorted(
        results,
        key=lambda x: (x["priority"], x["final_score"]),
        reverse=True
    )

    recommendations = [
        item["slug"]
        for item in results[:n]
    ]

    print(f"[recommender] Rekomendasi untuk {product_slug}:")
    for item in results[:n]:
        print(
            item["slug"],
            "| subcategory:", item["subcategory"],
            "| category:", item["category"],
            "| similarity:", round(item["similarity"], 6),
            "| final:", round(item["final_score"], 6),
            "| priority:", item["priority"]
        )

    return recommendations


def recommend_for_many(product_slugs, n=10):
    if not product_slugs:
        return []

    product_slugs = [normalize_slug(s) for s in product_slugs]

    results = []
    seen = set(product_slugs)

    for slug in product_slugs:
        recs = recommend(slug, n=n)

        for rec in recs:
            rec = normalize_slug(rec)

            if rec not in seen:
                results.append(rec)
                seen.add(rec)

            if len(results) >= n:
                return results

    return results