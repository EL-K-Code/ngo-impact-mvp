from utils.helpers import normalize_key


def detect_sections(pages: list[dict]) -> dict:
    sections = {
        "cover": None,
        "in_brief": None,
        "results_overview": None,
        "sector_pages": {},
        "country_focus": None,
    }

    for page in pages:
        page_num = page["page_number"]
        text = normalize_key(page["text"])

        if page_num == 1:
            sections["cover"] = page_num

        if "2024 EN BREF" in text or "2024 IN BRIEF" in text:
            sections["in_brief"] = page_num

        if "NOTRE BILAN" in text or "OUR RESULTS" in text:
            sections["results_overview"] = page_num

        if "FOCUS PAYS" in text or "COUNTRY FOCUS" in text:
            sections["country_focus"] = page_num

        if "SANTE & NUTRITION" in text or "HEALTH & NUTRITION" in text:
            sections["sector_pages"]["health_nutrition"] = page_num

        if "SECURITE ALIMENTAIRE" in text or "FOOD SECURITY & LIVELIHOODS" in text:
            sections["sector_pages"]["food_security_livelihoods"] = page_num

        if "EAU, HYGIENE" in text or "WATER, HYGIENE" in text:
            sections["sector_pages"]["wash"] = page_num

        if "SANTE MENTALE" in text or "MENTAL HEALTH" in text:
            sections["sector_pages"]["mhpss_protection"] = page_num

    return sections
