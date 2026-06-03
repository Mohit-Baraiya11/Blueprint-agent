import os
import tempfile
from fpdf import FPDF
from state import ProjectBlueprintState


class BlueprintPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "Project Blueprint", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(50, 50, 200)
        self.ln(6)
        self.set_fill_color(240, 240, 255)
        self.set_x(self.l_margin)
        self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(3)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(self.l_margin)
        self.multi_cell(0, 6, str(text))
        self.ln(2)

    def bullet_list(self, items):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        for item in items:
            self.set_x(self.l_margin)
            self.multi_cell(0, 6, f"  - {str(item)}")
        self.ln(2)


def clean(text: str) -> str:
    return (str(text)
        .replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2022", "-")
        .replace("\u00e2", "")
        .replace("—", "-")
        .replace("–", "-")
    )


def generate_pdf(state: ProjectBlueprintState) -> bytes:
    pdf = BlueprintPDF()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # IDEA
    pdf.section_title("Idea")
    pdf.body_text(clean(state["clarified_idea"]))

    # VALIDATION
    pdf.section_title("Validation")
    v = state["validation_result"]
    pdf.body_text(clean(f"Valid: {v['is_valid']}"))
    pdf.body_text(clean(f"Problem Score: {v['problem_score']}/10"))
    pdf.body_text(clean(f"Reason: {v['reason']}"))

    # COMPETITORS
    pdf.section_title("Competitors")
    pdf.bullet_list([clean(c) for c in state["competitors"]])

    # UNIQUE ANGLE
    pdf.section_title("Unique Angle")
    pdf.body_text(clean(state["unique_angle"]))

    # ARCHITECTURE SVG
    svg_str = state["architecture"].get("svg_diagram", "")
    if svg_str:
        pdf.section_title("Architecture Diagram")
        try:
            import cairosvg

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                cairosvg.svg2png(bytestring=svg_str.encode(), write_to=tmp.name)
                tmp_path = tmp.name
            pdf.set_x(pdf.l_margin)
            pdf.image(tmp_path, x=pdf.l_margin, w=pdf.epw)
            os.unlink(tmp_path)
            pdf.ln(4)
        except Exception as e:
            pdf.body_text(f"[Diagram could not be rendered: {e}]")

    # COMPONENTS
    pdf.section_title("Components")
    pdf.bullet_list([clean(c) for c in state["architecture"]["components"]])

    # API ROUTES
    pdf.section_title("API Routes")
    pdf.bullet_list([clean(r) for r in state["architecture"]["api_routes"]])

    # TECH STACK
    pdf.section_title("Tech Stack")
    ts = state["tech_stack"]
    pdf.bullet_list([
        clean(f"Frontend: {ts['frontend']}"),
        clean(f"Backend:  {ts['backend']}"),
        clean(f"Database: {ts['database']}"),
        clean(f"Infra:    {ts['infra']}"),
    ])

    # EXECUTION PLAN
    pdf.section_title("Execution Plan")
    ep = state["execution_plan"]
    pdf.body_text(clean(f"MVP Scope: {ep['mvp_scope']}"))
    pdf.body_text(clean(f"Timeline: {ep['timeline_weeks']} weeks"))

    for i, phase in enumerate(ep["phases"]):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 7, f"  Week {phase.get('week', i + 1)}", new_x="LMARGIN", new_y="NEXT")
        pdf.bullet_list([clean(t) for t in phase.get("tasks", [])])

    # RISKS
    pdf.section_title("Risks")
    pdf.bullet_list([clean(r) for r in state["risks"]])

    # get bytes first, then write to file — avoids double output() bug
    pdf_bytes = bytes(pdf.output())

    os.makedirs("output", exist_ok=True)
    with open("output/blueprint.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("\nPDF saved to output/blueprint.pdf")

    return pdf_bytes


def blueprint_node(state: ProjectBlueprintState) -> dict:
    competitors = "\n".join([f"- {c}" for c in state["competitors"]])
    components  = "\n".join([f"- {c}" for c in state["architecture"]["components"]])
    api_routes  = "\n".join([f"- {r}" for r in state["architecture"]["api_routes"]])
    risks       = "\n".join([f"- {r}" for r in state["risks"]])
    phases      = "\n".join([
        f"### Week {p.get('week', i + 1)}\n" +
        "\n".join([f"- {t}" for t in p.get("tasks", [])])
        for i, p in enumerate(state["execution_plan"]["phases"])
    ])

    markdown = f"""# Project Blueprint

## Idea
{state["clarified_idea"]}

## Validation
- Valid: {state["validation_result"]["is_valid"]}
- Problem Score: {state["validation_result"]["problem_score"]}/10
- Reason: {state["validation_result"]["reason"]}

## Competitors
{competitors}

## Unique Angle
{state["unique_angle"]}

## Architecture
### Components
{components}

### API Routes
{api_routes}

## Tech Stack
- Frontend: {state["tech_stack"]["frontend"]}
- Backend:  {state["tech_stack"]["backend"]}
- Database: {state["tech_stack"]["database"]}
- Infra:    {state["tech_stack"]["infra"]}

## Execution Plan
- MVP Scope: {state["execution_plan"]["mvp_scope"]}
- Timeline:  {state["execution_plan"]["timeline_weeks"]} weeks

### Phases
{phases}

## Risks
{risks}
"""

    return {
        "blueprint_markdown": markdown,
        "blueprint_pdf_bytes": generate_pdf(state),
        "current_agent": "done",
    }
