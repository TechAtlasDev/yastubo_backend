import os


def scaffold_module(module_name: str) -> str:
    """Generates the boilerplate for a new Yastubo domain module."""
    if not module_name or not module_name.isidentifier():
        return f"Error: '{module_name}' is not a valid Python identifier."

    base_path = os.path.join(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ),
        "app",
        "modules",
        module_name,
    )

    if os.path.exists(base_path):
        return f"Error: Module '{module_name}' already exists."

    try:
        os.makedirs(base_path)

        # __init__.py
        with open(os.path.join(base_path, "__init__.py"), "w") as f:
            f.write("")

        # models.py
        with open(os.path.join(base_path, "models.py"), "w") as f:
            f.write(
                "import uuid\nfrom sqlalchemy import String, ForeignKey\nfrom sqlalchemy.orm import Mapped, mapped_column\nfrom app.shared.base_model import BaseModel, GUID\n\n# Define your SQLAlchemy models here\n"
            )

        # schemas.py
        with open(os.path.join(base_path, "schemas.py"), "w") as f:
            f.write(
                "from pydantic import BaseModel, ConfigDict\nimport uuid\n\n# Define your Pydantic schemas here\n"
            )

        # service.py
        with open(os.path.join(base_path, "service.py"), "w") as f:
            f.write(
                "from sqlalchemy.ext.asyncio import AsyncSession\nfrom app.modules.audit.decorator import audited\n\n# Define your business logic here\n"
            )

        # router.py
        with open(os.path.join(base_path, "router.py"), "w") as f:
            f.write(
                f'import uuid\nfrom fastapi import APIRouter, Depends\nfrom app.core.database import get_db\nfrom sqlalchemy.ext.asyncio import AsyncSession\nfrom app.modules.auth.dependencies import require_role\nfrom app.modules.auth.models import User\n\nrouter = APIRouter(prefix="/{module_name}", tags=["{module_name.capitalize()}"])\n\n# Define your endpoints here\n'
            )

        # state_machine.py (optional but good practice as per CONTRIBUTING)
        with open(os.path.join(base_path, "state_machine.py"), "w") as f:
            f.write(
                'from enum import Enum\n\nclass Status(str, Enum):\n    DRAFT = "DRAFT"\n    ACTIVE = "ACTIVE"\n\nVALID_TRANSITIONS = {\n    Status.DRAFT: [Status.ACTIVE],\n}\n\ndef transition(current: Status, target: Status) -> Status:\n    if target not in VALID_TRANSITIONS.get(current, []):\n        raise ValueError(f"Invalid transition: {current} -> {target}")\n    return target\n'
            )

        return f"Success: Module '{module_name}' scaffolded correctly at app/modules/{module_name}"
    except Exception as e:
        return f"Error: Failed to create module. {str(e)}"
