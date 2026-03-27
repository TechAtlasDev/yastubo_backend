import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from app.modules.emission.models import Policy, Client

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
STORAGE_DIR = "storage/policies"


def generate_contract_pdf(policy: Policy, client: Client, plan_snapshot: dict) -> bytes:
    """
    Renders the contract HTML and converts it to PDF using WeasyPrint.
    """
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("contract.html")

    html_content = template.render(
        policy=policy, client=client, plan_snapshot=plan_snapshot, now=datetime.now()
    )

    # Ensure storage directory exists
    os.makedirs(STORAGE_DIR, exist_ok=True)

    # Generate PDF
    pdf_bytes = HTML(string=html_content).write_pdf()

    # Save to file
    file_path = os.path.join(STORAGE_DIR, f"{policy.policy_number}.pdf")
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    return pdf_bytes
