// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'Yastubo Backend API',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/TechAtlasDev/yastubo_backend' }],
			sidebar: [
				{
					label: 'Guides',
					items: [
						{ label: 'Getting Started', slug: 'guides/getting-started' },
					],
				},
				{
					label: 'API Reference',
					items: [
						{ label: 'Overview', slug: 'reference/overview' },
						{ label: 'Authentication', slug: 'reference/auth' },
						{ label: 'Plans', slug: 'reference/plans' },
						{ label: 'Emission (Policies)', slug: 'reference/emission' },
						{ label: 'Payments', slug: 'reference/payments' },
						{ label: 'Audit', slug: 'reference/audit' },
						{ label: 'Portal (Client)', slug: 'reference/portal' },
					],
				},
			],
		}),
	],
});
