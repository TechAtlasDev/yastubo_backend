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
						{ label: 'Quickstart', slug: 'get-started/quickstart' },
						{ label: 'Configuración de Entorno', slug: 'get-started/environment-setup' },
						{ label: 'Servidor Local', slug: 'get-started/local-server' },
					],
				},
				{
					label: 'Concepts',
					items: [
						{ label: 'Thinking in Yastubo', slug: 'concepts/thinking-in-yastubo' },
						{ label: 'Architecture', slug: 'concepts/architecture' },
						{ label: 'The State Machine', slug: 'concepts/state-machine' },
						{ label: 'Security & RBAC', slug: 'concepts/security-rbac' },
						{ label: 'Audit-First Design', slug: 'concepts/audit-first-design' },
					],
				},
				{
					label: 'Core Workflows',
					items: [
						{ label: 'Emisión de Pólizas', slug: 'workflows/issuing-a-policy' },
						{ label: 'Gestión de Pagos', slug: 'workflows/managing-payments' },
						{ label: 'Ciclo de Siniestros', slug: 'workflows/claims-lifecycle' },
						{ label: 'Automatización con IA', slug: 'workflows/automating-with-ai' },
						{ label: 'Sincronización con CRM', slug: 'workflows/crm-sync' },
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
						{ label: 'Overview', slug: 'reference/overview' },
						{ label: 'Auth (Identidad)', slug: 'reference/auth' },
						{ label: 'Plans (Actuarial)', slug: 'reference/plans' },
						{ label: 'Emission (Pólizas)', slug: 'reference/emission' },
						{ label: 'Payments (Pagos)', slug: 'reference/payments' },
						{ label: 'Claims (Siniestros)', slug: 'reference/claims' },
						{ label: 'Audit (Auditoría)', slug: 'reference/audit' },
						{ label: 'Notifications (Alertas)', slug: 'reference/notifications' },
						{ label: 'IA (Inteligencia)', slug: 'reference/ai' },
						{ label: 'Portal (Cliente)', slug: 'reference/portal' },
					],
				},
				{
					label: 'Operations & Deployment',
					items: [
						{ label: 'Production Setup', slug: 'operations/production' },
						{ label: 'Scaling & Workers', slug: 'operations/scaling' },
						{ label: 'Monitoring & Health', slug: 'operations/monitoring' },
						{ label: 'CI/CD Pipeline', slug: 'operations/cicd' },
					],
				},
				{
					label: 'Developer Experience (DX)',
					items: [
						{ label: 'CLI Reference', slug: 'dx/cli' },
						{ label: 'Testing Strategy', slug: 'dx/testing' },
						{ label: 'Coding Standards', slug: 'dx/standards' },
						{ label: 'Contributing', slug: 'dx/contributing' },
						{ label: 'Changelog', slug: 'dx/changelog' },
					],
				},
			],
		}),
	],
});
