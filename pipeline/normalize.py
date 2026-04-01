import re
from pathlib import Path

from utils.helpers import (
    clean_lines,
    first_non_empty,
    load_json,
    normalize_key,
    parse_number_token,
    parse_percent_token,
)

SECTOR_LABELS = {
    "health_nutrition": "Health & Nutrition",
    "wash": "Water, Hygiene and Sanitation",
    "food_security_livelihoods": "Food Security & Livelihoods",
    "mhpss_protection": "Mental Health, Psychosocial Support and Protection",
    "drr": "Disaster Risk Reduction",
    "advocacy": "Advocacy",
}

COUNTRY_SHARE_ORDER = [
    "health_nutrition",
    "wash",
    "food_security_livelihoods",
    "mhpss_protection",
]

SECTOR_METRIC_PATTERNS = {
    "health_nutrition": {
        "health_facilities_supported": {
            "unit": "facilities",
            "patterns": [
                r"([\d\s,\.]+)\s+HEALTH FACILITIES RECEIVED SUPPORT",
                r"([\d\s,\.]+)\s+STRUCTURES SANITAIRES ONT RECU UN APPUI",
            ],
        },
        "children_u5_treated_for_sam": {
            "unit": "children",
            "patterns": [
                r"([\d\s,\.]+)\s+CHILDREN UNDER FIVE WERE TREATED FOR SAM",
                r"([\d\s,\.]+)\s+ENFANTS DE MOINS DE 5 ANS ONT ETE PRIS EN CHARGE POUR LA MAS",
            ],
        },
        "children_u5_primary_healthcare": {
            "unit": "children",
            "patterns": [
                r"([\d\s,\.]+)\s+CHILDREN UNDER FIVE BENEFITED FROM PRIMARY HEALTHCARE SERVICES",
                r"([\d\s,\.]+)\s+ENFANTS DE MOINS DE 5 ANS ONT BENEFICIE DE SOINS EN SANTE PRIMAIRE",
            ],
        },
        "children_u5_screened_for_sam": {
            "unit": "children",
            "patterns": [
                r"([\d\s,\.]+)\s+CHILDREN UNDER FIVE WERE SCREENED FOR SAM",
                r"([\d\s,\.]+)\s+ENFANTS DE MOINS DE 5 ANS ONT ETE DEPISTES POUR LA MAS",
            ],
        },
        "women_primary_healthcare": {
            "unit": "women",
            "patterns": [
                r"([\d\s,\.]+)\s+WOMEN BENEFITED FROM PRIMARY HEALTHCARE SERVICES",
                r"([\d\s,\.]+)\s+FEMMES ONT BENEFICIE DE SOINS EN SANTE PRIMAIRE",
            ],
        },
    },
    "food_security_livelihoods": {
        "people_supported_agropastoral": {
            "unit": "people",
            "patterns": [
                r"([\d\s,\.]+)\s+NUMBER OF PEOPLE ASSISTED THROUGH AGROPASTORAL SUPPORT",
                r"([\d\s,\.]+)\s+NOMBRE DE PERSONNES AIDEES GRACE AU SOUTIEN AGROPASTORAL",
            ],
        },
        "people_received_food_assistance_total": {
            "unit": "people",
            "patterns": [
                r"([\d\s,\.]+)\s+PEOPLE RECEIVED FOOD ASSISTANCE\b",
                r"([\d\s,\.]+)\s+PERSONNES ONT RECU UNE ASSISTANCE ALIMENTAIRE\b",
            ],
        },
        "people_received_food_assistance_in_kind": {
            "unit": "people",
            "patterns": [
                r"([\d\s,\.]+)\s+PEOPLE RECEIVED IN-KIND FOOD ASSISTANCE",
                r"([\d\s,\.]+)\s+PERSONNES ONT RECU UNE ASSISTANCE ALIMENTAIRE EN NATURE",
            ],
        },
        "people_received_food_assistance_vouchers": {
            "unit": "people",
            "patterns": [
                r"([\d\s,\.]+)\s+PEOPLE RECEIVED FOOD ASSISTANCE THROUGH VOUCHERS",
                r"([\d\s,\.]+)\s+PERSONNES ONT RECU UNE ASSISTANCE ALIMENTAIRE A TRAVERS DES COUPONS",
            ],
        },
        "people_received_food_assistance_cash_transfers": {
            "unit": "people",
            "patterns": [
                r"([\d\s,\.]+)\s+PEOPLE RECEIVED FOOD ASSISTANCE THROUGH CASH TRANSFERS",
                r"([\d\s,\.]+)\s+PERSONNES ONT RECU UNE ASSISTANCE ALIMENTAIRE A TRAVERS DES TRANSFERTS MONETAIRES",
            ],
        },
        "people_received_economic_assistance": {
            "unit": "people",
            "patterns": [
                r"([\d\s,\.]+)\s+PEOPLE RECEIVED ECONOMIC ASSISTANCE",
                r"([\d\s,\.]+)\s+PERSONNES ONT RECU UNE ASSISTANCE ECONOMIQUE",
            ],
        },
    },
    "wash": {
        "people_received_wash_cash_transfers": {
            "unit": "people",
            "patterns": [
                r"([\d\s,\.]+)\s+PEOPLE RECEIVED WASH ASSISTANCE THROUGH CASH TRANSFERS",
                r"([\d\s,\.]+)\s+PERSONNES ONT RECU UNE ASSISTANCE EHA A TRAVERS DES TRANSFERTS MONETAIRES",
            ],
        },
        "people_received_wash_vouchers": {
            "unit": "people",
            "patterns": [
                r"([\d\s,\.]+)\s+PEOPLE RECEIVED WASH ASSISTANCE THROUGH VOUCHERS",
                r"([\d\s,\.]+)\s+PERSONNES ONT RECU UNE ASSISTANCE EHA A TRAVERS DES COUPONS",
            ],
        },
        "pit_latrines_constructed_clts": {
            "unit": "latrines",
            "patterns": [
                r"([\d\s,\.]+)\s+PIT LATRINES WERE CONSTRUCTED USING THE CLTS APPROACH",
                r"([\d\s,\.]+)\s+LATRINES \(TROUS DE CHUTE\) ONT ETE CONSTRUITES AVEC L'APPROCHE CLTS",
            ],
        },
        "handwashing_facilities_constructed_or_rehabilitated": {
            "unit": "facilities",
            "patterns": [
                r"([\d\s,\.]+)\s+HANDWASHING FACILITIES WERE CONSTRUCTED OR REHABILITATED",
                r"([\d\s,\.]+)\s+STRUCTURES DE LAVAGE DE MAINS ONT ETE CONSTRUITES OU REHABILITEES",
            ],
        },
        "wash_kits_distributed": {
            "unit": "kits",
            "patterns": [
                r"([\d\s,\.]+)\s+WASH KITS WERE DISTRIBUTED",
                r"([\d\s,\.]+)\s+KITS EHA ONT ETE DISTRIBUES",
            ],
        },
        "people_received_wash_in_kind_assistance": {
            "unit": "people",
            "patterns": [
                r"([\d\s,\.]+)\s+PEOPLE RECEIVED IN-KIND WASH ASSISTANCE",
                r"([\d\s,\.]+)\s+PERSONNES ONT RECU UNE ASSISTANCE EHA EN NATURE",
            ],
        },
    },
    "mhpss_protection": {
        "people_received_tailored_psychological_support": {
            "unit": "people",
            "patterns": [
                r"([\d\s,\.]+)\s+PEOPLE RECEIVED TAILORED PSYCHOLOGICAL SUPPORT",
                r"([\d\s,\.]+)\s+PERSONNES ONT BENEFICIE D.?UN SOUTIEN PSYCHOLOGIQUE ADAPTE",
            ],
        },
        "people_received_psych_support_and_malnutrition_prevention": {
            "unit": "people",
            "patterns": [
                r"([\d\s,\.]+)\s+PEOPLE RECEIVED BOTH TAILORED PSYCHOLOGICAL SUPPORT",
                r"([\d\s,\.]+)\s+PERSONNES ONT BENEFICIE A LA FOIS D.?UN SOUTIEN PSYCHOLOGIQUE ADAPTE",
            ],
        },
        "mhpss_related_training_metric": {
            "unit": "reported_metric",
            "patterns": [
                r"([\d\s,\.]+)\s+ON MHPSS",
                r"([\d\s,\.]+)\s+SUR LA SMSP",
            ],
        },
        "gbv_trainings_count": {
            "unit": "trainings",
            "patterns": [
                r"([\d\s,\.]+)\s+ON GBV",
                r"([\d\s,\.]+)\s+SUR LA VBG",
            ],
        },
    },
}


def _page_text(doc: dict, page_number: int | None) -> str:
    if not page_number:
        return ""
    for page in doc["pages"]:
        if page["page_number"] == page_number:
            return page["text"]
    return ""


def _extract_year(text: str):
    match = re.search(r"\b(20\d{2})\b", text)
    return int(match.group(1)) if match else None


def _detect_language(text: str) -> str:
    norm = normalize_key(text[:4000])
    if "ACTION CONTRE LA FAIM" in norm or "PERSONNES ASSISTEES" in norm or "FOCUS PAYS" in norm:
        return "fr"
    return "en"


def _organization_name(text: str) -> str:
    norm = normalize_key(text[:3000])
    if "ACTION AGAINST HUNGER" in norm or "ACTION CONTRE LA FAIM" in norm:
        return "Action Against Hunger / Action contre la Faim"
    return "Unknown Organization"


def _canonical_title(text: str) -> str:
    norm = normalize_key(text[:3000])
    if "WEST AND CENTRAL AFRICA" in norm or "AFRIQUE DE L'OUEST ET DU CENTRE" in norm:
        return "Action Against Hunger in West and Central Africa - Key Figures and Interventions 2024"
    return "Standardized NGO Impact Report"


def _build_alias_groups(mapping: dict) -> dict:
    grouped = {}
    for raw_alias, canonical in mapping.items():
        grouped.setdefault(canonical, []).append(normalize_key(raw_alias))
    return grouped


def _extract_countries_list(page_text: str, country_mapping: dict) -> list[str]:
    grouped = _build_alias_groups(country_mapping)
    norm = normalize_key(page_text)
    found = []

    for canonical, aliases in grouped.items():
        positions = [norm.find(alias) for alias in aliases if norm.find(alias) >= 0]
        if positions:
            found.append((min(positions), canonical))

    found.sort(key=lambda x: x[0])
    return [country for _, country in found]


def _extract_countries_count(text: str):
    patterns = [
        r"(\d+)\s+COUNTRIES\s+OF\s+INTERVENTION",
        r"(\d+)\s+PAYS\s+D'INTERVENTION",
    ]
    norm = normalize_key(text)
    for pattern in patterns:
        match = re.search(pattern, norm)
        if match:
            return int(match.group(1))
    return None


def _extract_people_total(text: str):
    norm = normalize_key(text)
    patterns = [
        r"([\d\s,\.]+)\s+PEOPLE ASSISTED",
        r"([\d\s,\.]+)\s+PERSONNES ASSISTEES",
    ]
    candidates = []

    for pattern in patterns:
        for match in re.finditer(pattern, norm):
            value = parse_number_token(match.group(1))
            if value and value >= 100_000:
                candidates.append(value)

    return max(candidates) if candidates else None


def _extract_advocacy_count(text: str):
    norm = normalize_key(text)
    patterns = [
        r"(\d+)\s+ADVOCACY REPORTS",
        r"(\d+)\s+RAPPORTS DE PLAIDOYER",
    ]
    for pattern in patterns:
        match = re.search(pattern, norm)
        if match:
            return int(match.group(1))
    return None


def _extract_sector_distribution(page_text: str, sector_mapping: dict) -> list[dict]:
    lines = clean_lines(page_text)
    alias_lookup = {normalize_key(k): v for k, v in sector_mapping.items()}
    start_idx = None

    for i, line in enumerate(lines):
        if "PEOPLE ASSISTED BY SECTOR" in line or "PERSONNES ASSISTEES PAR SECTEUR" in line:
            start_idx = i
            break

    if start_idx is None:
        return []

    window = lines[start_idx + 1 : start_idx + 25]

    sectors = []
    seen = set()

    for line in window:
        if line in alias_lookup:
            canonical = alias_lookup[line]
            if canonical in SECTOR_LABELS and canonical not in seen:
                sectors.append(canonical)
                seen.add(canonical)

    counts = []
    pcts = []

    for line in window:
        if len(counts) < len(sectors) and re.fullmatch(r"[\d\s,\.]+", line):
            value = parse_number_token(line)
            if value is not None:
                counts.append(value)

        if len(pcts) < len(sectors) and re.fullmatch(r"[\d\s,\.]+\s*%", line):
            value = parse_percent_token(line)
            if value is not None:
                pcts.append(value)

    out = []
    for i, sector_id in enumerate(sectors):
        out.append(
            {
                "sector_id": sector_id,
                "sector_label_canonical": SECTOR_LABELS.get(sector_id, sector_id),
                "people_assisted": counts[i] if i < len(counts) else None,
                "reported_share_pct": pcts[i] if i < len(pcts) else None,
            }
        )
    return out


def _extract_narrative_summary(page_text: str) -> str:
    text = re.sub(r"\s+", " ", page_text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    filtered = [s.strip() for s in sentences if len(s.strip()) > 80]
    return " ".join(filtered[:2])


def _extract_metric_from_patterns(norm_text: str, patterns: list[str]):
    for pattern in patterns:
        match = re.search(pattern, norm_text, flags=re.IGNORECASE)
        if match:
            value = parse_number_token(match.group(1))
            if value is not None:
                return value
    return None


def _extract_sector_results(doc: dict, sector_distribution: list[dict]) -> list[dict]:
    sector_map = {item["sector_id"]: item for item in sector_distribution}
    sector_results = []

    for sector_id, page_number in doc["sections"]["sector_pages"].items():
        raw_text = _page_text(doc, page_number)
        norm_text = normalize_key(raw_text)
        metrics_spec = SECTOR_METRIC_PATTERNS.get(sector_id, {})

        sub_indicators = []
        for metric_id, spec in metrics_spec.items():
            value = _extract_metric_from_patterns(norm_text, spec["patterns"])
            if value is not None:
                sub_indicators.append(
                    {
                        "metric_id": metric_id,
                        "value": value,
                        "unit": spec["unit"],
                    }
                )

        sector_results.append(
            {
                "sector_id": sector_id,
                "sector_label_canonical": SECTOR_LABELS.get(sector_id, sector_id),
                "source_labels": {},
                "people_assisted": sector_map.get(sector_id, {}).get("people_assisted"),
                "reported_share_pct": sector_map.get(sector_id, {}).get("reported_share_pct"),
                "narrative_summary": _extract_narrative_summary(raw_text),
                "sub_indicators": sub_indicators,
                "source_page": page_number,
            }
        )

    return sector_results


def _extract_country_focus(doc: dict, country_mapping: dict) -> list[dict]:
    page_number = doc["sections"].get("country_focus")
    if not page_number:
        return []

    raw_text = _page_text(doc, page_number)
    norm = normalize_key(raw_text)
    grouped = _build_alias_groups(country_mapping)

    positions = []
    for canonical, aliases in grouped.items():
        found_positions = [norm.find(alias) for alias in aliases if norm.find(alias) >= 0]
        if found_positions:
            positions.append((min(found_positions), canonical))

    positions.sort(key=lambda x: x[0])

    entries = []
    for i, (start_pos, country) in enumerate(positions):
        end_pos = positions[i + 1][0] if i + 1 < len(positions) else len(norm)
        block = norm[start_pos:end_pos]

        number_candidates = re.findall(r"\d[\d\s,\.]*", block)
        people_assisted = None
        for token in number_candidates:
            value = parse_number_token(token)
            if value and value >= 1000:
                people_assisted = value
                break

        percentages = [
            parse_percent_token(m.group(0))
            for m in re.finditer(r"\d+(?:[.,]\d+)?\s*%", block)
        ]
        percentages = [p for p in percentages if p is not None][:4]

        sector_shares_pct = {}
        for idx, pct in enumerate(percentages):
            if idx < len(COUNTRY_SHARE_ORDER):
                sector_shares_pct[COUNTRY_SHARE_ORDER[idx]] = pct

        entries.append(
            {
                "country_name_canonical": country,
                "people_assisted": people_assisted,
                "sector_shares_pct": sector_shares_pct,
                "country_focus_mapping_assumption": True,
                "source_page": page_number,
            }
        )

    return entries


def build_standard_payload(doc: dict, data_dir: str = "data") -> dict:
    sector_mapping = load_json(str(Path(data_dir) / "sector_mapping.json"))
    country_mapping = load_json(str(Path(data_dir) / "country_mapping.json"))

    cover_text = _page_text(doc, doc["sections"].get("cover"))
    in_brief_text = _page_text(doc, doc["sections"].get("in_brief"))
    full_text = doc["full_text"]

    language = _detect_language(full_text)
    year = first_non_empty(_extract_year(cover_text), _extract_year(full_text))
    countries_list = _extract_countries_list(in_brief_text, country_mapping)
    countries_count = first_non_empty(_extract_countries_count(in_brief_text), len(countries_list))
    sector_distribution = _extract_sector_distribution(in_brief_text, sector_mapping)
    sector_results = _extract_sector_results(doc, sector_distribution)
    country_focus = _extract_country_focus(doc, country_mapping)

    people_total = _extract_people_total(full_text)
    advocacy_count = _extract_advocacy_count(full_text)
    sector_sum = sum(item["people_assisted"] or 0 for item in sector_distribution)

    payload = {
        "report_identity": {
            "report_family_id": f"standard_report_{year or 'unknown'}",
            "canonical_report_id": f"standard_report_{year or 'unknown'}",
            "organization_name": _organization_name(cover_text),
            "report_title_canonical": _canonical_title(cover_text),
            "report_year": year,
            "region_name": "West and Central Africa",
            "document_type": "impact_report",
            "reporting_scope": "regional",
        },
        "source_documents": [
            {
                "source_document_id": Path(doc["file_name"]).stem,
                "language": language,
                "file_name": doc["file_name"],
                "page_count": doc["page_count"],
                "source_title": _canonical_title(cover_text),
            }
        ],
        "coverage": {
            "countries_of_intervention_count": countries_count,
            "countries_of_intervention": countries_list,
        },
        "global_kpis": {
            "people_assisted_total": people_total,
            "advocacy_reports_count": advocacy_count,
            "sector_distribution": sector_distribution,
        },
        "sector_results": sector_results,
        "country_focus": country_focus,
        "quality_flags": {
            "sector_totals_overlap_flag": bool(people_total and sector_sum and sector_sum > people_total),
            "rounded_percentages_present": True,
            "visual_only_elements_present": True,
            "country_focus_mapping_assumption": True,
        },
        "provenance": [
            {
                "field_path": "global_kpis.people_assisted_total",
                "source_document_language": language,
                "source_pages": [doc["sections"].get("in_brief"), doc["sections"].get("results_overview")],
                "source_label": "PEOPLE ASSISTED / PERSONNES ASSISTEES",
                "extraction_mode": "rule_based",
                "confidence": 0.95,
            },
            {
                "field_path": "global_kpis.advocacy_reports_count",
                "source_document_language": language,
                "source_pages": [doc["sections"].get("in_brief")],
                "source_label": "ADVOCACY REPORTS / RAPPORTS DE PLAIDOYER",
                "extraction_mode": "rule_based",
                "confidence": 0.95,
            },
        ],
    }

    return payload
