---
title: Generación de PDF y Passbook
description: Guía de personalización de documentos legales y tarjetas digitales para los clientes de Yastubo.
---

Yastubo automatiza la creación de documentos contractuales y tarjetas de identificación digital (Wallet) para ofrecer una experiencia premium a sus asegurados. Esta guía explica el funcionamiento del motor de documentos y cómo personalizar sus plantillas.

## Core Benefits / Key Features
* **Plantillas Flexibles (Jinja2):** Personalización dinámica de contratos usando HTML y CSS moderno.
* **Conversión de Alta Fidelidad:** Generación de PDFs precisos mediante WeasyPrint.
* **Portabilidad:** Emisión de archivos `.pkpass` para Apple Wallet y Google Pay.
* **Almacenamiento Localizado:** Organización automática de pólizas por número de referencia.

## Deep Dive Técnico: Generación de Contratos

La lógica reside en `app/modules/emission/pdf_generator.py`.

### Renderizado de PDF (WeasyPrint)

El proceso de generación sigue estos pasos:
1. Se cargan los datos de la póliza y el cliente desde la base de datos.
2. Se procesa la plantilla HTML (`contract.html`) usando el motor Jinja2.
3. WeasyPrint convierte el HTML renderizado en un binario PDF.
4. El archivo se guarda en `storage/policies/` y se retorna para su descarga o envío por email.

```python
# app/modules/emission/pdf_generator.py

def generate_contract_pdf(policy: Policy, client: Client, plan_snapshot: dict) -> bytes:
    # 1. Cargar el entorno de Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("contract.html")

    # 2. Renderizar contenido con datos reales
    html_content = template.render(
        policy=policy, 
        client=client, 
        plan_snapshot=plan_snapshot, 
        now=datetime.now()
    )

    # 3. Convertir a PDF y guardar en el disco
    pdf_bytes = HTML(string=html_content).write_pdf()
    
    return pdf_bytes
```

## Ejemplo Práctico: Añadir un Nuevo Campo al Contrato

Si necesitas añadir la fecha de nacimiento del beneficiario en el contrato PDF:

### 1. Actualiza la Plantilla HTML
Modifica `app/modules/emission/templates/contract.html` añadiendo la variable Jinja2:

```html
<!-- app/modules/emission/templates/contract.html -->
<div class="row">
    <div class="label">Fecha de Nacimiento:</div>
    <div class="value">{{ client.birth_date }}</div>
</div>
```

### 2. Pasa los Datos en el Generador
Asegúrate de que el objeto `client` tenga el atributo disponible (ya incluido en la lógica base).

:::tip[Estilizado de PDF]
WeasyPrint soporta CSS3 moderno, incluyendo Flexbox y Grid. Puedes usar fuentes personalizadas y logotipos de alta resolución para el branding.
:::

## Generación de Passbook (Apple Wallet)

El servicio `PassbookService` en `app/modules/emission/passbook_service.py` es el encargado de orquestar la creación de la tarjeta digital.

```python
# Estructura del objeto pass_info para Apple Wallet
pass_info = {
    "formatVersion": 1,
    "passTypeIdentifier": "pass.com.yastubo",
    "serialNumber": "POL-12345",
    "teamIdentifier": "YASTUBO_ID",
    "organizationName": "Yastubo Insurance",
    "description": "Tu póliza activa",
    "storeCard": {
        "primaryFields": [
            {"key": "policy", "label": "PÓLIZA", "value": "POL-12345"}
        ]
    }
}
```

## Diagrama de Flujo de Documentos

![Document Generation Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774844570/ec004793-0b1f-4730-abbb-21411b1a7dbf.png)
