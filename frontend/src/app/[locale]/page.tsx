import { useTranslations } from "next-intl";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  const t = useTranslations("dashboard");

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <GlassCard className="max-w-md p-10 text-center">
        <h1 className="text-4xl font-bold text-[var(--color-primary-600)] mb-4">
          {t("title")}
        </h1>
        <p className="text-lg text-[var(--color-neutral-500)] mb-8">
          {t("description")}
        </p>
        <Button className="bg-[var(--color-primary-500)] hover:bg-[var(--color-primary-600)] text-white">
          Continuar
        </Button>
      </GlassCard>
    </main>
  );
}
