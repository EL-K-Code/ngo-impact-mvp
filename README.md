<div align="center">

# NGO Impact Report Standardizer

### Document intelligence pipeline for structured extraction and standardized reporting

This project transforms heterogeneous NGO impact-report PDFs into a normalized JSON representation and a standardized PDF brief generated through a LaTeX pipeline.

![Python](https://img.shields.io/badge/Python-Document%20Pipeline-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive%20MVP-FF4B4B?logo=streamlit&logoColor=white)
![LaTeX](https://img.shields.io/badge/LaTeX-Automated%20Reporting-008080?logo=latex&logoColor=white)
![Status](https://img.shields.io/badge/Status-Working%20Local%20MVP-2E8B57)

</div>

---

## Problem

Impact reports are often valuable but difficult to compare or reuse because each organization chooses its own structure, vocabulary, indicators and visual format.

This MVP explores a reusable workflow for converting those reports into:

- extracted text and sections;
- a standardized internal schema;
- structured JSON data;
- a consistent editorial brief;
- downloadable PDF and LaTeX artifacts.

The goal is not to replace human program evaluation. It is to reduce repetitive document-processing work and make extracted information easier to review.

---

## Current workflow

```mermaid
flowchart LR
    A[NGO PDF reports] --> B[Text extraction]
    B --> C[Section detection]
    C --> D[Normalization]
    D --> E[Schema validation]
    E --> F[LaTeX rendering]
    F --> G[PDF compilation]
    G --> H[Preview and downloads]
```

A user can upload one or more reports through Streamlit, run the pipeline and inspect:

- the generated standardized PDF;
- the normalized JSON payload;
- extracted indicators;
- the generated LaTeX source;
- compilation logs when errors occur.

---

## Implemented capabilities

- upload of one or more PDF reports;
- text extraction with PyMuPDF;
- section-detection logic;
- normalization into a shared JSON payload;
- validation before rendering;
- Jinja2-based LaTeX templating;
- PDF compilation through `pdflatex`;
- in-application preview;
- downloads for PDF, LaTeX and JSON outputs;
- generation of logs for compilation troubleshooting.

---

## Technology stack

| Layer | Technology |
| --- | --- |
| Interface | Streamlit |
| Pipeline | Python |
| PDF extraction | PyMuPDF / `fitz` |
| Data handling | pandas |
| Templating | Jinja2 |
| Report rendering | LaTeX / pdfLaTeX |
| Structured payload | JSON |

---

## Repository structure

```text
ngo-impact-mvp/
├── app.py
├── pipeline/
│   ├── pipeline.py
│   ├── extract.py
│   ├── detect_sections.py
│   ├── normalize.py
│   ├── validate.py
│   ├── render_latex.py
│   └── compile_pdf.py
├── templates/
│   └── ngo_impact_mvp_template.tex
├── uploads/              # local input files
├── outputs/              # generated artifacts
├── utils/
│   └── helpers.py
├── requirements.txt
└── README.md
```

---

## Local setup

### 1. Clone the repository

```bash
git clone https://github.com/EL-K-Code/ngo-impact-mvp.git
cd ngo-impact-mvp
```

### 2. Create a virtual environment

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install LaTeX

A working `pdflatex` installation is required.

Ubuntu or Debian:

```bash
sudo apt update
sudo apt install -y \
  texlive-latex-base \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-pictures \
  lmodern
```

Verify the installation:

```bash
pdflatex --version
```

### 5. Run the application

```bash
streamlit run app.py
```

The local interface is typically available at:

```text
http://localhost:8501
```

---

## Generated artifacts

A successful run can create:

```text
outputs/
├── normalized_report.json
├── standardized_report.tex
├── standardized_report.pdf
├── standardized_report.log
├── standardized_report_pdflatex_stdout.txt
└── standardized_report_pdflatex_stderr.txt
```

These artifacts support both user review and technical debugging.

---

## Design principles

### Structured before generative

The pipeline creates a normalized intermediate representation before generating the final report. This makes it easier to validate extracted information and reuse it in other outputs.

### Reviewable outputs

JSON, LaTeX and PDF are all exposed so that extracted values and editorial rendering can be inspected independently.

### Honest uncertainty

The current MVP does not assume that every PDF follows the same structure. Missing fields, section-detection errors and weak extraction should be visible rather than silently fabricated.

### Local-first processing

The current implementation is designed to run locally, which is useful when documents may contain sensitive organizational information.

---

## Current boundaries

This is a technical proof of concept, not yet a production document-intelligence platform.

Current limitations include:

- extraction depends mainly on embedded PDF text;
- scanned documents may require OCR;
- section detection is heuristic;
- some template placeholders may not yet be connected to every normalized field;
- no page-level citation system;
- no confidence score for extracted values;
- no human validation workflow for individual fields;
- no automated test suite or CI workflow;
- no containerized production deployment;
- no authentication, authorization or secure document-retention policy.

---

## Troubleshooting

### `pdflatex: command not found`

Install a LaTeX distribution and verify:

```bash
pdflatex --version
```

### Missing LaTeX package

Install the package reported in the compilation log or install a broader TeX collection.

### No generated PDF

Inspect:

```text
outputs/standardized_report.log
outputs/standardized_report_pdflatex_stdout.txt
outputs/standardized_report_pdflatex_stderr.txt
```

### Static placeholders remain in the output

This indicates that the template and normalized payload are not fully bound for those fields. The JSON output should be reviewed before changing the template or rendering code.

---

## Recommended next milestones

1. add OCR and layout-aware extraction for scanned reports;
2. define a versioned schema with field descriptions and validation rules;
3. attach source-page references to extracted claims;
4. expose confidence and extraction status for each field;
5. add a human review screen before report generation;
6. create a benchmark set of heterogeneous reports;
7. measure field-level precision, recall and missing-value behaviour;
8. add unit, integration and snapshot tests;
9. containerize Python and LaTeX dependencies;
10. add secure temporary-file handling and retention controls;
11. support additional output templates and languages.

---

## Evaluation plan

A serious document-intelligence evaluation should report:

- field-level exact match and relaxed match;
- precision and recall for detected sections;
- missing-field detection;
- unsupported-value rate;
- page-citation accuracy;
- robustness across native and scanned PDFs;
- PDF compilation success rate;
- human correction time compared with manual report creation.

---

## What this project demonstrates

- document-processing pipeline design;
- extraction-to-schema normalization;
- validation before generation;
- automated LaTeX report production;
- local interactive application development;
- understanding of reliability requirements for document AI.

---

## Author

**Alex Komla LABOU**  
Applied AI and Machine Learning Engineer — Research-Oriented

- GitHub: [EL-K-Code](https://github.com/EL-K-Code)
- LinkedIn: [komla-alex-labou](https://www.linkedin.com/in/komla-alex-labou/)
