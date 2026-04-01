import json
import re
import unicodedata
from pathlib import Path


def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def strip_accents(text: str) -> str:
    text = text or ""
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(ch)
    )


def normalize_key(text: str) -> str:
    text = strip_accents(text or "")
    text = text.replace("’", "'").replace("`", "'").replace("–", "-").replace("—", "-")
    text = text.upper()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_lines(text: str) -> list[str]:
    lines = []
    for line in (text or "").splitlines():
        cleaned = normalize_key(line)
        if cleaned:
            lines.append(cleaned)
    return lines


def parse_number_token(token: str):
    if token is None:
        return None

    t = normalize_key(str(token))
    t = t.replace(" ", "")

    if re.fullmatch(r"\d+(?:[.,]\d+)?M", t):
        return int(round(float(t[:-1].replace(",", ".")) * 1_000_000))

    if re.fullmatch(r"\d+(?:[.,]\d+)?K", t):
        return int(round(float(t[:-1].replace(",", ".")) * 1_000))

    digits = re.sub(r"[^0-9]", "", t)
    if not digits:
        return None
    return int(digits)


def parse_percent_token(token: str):
    if token is None:
        return None

    t = normalize_key(str(token))
    t = t.replace("%", "").replace(" ", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def first_non_empty(*values):
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None
