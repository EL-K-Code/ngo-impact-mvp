import subprocess
from pathlib import Path


def compile_tex_to_pdf(tex_path: str, output_dir: str = "outputs") -> dict:
    tex_file = Path(tex_path).resolve()
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    stdout_path = out_dir / f"{tex_file.stem}_pdflatex_stdout.txt"
    stderr_path = out_dir / f"{tex_file.stem}_pdflatex_stderr.txt"
    log_path = out_dir / f"{tex_file.stem}.log"
    pdf_path = out_dir / f"{tex_file.stem}.pdf"

    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={out_dir}",
        str(tex_file),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        stdout_path.write_text(result.stdout or "", encoding="utf-8")
        stderr_path.write_text(result.stderr or "", encoding="utf-8")

        ok = pdf_path.exists()

        message = (result.stdout or "") + "\n\n" + (result.stderr or "")
        message = message.strip()

        return {
            "ok": ok,
            "pdf_path": str(pdf_path.resolve()) if ok else None,
            "log_path": str(log_path.resolve()) if log_path.exists() else None,
            "stdout_path": str(stdout_path.resolve()),
            "stderr_path": str(stderr_path.resolve()),
            "message": message,
        }

    except Exception as e:
        return {
            "ok": False,
            "pdf_path": None,
            "log_path": str(log_path.resolve()) if log_path.exists() else None,
            "stdout_path": str(stdout_path.resolve()) if stdout_path.exists() else None,
            "stderr_path": str(stderr_path.resolve()) if stderr_path.exists() else None,
            "message": str(e),
        }
