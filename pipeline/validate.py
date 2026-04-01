def validate_payload(payload: dict) -> dict:
    warnings = []

    if not payload["global_kpis"].get("people_assisted_total"):
        warnings.append("Missing global people_assisted_total.")

    if not payload["coverage"].get("countries_of_intervention_count"):
        warnings.append("Missing countries_of_intervention_count.")

    if not payload["global_kpis"].get("sector_distribution"):
        warnings.append("Missing sector distribution.")

    if not payload.get("sector_results"):
        warnings.append("No sector pages extracted.")

    if not payload.get("country_focus"):
        warnings.append("No country focus extracted.")

    payload["validation"] = {
        "is_valid": len(warnings) == 0,
        "warnings": warnings,
    }
    return payload
