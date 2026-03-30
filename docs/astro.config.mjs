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
						{ label: 'Architecture', slug: 'concepts/architecture' },
						{ label: 'The State Machine', slug: 'concepts/state-machine' },
						{ label: 'Security & RBAC', slug: 'concepts/security-rbac' },
						{ label: 'Audit-First Design', slug: 'concepts/audit-first-design' },
					],
				},
				{
					label: 'Core Workflows',
					items: [
						{ label: 'Issuing a Policy', slug: 'workflows/issuing-a-policy' },
						{ label: 'Managing Payments', slug: 'workflows/managing-payments' },
						{ label: 'Claims Lifecycle', slug: 'workflows/claims-lifecycle' },
						{ label: 'Automating with AI', slug: 'workflows/automating-with-ai' },
						{ label: 'CRM Sync', slug: 'workflows/crm-sync' },
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
						{ label: 'Production Setup', slug: 'operations/production' },
						{ label: 'Scaling', slug: 'operations/scaling' },
						{ label: 'Monitoring', slug: 'operations/monitoring' },
						{ label: 'CI/CD', slug: 'operations/cicd' },
					],
				},
				{
					label: 'Developer Experience (DX)',
					items: [
						{ label: 'Contributing', slug: 'dx/contributing' },
						{ label: 'Releases & Changelog', slug: 'dx/changelog' },
						{ label: 'CLI Reference', slug: 'dx/cli' },
						{ label: 'Testing Strategy', slug: 'dx/testing' },
						{ label: 'Coding Standards', slug: 'dx/standards' },
					],
				},
			],
		}),
	],
});
