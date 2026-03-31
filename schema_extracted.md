## Companies

\`\`\`sql
CREATE TABLE companies (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `short_code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `status` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `branding_text_dark` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `branding_bg_light` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `branding_text_light` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `branding_bg_dark` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `branding_logo_file_id` bigint(20) unsigned DEFAULT NULL,
  `pdf_template_id` bigint(20) unsigned DEFAULT NULL,
  `commission_beneficiary_user_id` bigint(20) unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `companies_short_code_unique` (`short_code`),
  KEY `companies_branding_logo_file_id_foreign` (`branding_logo_file_id`),
  KEY `companies_commission_beneficiary_user_id_foreign` (`commission_beneficiary_user_id`),
  KEY `companies_pdf_template_id_foreign` (`pdf_template_id`),
  CONSTRAINT `companies_branding_logo_file_id_foreign` FOREIGN KEY (`branding_logo_file_id`) REFERENCES `files` (`id`) ON DELETE SET NULL,
  CONSTRAINT `companies_commission_beneficiary_user_id_foreign` FOREIGN KEY (`commission_beneficiary_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `companies_pdf_template_id_foreign` FOREIGN KEY (`pdf_template_id`) REFERENCES `templates` (`id`) ON DELETE SET NULL
)
\`\`\`

## Business Units

\`\`\`sql
CREATE TABLE business_units (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `parent_id` bigint(20) unsigned DEFAULT NULL,
  `name` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `branding_text_dark` varchar(12) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `branding_bg_light` varchar(12) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `branding_text_light` varchar(12) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `branding_bg_dark` varchar(12) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `branding_logo_file_id` bigint(20) unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `business_units_branding_logo_file_id_foreign` (`branding_logo_file_id`),
  KEY `business_units_type_index` (`type`),
  KEY `business_units_parent_id_index` (`parent_id`),
  KEY `business_units_status_index` (`status`),
  CONSTRAINT `business_units_branding_logo_file_id_foreign` FOREIGN KEY (`branding_logo_file_id`) REFERENCES `files` (`id`) ON DELETE SET NULL,
  CONSTRAINT `business_units_parent_id_foreign` FOREIGN KEY (`parent_id`) REFERENCES `business_units` (`id`)
)
\`\`\`
