# 🎨 Plan de Frontend — Dashboard Demo Yastubo

**Stack:** Next.js 14 (App Router) + shadcn/ui + TanStack Query + Zustand + next-intl  
**Idiomas:** Español / Inglés  
**Audiencia:** Jueces del concurso — perfil Admin de la aseguradora  
**Objetivo:** Demo fluida de 10 minutos que demuestre las 5 capacidades core del sistema

---

## 📦 Stack Técnico

| Responsabilidad | Librería | Por qué |
|----------------|----------|---------|
| Framework | Next.js 14 App Router | SSR, routing, layouts anidados |
| UI Components | shadcn/ui + Tailwind | Componentes accesibles, fácil de customizar |
| Estado servidor | TanStack Query v5 | Cache, loading/error, refetch automático |
| Estado cliente | Zustand | Token JWT, usuario autenticado |
| HTTP Client | Axios | Interceptores para adjuntar Bearer token |
| Formularios | React Hook Form + Zod | Validación tipada, integra con shadcn |
| i18n | next-intl | Español/Inglés nativo en App Router |
| Gráficas | Recharts | Lightweight, funciona con shadcn |
| Tablas | TanStack Table v8 | Paginación, sorting, filtros |
| Upload Excel | react-dropzone | Drag & drop para capitados |
| PDF Viewer | react-pdf | Preview del certificado de póliza |
| Notificaciones | sonner | Toasts elegantes |
| Iconos | lucide-react | Ya incluido en shadcn |

---

## 🗂️ Estructura del Proyecto

```
yastubo-frontend/
├── app/
│   ├── [locale]/                    # next-intl
│   │   ├── (auth)/
│   │   │   └── login/page.tsx
│   │   └── (dashboard)/
│   │       ├── layout.tsx           # Sidebar + Header globales
│   │       ├── page.tsx             # Dashboard principal
│   │       ├── organizations/
│   │       │   ├── page.tsx         # Lista de empresas
│   │       │   ├── new/page.tsx     # Crear empresa
│   │       │   └── [id]/page.tsx    # Detalle + unidades de negocio
│   │       ├── products/
│   │       │   ├── page.tsx         # Catálogo de productos
│   │       │   └── new/page.tsx     # Crear producto (wizard)
│   │       ├── capitados/
│   │       │   ├── page.tsx         # Historial de batches
│   │       │   └── upload/page.tsx  # Carga de Excel
│   │       ├── emission/
│   │       │   ├── page.tsx         # Lista de pólizas
│   │       │   └── new/page.tsx     # Emitir póliza individual
│   │       ├── finance/
│   │       │   └── page.tsx         # Dashboard de comisiones
│   │       └── audit/
│   │           └── page.tsx         # Log de auditoría
├── components/
│   ├── ui/                          # shadcn components (auto-generados)
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── BreadCrumb.tsx
│   ├── dashboard/
│   │   ├── KpiCard.tsx
│   │   └── ActivityFeed.tsx
│   ├── organizations/
│   │   ├── CompanyForm.tsx
│   │   ├── CompanyTable.tsx
│   │   └── BusinessUnitForm.tsx
│   ├── products/
│   │   ├── ProductWizard.tsx        # Wizard de 3 pasos
│   │   ├── PlanVersionForm.tsx
│   │   └── ProductCard.tsx
│   ├── capitados/
│   │   ├── BatchUploader.tsx        # Dropzone + progress
│   │   ├── BatchStatusCard.tsx
│   │   └── BatchItemsTable.tsx
│   ├── emission/
│   │   ├── PolicyForm.tsx
│   │   ├── PolicyTable.tsx
│   │   └── PolicyPdfViewer.tsx
│   └── finance/
│       ├── CommissionCalculator.tsx
│       └── CommissionChart.tsx
├── lib/
│   ├── api/
│   │   ├── client.ts                # Axios instance con interceptores
│   │   ├── auth.ts                  # Endpoints de auth
│   │   ├── organizations.ts
│   │   ├── products.ts
│   │   ├── capitados.ts
│   │   ├── emission.ts
│   │   └── finance.ts
│   ├── store/
│   │   └── auth.store.ts            # Zustand: user, token, logout
│   └── hooks/
│       ├── useCompanies.ts          # TanStack Query hooks
│       ├── useProducts.ts
│       ├── useCapitados.ts
│       └── usePolicies.ts
├── messages/
│   ├── es.json                      # Traducciones español
│   └── en.json                      # Traducciones inglés
└── middleware.ts                    # next-intl routing
```

---

## 🗺️ Roadmap de Pantallas

### F-00 · Setup inicial del proyecto

**Objetivo:** Proyecto Next.js funcionando con todas las dependencias, CORS verificado y axios configurado con el token.

**Entregables:**
- `npx create-next-app` con TypeScript y Tailwind
- shadcn/ui inicializado
- axios client con interceptor de Bearer token
- Zustand store de auth
- next-intl configurado (es/en)
- Variable de entorno `NEXT_PUBLIC_API_URL`
- Verificar CORS en el backend (`app/main.py`) y corregir si es necesario

**Criterio de éxito:** `GET /api/v1/auth/me` funciona desde el frontend con token válido.

---

### F-01 · Autenticación

**Ruta:** `/[locale]/login`  
**Flujo de demo:** Inicio — el juez ve el login primero

**Componentes shadcn:** Card, Input, Button, Form  
**Endpoints:**
- `POST /api/v1/auth/login` → guarda token en Zustand + cookie httpOnly
- `GET /api/v1/auth/me` → carga perfil del usuario

**Comportamiento:**
- Login exitoso → redirect a `/dashboard`
- Token expirado → redirect automático a `/login`
- Middleware de Next.js protege todas las rutas `/dashboard/*`

**Datos de demo:** Usuario admin pre-creado con `seed_roles.py`

---

### F-02 · Dashboard Principal

**Ruta:** `/[locale]/dashboard`  
**Flujo de demo:** Pantalla de bienvenida — primera impresión ante los jueces

**Componentes shadcn:** Card, Badge, Skeleton (loading state)  
**Librerías:** Recharts para gráfica de primas por mes  
**Endpoints:**
- `GET /api/v1/dashboard/metrics` → KPI cards
- `GET /api/v1/audit/` → feed de actividad reciente

**Layout:**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total       │ Primas      │ Capitados   │ Comisiones  │
│ Pólizas     │ del Mes     │ Activos     │ Generadas   │
└─────────────┴─────────────┴─────────────┴─────────────┘
┌──────────────────────────┬──────────────────────────────┐
│ Gráfica: Primas por mes  │ Feed: Actividad reciente     │
│ (Recharts BarChart)      │ (lista de audit logs)        │
└──────────────────────────┴──────────────────────────────┘
```

**Datos de demo necesarios:** Script `seed_demo.py` con 10 pólizas y 5 audit logs pre-cargados.

---

### F-03 · Organizaciones

**Rutas:**
- `/dashboard/organizations` — lista de empresas
- `/dashboard/organizations/new` — crear empresa
- `/dashboard/organizations/[id]` — detalle + unidades de negocio

**Flujo de demo:** "Así se onboardea una nueva aseguradora en el sistema"

**Componentes shadcn:** DataTable, Dialog, Form, Tabs, Badge  
**Endpoints:**
- `GET /api/v1/organizations/companies`
- `POST /api/v1/organizations/companies`
- `GET /api/v1/organizations/companies/{id}`
- `POST /api/v1/organizations/companies/{id}/business-units`

**Flujo en pantalla:**
1. Lista de empresas existentes (tabla)
2. Click "Nueva Empresa" → abre Dialog con formulario
3. Empresa creada → aparece en tabla con badge "Activa"
4. Click en empresa → detalle con tabs: Info | Unidades de Negocio | Comisiones

---

### F-04 · Productos

**Rutas:**
- `/dashboard/products` — catálogo de productos
- `/dashboard/products/new` — wizard de creación

**Flujo de demo:** "Configuramos un nuevo seguro de vida colectivo en minutos"

**Componentes shadcn:** Card, Stepper (wizard), Form, Select, Badge, Accordion  
**Endpoints:**
- `GET /api/v1/products/`
- `POST /api/v1/products/`
- `GET /api/v1/finance/currencies`

**Wizard de 3 pasos:**
```
Paso 1: Información del Producto
  → Nombre, descripción, tipo de producto

Paso 2: Planes y Versiones
  → Nombre del plan, precio base, moneda
  → Tiempos de carencia (suicide, accident, preexisting)

Paso 3: Configuración por País
  → Precio por país de residencia
  → Recargos por rango de edad
  → Países de repatriación permitidos
```

**Datos de demo:** Al finalizar el wizard, producto visible en el catálogo con badge "Activo".

---

### F-05 · Capitados

**Rutas:**
- `/dashboard/capitados` — historial de batches
- `/dashboard/capitados/upload` — carga de Excel

**Flujo de demo:** "Procesamos 1,000 vidas en segundos con validación automática"

**Componentes shadcn:** DataTable, Badge, Progress, Alert  
**Librerías:** react-dropzone para el upload  
**Endpoints:**
- `POST /api/v1/capitados/batches/upload`
- `GET /api/v1/capitados/batches/{id}` — polling cada 2s
- `GET /api/v1/capitados/batches/{id}/items`

**Flujo en pantalla:**
1. Dropzone para arrastrar el Excel
2. Seleccionar empresa y mes de cobertura
3. Click "Procesar" → barra de progreso animada
4. Polling al backend cada 2 segundos
5. Resultado: tabla con filas aplicadas / rechazadas / duplicadas
6. Badge de estado: verde (completado) / rojo (con errores)

**Datos de demo:** Excel de prueba con 100 filas (80 válidas, 15 errores, 5 duplicadas).

---

### F-06 · Emisión Individual

**Rutas:**
- `/dashboard/emission` — lista de pólizas
- `/dashboard/emission/new` — emitir póliza

**Flujo de demo:** "Para casos individuales, emisión en 3 pasos con certificado instantáneo"

**Componentes shadcn:** Form, Select, Dialog, Table, Button  
**Librerías:** react-pdf para preview del certificado  
**Endpoints:**
- `POST /api/v1/emission/clients`
- `POST /api/v1/emission/issue`
- `GET /api/v1/emission/policies`
- `GET /api/v1/emission/policies/{id}/pdf`

**Flujo en pantalla:**
1. Formulario: datos del asegurado (nombre, documento, fecha nacimiento)
2. Seleccionar producto y versión de plan
3. Click "Emitir" → póliza creada con número YAS-XXXX
4. Dialog: "Póliza emitida con éxito" + botón "Descargar PDF"
5. PDF se abre en nueva pestaña con el certificado

---

### F-07 · Finanzas y Comisiones

**Ruta:** `/dashboard/finance`  
**Flujo de demo:** "Visibilidad total de la dispersión económica"

**Componentes shadcn:** Card, Table, Form  
**Librerías:** Recharts PieChart  
**Endpoints:**
- `POST /api/v1/finance/commissions/calculate`
- `GET /api/v1/finance/currencies`

**Layout:**
```
┌─────────────────────────────┬──────────────────────────────┐
│ Calculadora de Comisiones   │ Gráfica de Dispersión        │
│ Monto: [input]              │ (PieChart: Empresa/BU/Agente)│
│ Empresa: [select]           │                              │
│ [Calcular]                  │                              │
└─────────────────────────────┴──────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Resultado: tabla con actor | porcentaje | monto calculado   │
└─────────────────────────────────────────────────────────────┘
```

---

### F-08 · Auditoría

**Ruta:** `/dashboard/audit`  
**Flujo de demo:** "Trazabilidad completa de cada acción en el sistema"

**Componentes shadcn:** DataTable, Badge, DateRangePicker  
**Endpoints:**
- `GET /api/v1/audit/`

**Funcionalidad:** Tabla paginada con filtros por fecha, usuario y tipo de acción. Muestra quién hizo qué y cuándo.

---

## 🔧 Configuración de CORS en Backend

Antes de iniciar el frontend, verificar y configurar en `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Next.js dev
        "https://tudominio.com",    # Producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📋 Tabla de Control Frontend

| ID | Pantalla | Endpoints | Estado |
|----|----------|-----------|--------|
| F-00 | Setup + CORS | — | [ ] |
| F-01 | Login | auth/login, auth/me | [ ] |
| F-02 | Dashboard | metrics, audit | [ ] |
| F-03 | Organizaciones | companies CRUD | [ ] |
| F-04 | Productos | products CRUD | [ ] |
| F-05 | Capitados | batches upload | [ ] |
| F-06 | Emisión | emission/issue, pdf | [ ] |
| F-07 | Finanzas | commissions | [ ] |
| F-08 | Auditoría | audit | [ ] |

---

## 🎯 Narrativa de Demo (10 minutos)

```
00:00 - 01:00  Login como admin → Dashboard con KPIs reales
01:00 - 02:30  Crear empresa "Seguros Andinos" + unidad "Lima"
02:30 - 04:30  Crear producto "Vida Colectivo Premium" (wizard)
04:30 - 07:00  Cargar Excel con 100 capitados → ver progreso en vivo
07:00 - 08:30  Emitir póliza individual para "Juan Pérez" → PDF
08:30 - 09:30  Dashboard de comisiones generadas
09:30 - 10:00  Log de auditoría — trazabilidad completa
```

---

## ⚠️ Seed de Datos para Demo

Crear `scripts/seed_demo.py` con:
- 1 empresa "Seguros Andinos" con 2 unidades de negocio
- 1 producto "Vida Colectivo Premium" con 2 versiones
- 10 pólizas individuales emitidas
- 1 batch de capitados procesado (para el historial)
- Audit logs de las operaciones anteriores
- Usuario admin con email y password conocidos para el login en vivo
