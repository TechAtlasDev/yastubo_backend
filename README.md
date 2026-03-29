# 🌟 Yastubo Backend v1

> **El motor inteligente diseñado para transformar los seguros funerarios de migrantes.** 🌍✈️

<p align="center">
  <img src="docs/src/assets/logo_yastubo.png" alt="Yastubo Logo" width="350px" />
</p>

<p align="center">
  <a href="http://localhost:4321/get-started/installation/"><img src="https://img.shields.io/badge/Gu%C3%ADa-Instalaci%C3%B3n-8350F9?style=for-the-badge" /></a>
  <a href="http://localhost:4321"><img src="https://img.shields.io/badge/Docs-Oficiales-black?style=for-the-badge" /></a>
</p>

---

## ✨ ¿Por qué Yastubo?

Yastubo no es solo una API; es una **infraestructura modular de alta fidelidad** diseñada para orquestar cada aspecto de la protección familiar funeraria. 

### 🚀 Capacidades Core
*   **🏦 Stripe Connect Native:** Gestión de carteras, suscripciones y pagos recurrentes sin fricciones.
*   **📜 State Machine Mastery:** Una máquina de estados determinística que controla cada fase de la póliza (Draft → Active → Cancelled).
*   **🤖 AI Integration:** Agentes inteligentes que automatizan el análisis de riesgo y el soporte operativo.
*   **🔍 Auditoría Total:** Trazabilidad absoluta mediante nuestro motor `@audited` (sabemos quién, qué y cuándo cambió cada dato).
*   **⚙️ Modular por Diseño:** Dominios desacoplados que permiten escalar y evolucionar el producto sin generar deuda técnica.

---

## 🛠️ Yastubo Dev Machine (CLI)

Olvídate de memorizar comandos complejos. Hemos construido una **Terminal User Interface (TUI)** interactiva para que gestiones todo el ecosistema desde un solo lugar.

```bash
make cli
```

> **¿Qué puedes hacer?**
> - 📊 **Dashboard:** Monitorear la salud del sistema y configuración en tiempo real.
> - 🏗️ **Scaffolder:** Crear nuevos módulos siguiendo los estándares de arquitectura.
> - 🧪 **Testing:** Runner visual para ejecutar pruebas por módulos o archivos.
> - 📖 **Docs:** Lanzar el servidor de documentación local de forma instantánea.

---

## ⚡ Get Started

### 1. El camino rápido (Recomendado) 🚀
Levanta todo el entorno de desarrollo (dependencias, base de datos, hooks de git y semillas de datos) con un solo comando:

```bash
uv run python scripts/backend_setup.py
```

### 2. Estructura de Módulos 🧩
Cada pieza del sistema está en su lugar. Así se organiza la inteligencia de Yastubo:

*   **🔐 Auth:** Identidad robusta basada en JWT y control de acceso por roles (RBAC).
*   **📋 Plans:** Lógica actuarial profunda con recargos por edad, países y versionado dinámico.
*   **🖋️ Emission:** El corazón del negocio; orquestación de leads, clientes y emisión de pólizas.
*   **💳 Payments:** Integración profunda con el ecosistema de Stripe y manejo de webhooks financieros.
*   **🩺 Claims:** Gestión sensible de siniestros, validación de beneficiarios y coordinación de servicios.
*   **🤖 AI:** Modelos y prompts optimizados para la automatización inteligente del flujo de trabajo.

---

## 🧪 Quality Gate

En Yastubo, la calidad no es una opción, es nuestra base. Nuestro "Quality Gate" asegura que cada cambio cumpla con los estándares técnicos más altos.

*   **Check de Integridad:** `uv run python scripts/build.py` (Ejecuta Lint obligatorio + Test Suite completa).
*   **Consola de Pruebas:** `uv run python scripts/test_console.py` para un desarrollo iterativo rápido.
*   **Mantenimiento:** `make build` para asegurar que el proyecto está listo para producción.

---

## 📖 Documentación Viva

Hemos construido una experiencia de documentación de clase mundial con **Astro Starlight**. Encontrarás guías interactivas, diagramas de flujo y la referencia completa de la API.

*   **Acceso Principal:** `http://localhost:4321`
*   **Atajos Rápidos:**
    *   [🚀 Guía de Instalación](http://localhost:4321/get-started/installation/)
    *   [🏛️ Arquitectura Técnica](http://localhost:4321/guides/architecture/)
    *   [💻 CLI Master Guide](http://localhost:4321/dx/cli/)
    *   [🤝 Cómo Contribuir](http://localhost:4321/dx/contributing/)

---

<p align="center">
  Hecho con ❤️ por el equipo de <b>TechAtlas</b> para transformar el futuro de los seguros.
</p>
