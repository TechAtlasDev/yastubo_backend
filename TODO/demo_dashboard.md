# Diseño de Dashboard — Demo Concurso Yastubo

Este documento propone la estructura de pantallas para la demo de 10 minutos, mapeando endpoints reales a componentes visuales de Craft (Keenthemes).

## Resumen de la Narrativa de Demo (10 min)
1.  **Inicio (1 min):** Login y Dashboard Global (Métricas).
2.  **Configuración (2 min):** Simular creación de Compañía y Producto (Seguro Vida).
3.  **Operación Masiva (3 min):** Carga de Excel de capitados (1,000 empleados).
4.  **Casos Especiales (2 min):** Emisión individual de póliza manual.
5.  **Cierre (2 min):** Revisión de comisiones generadas y auditoría.

---

## Pantalla 1: Dashboard Principal (Métricas Globales)

**Ruta:** `/dashboard`
**Flujo de demo:** 1. Inicio y 5. Cierre
**Componentes Craft:** Stats Widgets (Cards con iconos), Charts (Barra para primas/mes), Tabla de Actividad Reciente.
**Endpoints:**
  - `GET /api/v1/dashboard/metrics` — alimenta los widgets de KPI (Total pólizas, primas).
  - `GET /api/v1/audit/` — alimenta la tabla de "Actividad Reciente del Sistema".
**Datos de ejemplo necesarios:** Al menos 10 pólizas emitidas previamente y 5 registros de auditoría de creación de productos.
**Notas para la presentación:** "Aquí vemos el pulso en tiempo real de la aseguradora: ventas acumuladas y el rastro de auditoría de cada acción administrativa."

---

## Pantalla 2: Catálogo de Productos (Configuración)

**Ruta:** `/dashboard/products/create`
**Flujo de demo:** 2. Crear producto con versiones y precios
**Componentes Craft:** Formulario Paso a Paso (Wizard), Repeater de campos (para versiones/planes), Selects con búsqueda.
**Endpoints:**
  - `POST /api/v1/products/` — para guardar la estructura completa (Producto > Plan > Versión).
  - `GET /api/v1/finance/currencies` — para poblar el select de monedas.
**Datos de ejemplo necesarios:** Definir un producto "Seguro Vida Colectivo" con dos planes: "Básico" y "Premium".
**Notas para la presentación:** "Yastubo permite crear productos paramétricos en minutos. Definimos coberturas, recargos por edad y disponibilidad por país sin tocar una línea de código."

---

## Pantalla 3: Carga de Capitados (Operación)

**Ruta:** `/dashboard/capitados/upload`
**Flujo de demo:** 3. Cargar un Excel de capitados
**Componentes Craft:** File Upload (Dropzone), Progress Bar (para el procesamiento), Badge de Status (Success/Error).
**Endpoints:**
  - `POST /api/v1/capitados/batches/upload` — sube el archivo Excel.
  - `GET /api/v1/capitados/batches/{id}` — consulta el estado cada 2 segundos mientras procesa.
  - `GET /api/v1/capitados/batches/{id}/items` — muestra la tabla de errores si alguna fila falló.
**Datos de ejemplo necesarios:** Excel de prueba con ~100 filas (algunas con errores para mostrar la validación).
**Notas para la presentación:** "Para seguros colectivos, procesamos miles de vidas en segundos. El sistema valida edad, país y kinship (parentesco) automáticamente antes de emitir."

---

## Pantalla 4: Emisión Individual (Manual)

**Ruta:** `/dashboard/emission/new`
**Flujo de demo:** 4. Emitir una póliza individual
**Componentes Craft:** Formulario de cliente, Modal de confirmación, Botón de "Descargar PDF".
**Endpoints:**
  - `POST /api/v1/emission/clients` — registra al tomador.
  - `POST /api/v1/emission/issue` — emite la póliza vinculada al plan creado en el Paso 2.
  - `GET /api/v1/emission/policies/{id}/pdf` — descarga el certificado PDF generado.
**Datos de ejemplo necesarios:** Un cliente "Juan Pérez" listo para ser registrado.
**Notas para la presentación:** "Para ventas directas o casos especiales, el agente puede emitir una póliza individual y entregar el certificado digital al instante."

---

## Identificación de Brechas Técnicas

### 1. Endpoints que faltan
- **Creación de Organizaciones:** No existen endpoints para `POST /companies`. Para la demo, se debe usar una empresa pre-creada vía Script/Seed o implementar el router en `app/modules/organizations/router.py`.
- **Listado Agregado de Comisiones:** Aunque existe el cálculo de dispersión, falta un listado tipo `/finance/commissions/summary` para ver cuánto ganó cada Unidad de Negocio en total.

### 2. Pantallas que requieren desarrollo adicional
- **Gestión de Organizaciones:** Actualmente no hay una interfaz para configurar la jerarquía de Unidades de Negocio (Agencias -> Sucursales).
- **Consola de IA de Voz:** Se necesitaría una pantalla simple para mostrar el log del asistente de voz (`/voice/stream`) y cómo responde a las llamadas de los clientes.

### 3. Datos de ejemplo (Seed) recomendados
- **Geografía:** Paises (Colombia, México, Chile) y Monedas (COP, MXN, CLP, USD) deben estar en la DB.
- **Roles:** Los roles `ADMIN` y `VENDEDOR` deben estar configurados en la tabla `roles` para que el flujo de permisos funcione.
- **Audit:** Seed de logs de auditoría para que la pantalla principal no se vea vacía al iniciar.
