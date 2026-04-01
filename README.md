# NGO Impact Report Standardizer

A Streamlit-based MVP that ingests NGO impact-report PDFs, extracts structured information, normalizes the data into a standard schema, and generates a standardized PDF brief through a LaTeX pipeline.

## Overview

This project was built as a local MVP to test one core idea:

> multiple NGO PDF reports can be transformed into a clean, structured, reusable editorial output.

The application currently:
- uploads one or more PDF reports,
- extracts text and structured signals,
- normalizes the extracted content into a standard JSON payload,
- renders a LaTeX template,
- compiles a PDF brief,
- previews the result inside Streamlit,
- lets the user download the generated PDF, LaTeX, and normalized JSON.

## Main features

- PDF upload from the Streamlit interface
- Extraction and section detection from source PDFs
- Standardized internal JSON payload
- LaTeX rendering with Jinja2
- PDF generation through `pdflatex`
- In-app preview
- Download buttons for:
  - generated PDF
  - generated LaTeX
  - normalized JSON

## Tech stack

- **Frontend**: Streamlit
- **Backend / pipeline**: Python
- **PDF parsing**: PyMuPDF (`fitz`)
- **Templating**: Jinja2
- **Data handling**: pandas
- **PDF output**: LaTeX / pdfLaTeX

---

# Project structure

```text
ngo-impact-mvp/
├── app.py
├── pipeline/
│   ├── pipeline.py
│   ├── render_latex.py
│   ├── compile_pdf.py
│   ├── extract.py
│   ├── detect_sections.py
│   ├── normalize.py
│   └── validate.py
├── templates/
│   └── ngo_impact_mvp_template.tex
├── uploads/
├── outputs/
├── utils/
│   └── helpers.py
├── requirements.txt
└── README.md
````

---

# Local installation

## 1. Clone the repository

```bash
git clone https://github.com/EL-K-Code/ngo-impact-mvp
cd ngo-impact-mvp
```

## 2. Create and activate a virtual environment

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

# LaTeX / PDF requirements

This project needs a working **pdfLaTeX** installation because the final report is compiled from a `.tex` template.

## Option A — TeX Live on Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y \
  texlive-latex-base \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-fonts-extra \
  texlive-pictures \
  lmodern
```

## Option B — TinyTeX / tlmgr users

If you use TinyTeX, make sure your TeX repository matches your local TeX Live version.

For TeX Live 2024, for example:

```bash
tlmgr init-usertree
tlmgr option repository https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2024/tlnet-final
```

Then install the packages required by the template:

```bash
tlmgr install \
  lato \
  fontaxes \
  tikzfill \
  pdfcol \
  enumitem \
  lastpage \
  parskip
```

## Verify pdfLaTeX

```bash
pdflatex --version
```

---

# Run the app locally

Start the Streamlit application:

```bash
streamlit run app.py
```

By default, Streamlit will open a local URL such as:

```text
http://localhost:8501
```

---

# How to use the app

1. Open the Streamlit interface
2. Upload one or more NGO PDF reports
3. Click **Generate standardized report**
4. Wait for the pipeline to:

   * extract text,
   * normalize the payload,
   * render LaTeX,
   * compile the PDF
5. Review:

   * the generated PDF preview,
   * extracted metrics,
   * normalized JSON
6. Download:

   * PDF
   * LaTeX
   * JSON

---

# Generated artifacts

Each run creates files in the `outputs/` directory.

Typical outputs:

```text
outputs/
├── normalized_report.json
├── standardized_report.tex
├── standardized_report.pdf
├── standardized_report.log
├── standardized_report_pdflatex_stdout.txt
└── standardized_report_pdflatex_stderr.txt
```

These files are useful for:

* debugging LaTeX compilation errors,
* checking extracted values,
* validating the generated report.

---

# Notes about the current MVP

This repository is an MVP, not yet a finalized production tool.

At this stage:

* the extraction pipeline works,
* the JSON normalization works,
* the LaTeX rendering works,
* the PDF compilation works when the required TeX dependencies are installed,
* some parts of the editorial template may still require refinement or stronger backend binding depending on the current template version.

In other words:

* **technical proof of concept: yes**
* **fully polished production workflow: not yet**

---

# Troubleshooting

## 1. `pdflatex: command not found`

Install TeX Live or TinyTeX correctly and verify with:

```bash
pdflatex --version
```

## 2. `LaTeX Error: File 'xxx.sty' not found`

A LaTeX package is missing. Install it through TeX Live / TinyTeX.

Example:

```bash
tlmgr install pdfcol
```

or install broader TeX collections on Linux.

## 3. Streamlit runs but no PDF is generated

Check these files:

```text
outputs/standardized_report.log
outputs/standardized_report_pdflatex_stdout.txt
outputs/standardized_report_pdflatex_stderr.txt
```

## 4. Preview works poorly in browser

The app may render preview pages as images instead of raw embedded PDF, depending on browser behavior and sandbox restrictions.

## 5. Upload works but placeholders still appear in the PDF

That usually means the LaTeX template still contains static placeholders not yet fully connected to the normalized backend payload.

---

# Suggested development workflow

A good local workflow is:

```bash
streamlit run app.py
```

Then, if PDF compilation fails:

```bash
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs outputs/standardized_report.tex
```

This makes LaTeX errors easier to inspect.

---

# Deployment notes

This project is easiest to deploy with **Docker + Railway** because it depends on both:

* Python packages
* TeX / LaTeX system packages

A simpler deployment on Streamlit Community Cloud may work for lighter setups, but LaTeX-heavy environments are usually more reliable in Docker-based deployments.

---

# Roadmap

Planned improvements may include:

* stronger backend binding for all template placeholders,
* better country-focus formatting,
* cleaner sector narrative generation,
* improved PDF visual design,
* stronger validation and confidence reporting,
* containerized deployment.

---

# License

Add your preferred license here.

Example:

```text
MIT License
```


