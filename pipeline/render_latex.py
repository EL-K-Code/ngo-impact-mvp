from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def render_latex(context: dict, template_dir: str = "templates", template_name: str = "ngo_impact_mvp_template.tex") -> str:
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        comment_start_string="((#",
        comment_end_string="#))",
    )
    template = env.get_template(template_name)
    return template.render(**context)

def save_latex(tex_content: str, output_path: str) -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tex_content, encoding="utf-8")
    return str(out.resolve())
