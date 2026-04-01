import json
from pathlib import Path

from pipeline.detect_sections import detect_sections
from pipeline.extract import extract_document
from pipeline.normalize import build_standard_payload
from pipeline.validate import validate_payload
from pipeline.render_latex import render_latex, save_latex
from pipeline.compile_pdf import compile_tex_to_pdf
from utils.helpers import ensure_dir


def _payload_score(payload: dict) -> int:
    score = 0
    if payload["global_kpis"].get("people_assisted_total"):
        score += 5
    if payload["global_kpis"].get("advocacy_reports_count"):
        score += 2
    score += len(payload["global_kpis"].get("sector_distribution", []))
    score += len(payload.get("sector_results", []))
    score += len(payload.get("country_focus", []))
    return score


def _merge_payloads(payloads: list[dict]) -> dict:
    best = max(payloads, key=_payload_score)
    merged = dict(best)

    merged["source_documents"] = []
    for payload in payloads:
        merged["source_documents"].extend(payload.get("source_documents", []))

    merged["validation"] = {
        "is_valid": all(p.get("validation", {}).get("is_valid", False) for p in payloads),
        "warnings": [w for p in payloads for w in p.get("validation", {}).get("warnings", [])],
    }

    return merged


def run_pipeline(pdf_paths: list[str], outputs_dir: str = "outputs") -> dict:
    outputs_path = ensure_dir(outputs_dir)
    payloads = []

    for pdf_path in pdf_paths:
        doc = extract_document(pdf_path)
        doc["sections"] = detect_sections(doc["pages"])
        payload = build_standard_payload(doc)
        payload = validate_payload(payload)
        payloads.append(payload)

    merged = _merge_payloads(payloads) if len(payloads) > 1 else payloads[0]

    json_path = outputs_path / "normalized_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    tex_content = render_latex(merged)
    tex_path = outputs_path / "standardized_report.tex"
    tex_path = Path(save_latex(tex_content, str(tex_path)))

    compile_result = compile_tex_to_pdf(str(tex_path), output_dir=str(outputs_path))

    merged["artifacts"] = {
        "normalized_json_path": str(json_path.resolve()),
        "latex_path": str(tex_path.resolve()),
        "pdf_path": compile_result.get("pdf_path"),
        "pdf_compile_ok": compile_result.get("ok"),
        "pdf_compile_message": compile_result.get("message"),
        "latex_log_path": compile_result.get("log_path"),
        "latex_stdout_path": compile_result.get("stdout_path"),
        "latex_stderr_path": compile_result.get("stderr_path"),
    }

    return merged
