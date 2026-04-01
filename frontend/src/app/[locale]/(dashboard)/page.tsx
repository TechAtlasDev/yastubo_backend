"use client";

import { useTranslations } from "next-intl";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { GlassCard } from "@/components/ui/glass-card";
import {
  FileText,
  DollarSign,
  Users,
  BadgeDollarSign,
  ArrowRight,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { useDashboardMetrics, useActivityFeed } from "@/hooks/use-dashboard";

const data = [
  { name: "Ene", value: 4000 },
  { name: "Feb", value: 3000 },
  { name: "Mar", value: 5000 },
  { name: "Abr", value: 2780 },
  { name: "May", value: 1890 },
  { name: "Jun", value: 2390 },
];

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const { data: metrics, isLoading: isMetricsLoading } = useDashboardMetrics();
  const { data: activities, isLoading: isActivitiesLoading } = useActivityFeed();

  const kpiData = [
    {
      label: "Total Pólizas",
      value: metrics?.total_policies || "1,248",
      icon: FileText,
      trend: { value: 12, isPositive: true },
    },
    {
      label: "Primas del Mes",
      value: metrics?.monthly_premiums || "45.2k",
      prefix: "$",
      icon: DollarSign,
      trend: { value: 8, isPositive: true },
    },
    {
      label: "Capitados Activos",
      value: metrics?.active_capitados || "8,920",
      icon: Users,
      trend: { value: 2, isPositive: false },
    },
    {
      label: "Comisiones Generadas",
      value: metrics?.total_commissions || "12.4k",
      prefix: "$",
      icon: BadgeDollarSign,
      trend: { value: 15, isPositive: true },
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div>
        <h1 className="text-3xl font-bold text-[var(--color-neutral-900)] tracking-tight">
          {t("title")}
        </h1>
        <p className="text-[var(--color-neutral-500)] mt-1">
          {t("description")}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiData.map((kpi, i) => (
          <KpiCard key={i} {...kpi} isLoading={isMetricsLoading} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <GlassCard className="lg:col-span-2 p-6 flex flex-col h-[400px]">
          <div className="flex items-center justify-between mb-8">
            <h3 className="text-lg font-bold text-[var(--color-neutral-900)]">
              Primas por Mes
            </h3>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[var(--color-primary-500)]" />
              <span className="text-xs text-[var(--color-neutral-500)] font-medium">
                2024
              </span>
            </div>
          </div>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#f0f0f0"
                />
                <XAxis
                  dataKey="name"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--color-neutral-400)", fontSize: 12 }}
                  dy={10}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--color-neutral-400)", fontSize: 12 }}
                />
                <Tooltip
                  cursor={{ fill: "var(--color-neutral-50)", radius: 8 }}
                  contentStyle={{
                    borderRadius: "12px",
                    border: "none",
                    boxShadow: "var(--shadow-lg)",
                  }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} barSize={32}>
                  {data.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        index === data.length - 1
                          ? "var(--color-primary-500)"
                          : "var(--color-primary-100)"
                      }
                      className="hover:fill-[var(--color-primary-500)] transition-colors cursor-pointer"
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <div className="lg:col-span-1 h-[400px]">
          <ActivityFeed
            activities={activities}
            isLoading={isActivitiesLoading}
          />
        </div>
      </div>

      <GlassCard className="p-8 bg-[var(--color-primary-900)] border-none relative overflow-hidden group">
        <div className="relative z-10">
          <h2 className="text-2xl font-bold text-white mb-2">
            ¿Listo para emitir una nueva póliza?
          </h2>
          <p className="text-blue-100/80 mb-6 max-w-lg">
            Utiliza nuestro asistente inteligente para configurar productos y
            emitir pólizas en segundos.
          </p>
          <button className="bg-white text-[var(--color-primary-900)] px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:bg-blue-50 transition-colors shadow-lg">
            Empezar Emisión
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-primary-500/20 rounded-full translate-y-1/2 -translate-x-1/2 blur-3xl pointer-events-none" />
      </GlassCard>
    </div>
  );
}
