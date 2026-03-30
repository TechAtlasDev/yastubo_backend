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
						{ label: 'Instalación Rápida', slug: 'guides/getting-started' },
						{ label: 'Instalación Detallada', slug: 'guides/installation' },
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
						{ label: 'Despliegue en VPS', slug: 'guides/deployment' },
						{ label: 'Scripts y CLI', slug: 'guides/scripts' },
						{ label: 'Arquitectura', slug: 'guides/architecture' },
					],
				},
				{
					label: 'Developer Experience (DX)',
					items: [
						{ label: 'Contributing', slug: 'guides/contributing' },
						{ label: 'Releases & Changelog', slug: 'reference/releases' },
					],
				},
			],
		}),
	],
});
