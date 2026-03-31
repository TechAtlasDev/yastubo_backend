import uuid
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.modules.emission.models import Policy
from app.modules.plans.models import PlanVersionCoverage


class PDFService:
    @staticmethod
    async def generate_policy_certificate(
        db: AsyncSession, policy_id: uuid.UUID
    ) -> bytes:
        # Load policy with relationships
        result = await db.execute(
            select(Policy)
            .where(Policy.id == policy_id)
            .options(
                selectinload(Policy.client),
                selectinload(Policy.beneficiaries),
                selectinload(Policy.plan_version),
                selectinload(Policy.plan),
            )
        )
        policy = result.scalar_one_or_none()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")

        # Load coverages
        result_cov = await db.execute(
            select(PlanVersionCoverage)
            .where(PlanVersionCoverage.plan_version_id == policy.plan_version_id)
            .options(selectinload(PlanVersionCoverage.coverage))
        )
        coverages = result_cov.scalars().all()

        # HTML Template (Inline for simplicity in this demo, usually in a separate file)
        template_str = """
        <html>
        <head>
            <style>
                body { font-family: 'Helvetica', sans-serif; color: #333; line-height: 1.6; }
                .header { text-align: center; border-bottom: 2px solid #004a99; padding-bottom: 20px; margin-bottom: 30px; }
                .section { margin-bottom: 20px; }
                .section-title { font-weight: bold; color: #004a99; border-bottom: 1px solid #ddd; margin-bottom: 10px; }
                .grid { display: flex; flex-wrap: wrap; }
                .col { width: 50%; margin-bottom: 10px; }
                .label { font-weight: bold; font-size: 0.9em; color: #666; }
                .value { font-size: 1em; }
                table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .footer { margin-top: 50px; text-align: center; font-size: 0.8em; color: #999; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Certificado de Póliza</h1>
                <p>Yastubo - Tu tranquilidad, nuestra prioridad</p>
            </div>

            <div class="section">
                <div class="section-title">Información de la Póliza</div>
                <div class="grid">
                    <div class="col"><span class="label">Número de Póliza:</span> <span class="value">{{ policy.policy_number }}</span></div>
                    <div class="col"><span class="label">Estado:</span> <span class="value">{{ policy.status }}</span></div>
                    <div class="col"><span class="label">Fecha de Emisión:</span> <span class="value">{{ policy.issued_at.strftime('%Y-%m-%d') if policy.issued_at else 'N/A' }}</span></div>
                    <div class="col"><span class="label">Vigencia:</span> <span class="value">{{ policy.start_date }} hasta {{ policy.end_date }}</span></div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Datos del Asegurado Principal</div>
                <div class="grid">
                    <div class="col"><span class="label">Nombre:</span> <span class="value">{{ policy.client.first_name }} {{ policy.client.last_name }}</span></div>
                    <div class="col"><span class="label">Documento:</span> <span class="value">{{ policy.client.document_type }} {{ policy.client.document_number }}</span></div>
                    <div class="col"><span class="label">Email:</span> <span class="value">{{ policy.client.email }}</span></div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Plan Contratado</div>
                <div class="grid">
                    <div class="col"><span class="label">Producto:</span> <span class="value">{{ policy.plan.name }}</span></div>
                    <div class="col"><span class="label">Prima Total:</span> <span class="value">{{ policy.final_price }} {{ policy.currency }}</span></div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Coberturas Principales</div>
                <table>
                    <thead>
                        <tr>
                            <th>Cobertura</th>
                            <th>Descripción</th>
                            <th>Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for cov in coverages %}
                        <tr>
                            <td>{{ cov.coverage.name }}</td>
                            <td>{{ cov.coverage.description or '' }}</td>
                            <td>
                                {% if cov.value_text %}
                                    {{ cov.value_text }}
                                {% elif cov.value_decimal %}
                                    {{ cov.value_decimal }}
                                {% elif cov.value_int %}
                                    {{ cov.value_int }}
                                {% else %}
                                    Incluido
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <div class="footer">
                <p>Este documento es un certificado válido de cobertura emitido por Yastubo.</p>
                <p>Generado el {{ now.strftime('%Y-%m-%d %H:%M:%S') }}</p>
            </div>
        </body>
        </html>
        """

        env = Environment(loader=FileSystemLoader("."))
        template = env.from_string(template_str)
        html_content = template.render(
            policy=policy, coverages=coverages, now=datetime.now()
        )

        # Generate PDF
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
