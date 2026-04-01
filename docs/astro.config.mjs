// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'Yastubo Backend API',
			logo: {
				src: './src/assets/logo_header.png',
				alt: 'Yastubo Logo',
				replacesTitle: true,
			},
			customCss: ['./src/styles/custom.css'],
			expressiveCode: {
				themes: ['github-dark'],
			},
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/TechAtlasDev/yastubo_backend' }],
			sidebar: [
				{
					label: 'Get Started',
					items: [
						{ label: 'Introducción', slug: 'get-started/introduction' },
						{ label: 'Instalación', slug: 'get-started/installation' },
						{ label: 'Dev Machine (CLI)', slug: 'get-started/cli' },
						{ label: 'Quickstart', slug: 'get-started/quickstart' },
						{ label: 'Configuración (.env)', slug: 'get-started/environment-setup' },
						{ label: 'Servidor Local', slug: 'get-started/local-server' },
					],
				},
				{
					label: 'Concepts',
					items: [
						{ label: 'Decisiones Arquitectónicas', slug: 'concepts/architecture-decisions' },
						{ label: 'Thinking in Yastubo', slug: 'concepts/thinking-in-yastubo' },
						{ label: 'Arquitectura', slug: 'concepts/architecture' },
						{ label: 'Máquina de Estados', slug: 'concepts/state-machine' },
						{ label: 'Seguridad y RBAC', slug: 'concepts/security-rbac' },
						{ label: 'Diseño Audit-First', slug: 'concepts/audit-first-design' },
					],
				},
				{
					label: 'Core Workflows',
					items: [
						{ label: 'Emisión de Pólizas', slug: 'workflows/issuing-a-policy' },
						{ label: 'Gestión de Pagos', slug: 'workflows/managing-payments' },
						{ label: 'Ciclo de Vida de Siniestros', slug: 'workflows/claims-lifecycle' },
						{ label: 'Automatización con IA', slug: 'workflows/automating-with-ai' },
						{ label: 'Sincronización con CRM', slug: 'workflows/crm-sync' },
					],
				},
				{
					label: 'API Reference',
					items: [
						{ label: 'IAM / Autenticación', slug: 'api-reference/iam' },
						{ label: 'Catálogo / Productos', slug: 'api-reference/catalog' },
						{ label: 'Emisión / Pólizas', slug: 'api-reference/policy-engine' },
						{ label: 'Finanzas / Pagos', slug: 'api-reference/financial' },
						{ label: 'Inteligencia / IA', slug: 'api-reference/intelligence' },
						{ label: 'CRM / Leads', slug: 'api-reference/crm-leads' },
						{ label: 'Siniestros / Claims', slug: 'api-reference/claims' },
						{ label: 'Operaciones / Infra', slug: 'api-reference/ops' },
					],
				},
				{
					label: 'Guides',
					items: [
						{ label: 'Creación de un Nuevo Módulo', slug: 'guides/creating-new-module' },
						{ label: 'Personalización del Calculador', slug: 'guides/customizing-calculator' },
						{ label: 'Integración de Webhooks', slug: 'guides/webhook-integration' },
						{ label: 'Generación de PDF y Passbook', slug: 'guides/document-generation' },
					],
				},
				{
					label: 'Referencia de Módulos',
					items: [
						{ label: 'Auth (Identidad)', slug: 'reference/auth' },
						{ label: 'Plans (Actuarial)', slug: 'reference/plans' },
						{ label: 'Emission (Pólizas)', slug: 'reference/emission' },
						{ label: 'Payments (Pagos)', slug: 'reference/payments' },
						{ label: 'Claims (Siniestros)', slug: 'reference/claims' },
						{ label: 'Audit (Auditoría)', slug: 'reference/audit' },
						{ label: 'Notifications (Alertas)', slug: 'reference/notifications' },
						{ label: 'IA (Inteligencia)', slug: 'reference/ai' },
					],
				},
				{
					label: 'Operations & Deployment',
					items: [
						{ label: 'Setup de Producción', slug: 'operations/production' },
						{ label: 'Escalabilidad', slug: 'operations/scaling' },
						{ label: 'Monitoreo', slug: 'operations/monitoring' },
						{ label: 'CI/CD', slug: 'operations/cicd' },
						{ label: 'Migraciones', slug: 'operations/migrations' },
					],
				},
				{
					label: 'Integraciones & n8n',
					items: [
						{ label: 'Arquitectura n8n', slug: 'integrations/n8n/overview' },
						{ label: 'Catálogo de Flujos', slug: 'integrations/n8n/flows' },
						{ label: 'Guía de Creación', slug: 'integrations/n8n/guide' },
						{ label: 'Seguridad y Auth', slug: 'integrations/n8n/security' },
					],
				},
				{
					label: 'Developer Experience (DX)',
					items: [
						{ label: 'Contributing', slug: 'dx/contributing' },
						{ label: 'Releases & Changelog', slug: 'dx/changelog' },
						{ label: 'CLI Reference', slug: 'dx/cli' },
						{ label: 'Estrategia en Testing', slug: 'dx/testing' },
						{ label: 'Standares de calidad', slug: 'dx/standards' },
					],
				},
			],
		}),
	],
});
