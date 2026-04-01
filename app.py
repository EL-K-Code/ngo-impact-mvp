import json
from pathlib import Path

import fitz
import pandas as pd
import streamlit as st

from pipeline.pipeline import run_pipeline


def pdf_page_to_png_bytes(pdf_bytes: bytes, page_number: int, zoom: float = 1.6) -> bytes:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_number)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_bytes = pix.tobytes("png")
    doc.close()
    return img_bytes


def render_pdf_preview(pdf_bytes: bytes) -> None:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = doc.page_count
    doc.close()

    c1, c2 = st.columns([1, 3])
    with c1:
        page_to_show = st.number_input(
            "Preview page",
            min_value=1,
            max_value=page_count,
            value=1,
            step=1
        )
    with c2:
        st.caption(f"{page_count} page(s) available")

    img_bytes = pdf_page_to_png_bytes(pdf_bytes, page_to_show - 1, zoom=1.7)
    st.image(img_bytes, caption=f"Page {page_to_show}", use_container_width=True)

    with st.expander("Show all pages"):
        for i in range(page_count):
            page_img = pdf_page_to_png_bytes(pdf_bytes, i, zoom=1.25)
            st.image(page_img, caption=f"Page {i+1}", use_container_width=True)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1220px;
        }

        .hero {
            background: linear-gradient(135deg, #1F5AA6 0%, #163E73 100%);
            padding: 1.4rem 1.4rem;
            border-radius: 18px;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 10px 24px rgba(31, 90, 166, 0.18);
        }

        .hero h1 {
            margin: 0 0 0.25rem 0;
            font-size: 2rem;
            line-height: 1.1;
        }

        .hero p {
            margin: 0;
            font-size: 1rem;
            color: rgba(255,255,255,0.92);
        }

        .mini-note {
            background: #F4F7FB;
            border: 1px solid #D9E2EC;
            border-radius: 14px;
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
            color: #334155;
        }

        .section-title {
            margin-top: 0.75rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
            font-size: 1.15rem;
            color: #163E73;
        }

        .artifact-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 0.9rem 1rem;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
            min-height: 118px;
        }

        .status-ok {
            color: #1F8A5B;
            font-weight: 700;
        }

        .status-warn {
            color: #B26A00;
            font-weight: 700;
        }

        .status-bad {
            color: #C0392B;
            font-weight: 700;
        }

        .quick-actions {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 1rem 1rem 0.8rem 1rem;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value) -> None:
    st.markdown(
        f"""
        <div class="artifact-card">
            <div style="font-size:0.9rem;color:#64748B;margin-bottom:0.35rem;">{label}</div>
            <div style="font-size:1.7rem;font-weight:800;color:#1F5AA6;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="NGO Impact MVP",
    page_icon="📄",
    layout="wide"
)

inject_css()

with st.sidebar:
    st.markdown("## NGO Impact MVP")
    st.caption("Standardize NGO impact reports into a premium PDF brief.")
    st.markdown("---")
    st.markdown("### Workflow")
    st.markdown("1. Upload source PDFs")
    st.markdown("2. Extract and normalize data")
    st.markdown("3. Generate LaTeX")
    st.markdown("4. Compile premium PDF")
    st.markdown("5. Preview and download")
    st.markdown("---")
    st.info("For the MVP, start with reports that have a similar structure.")

st.markdown(
    """
    <div class="hero">
        <h1>NGO Impact Report Standardizer</h1>
        <p>Upload PDF reports, extract KPIs, normalize content, and generate a premium standardized PDF.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mini-note">
    This MVP proves one clear idea: a set of NGO impact-report PDFs can be transformed into a clean,
    standardized, downloadable document with a professional structure.
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "Upload one or more PDF reports",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    upload_dir = Path("uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    st.markdown('<div class="section-title">Uploaded files</div>', unsafe_allow_html=True)

    for file in uploaded_files:
        out_path = upload_dir / file.name
        with open(out_path, "wb") as f:
            f.write(file.read())
        saved_paths.append(str(out_path))
        st.success(f"Saved: {file.name}")

    if st.button("Generate standardized report", type="primary"):
        with st.spinner("Processing PDFs and compiling LaTeX..."):
            payload = run_pipeline(saved_paths)

        st.success("Pipeline finished.")

        report_identity = payload.get("report_identity", {})
        global_kpis = payload.get("global_kpis", {})
        validation = payload.get("validation", {})
        artifacts = payload.get("artifacts", {})

        pdf_path = artifacts.get("pdf_path")
        latex_path = artifacts.get("latex_path")
        json_path = artifacts.get("normalized_json_path")
        pdf_ok = artifacts.get("pdf_compile_ok")

        pdf_bytes = None
        if pdf_path and Path(pdf_path).exists():
            pdf_bytes = Path(pdf_path).read_bytes()

        st.markdown('<div class="section-title">Key figures</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("People assisted", global_kpis.get("people_assisted_total") or "N/A")
        with c2:
            metric_card("Countries", payload.get("coverage", {}).get("countries_of_intervention_count") or "N/A")
        with c3:
            metric_card("Advocacy reports", global_kpis.get("advocacy_reports_count") or "N/A")

        st.markdown('<div class="section-title">Generation status</div>', unsafe_allow_html=True)
        g1, g2, g3 = st.columns([1.1, 1.1, 2.5])

        with g1:
            st.markdown(
                f"""
                <div class="artifact-card">
                    <div style="font-size:0.9rem;color:#64748B;">Payload valid</div>
                    <div style="font-size:1.2rem;margin-top:0.35rem;" class="{'status-ok' if validation.get('is_valid') else 'status-warn'}">
                        {validation.get('is_valid')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with g2:
            label_class = "status-ok" if pdf_ok else "status-bad"
            label_text = "OK" if pdf_ok else "Failed"
            st.markdown(
                f"""
                <div class="artifact-card">
                    <div style="font-size:0.9rem;color:#64748B;">PDF compilation</div>
                    <div style="font-size:1.2rem;margin-top:0.35rem;" class="{label_class}">
                        {label_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with g3:
            st.markdown(
                f"""
                <div class="artifact-card">
                    <div style="font-size:0.9rem;color:#64748B;">Report identity</div>
                    <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-top:0.35rem;">
                        {report_identity.get("report_title_canonical", "N/A")}
                    </div>
                    <div style="font-size:0.92rem;color:#475569;margin-top:0.3rem;">
                        {report_identity.get("organization_name", "N/A")} — {report_identity.get("report_year", "N/A")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-title">Quick actions</div>', unsafe_allow_html=True)

        a1, a2, a3 = st.columns(3)

        with a1:
            if pdf_bytes:
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name="standardized_report.pdf",
                    mime="application/pdf",
                    width="stretch"
                )
            else:
                st.button("Download PDF", disabled=True, width="stretch")

        with a2:
            if latex_path and Path(latex_path).exists():
                st.download_button(
                    label="Download LaTeX",
                    data=Path(latex_path).read_bytes(),
                    file_name="standardized_report.tex",
                    mime="text/plain",
                    width="stretch"
                )
            else:
                st.button("Download LaTeX", disabled=True, width="stretch")

        with a3:
            if json_path and Path(json_path).exists():
                st.download_button(
                    label="Download JSON",
                    data=Path(json_path).read_bytes(),
                    file_name="normalized_report.json",
                    mime="application/json",
                    width="stretch"
                )
            else:
                st.button("Download JSON", disabled=True, width="stretch")

        if pdf_bytes:
            st.markdown('<div class="section-title">Preview</div>', unsafe_allow_html=True)
            st.caption("Browser-safe preview rendered as images from the generated PDF.")
            render_pdf_preview(pdf_bytes)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Overview", "Sectors", "Countries", "Artifacts", "Debug JSON"]
        )

        with tab1:
            st.subheader("Validation")
            if validation.get("warnings"):
                for warning in validation["warnings"]:
                    st.warning(warning)
            else:
                st.success("No validation warnings.")

            st.subheader("Report identity")
            st.json(report_identity)

            sector_distribution = global_kpis.get("sector_distribution", [])
            if sector_distribution:
                st.subheader("Sector distribution")
                st.dataframe(pd.DataFrame(sector_distribution), width="stretch")

        with tab2:
            sector_rows = []
            for sector in payload.get("sector_results", []):
                if sector.get("sub_indicators"):
                    for metric in sector["sub_indicators"]:
                        sector_rows.append(
                            {
                                "sector_id": sector["sector_id"],
                                "metric_id": metric["metric_id"],
                                "value": metric["value"],
                                "unit": metric["unit"],
                                "source_page": sector.get("source_page"),
                            }
                        )
                else:
                    sector_rows.append(
                        {
                            "sector_id": sector.get("sector_id"),
                            "metric_id": None,
                            "value": None,
                            "unit": None,
                            "source_page": sector.get("source_page"),
                        }
                    )

            if sector_rows:
                st.subheader("Sector metrics")
                st.dataframe(pd.DataFrame(sector_rows), width="stretch")
            else:
                st.info("No sector metrics extracted.")

        with tab3:
            country_rows = []
            for item in payload.get("country_focus", []):
                row = {
                    "country": item.get("country_name_canonical"),
                    "people_assisted": item.get("people_assisted"),
                    "source_page": item.get("source_page"),
                }
                row.update(item.get("sector_shares_pct", {}))
                country_rows.append(row)

            if country_rows:
                st.subheader("Country focus")
                st.dataframe(pd.DataFrame(country_rows), width="stretch")
            else:
                st.info("No country focus extracted.")

        with tab4:
            st.subheader("Generated artifacts")
            st.write(artifacts)

            if not pdf_ok:
                st.error("PDF compilation failed.")
                if artifacts.get("pdf_compile_message"):
                    st.code(artifacts["pdf_compile_message"])

        with tab5:
            st.subheader("Normalized JSON")
            st.code(json.dumps(payload, ensure_ascii=False, indent=2), language="json")
