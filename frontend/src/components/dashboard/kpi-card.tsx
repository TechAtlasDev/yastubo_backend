import { GlassCard } from "@/components/ui/glass-card";
import { cn } from "@/lib/utils";
import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

interface KpiCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  isLoading?: boolean;
  prefix?: string;
}

export function KpiCard({
  label,
  value,
  icon: Icon,
  trend,
  isLoading,
  prefix,
}: KpiCardProps) {
  if (isLoading) {
    return (
      <GlassCard className="p-6">
        <div className="flex justify-between items-start mb-4">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-10 w-10 rounded-xl" />
        </div>
        <Skeleton className="h-8 w-32 mb-2" />
        <Skeleton className="h-4 w-20" />
      </GlassCard>
    );
  }

  return (
    <GlassCard className="p-6 group hover:-translate-y-1">
      <div className="flex justify-between items-start mb-4">
        <p className="text-sm font-medium text-[var(--color-neutral-500)] uppercase tracking-wider">
          {label}
        </p>
        <div className="p-2.5 rounded-xl bg-[var(--color-primary-50)] text-[var(--color-primary-500)] group-hover:bg-[var(--color-primary-500)] group-hover:text-white transition-all duration-300">
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <h3 className="text-2xl font-bold text-[var(--color-neutral-900)] mb-1">
        {prefix && <span className="text-lg font-medium mr-1">{prefix}</span>}
        {value}
      </h3>

      {trend && (
        <div className="flex items-center gap-1.5">
          <div
            className={cn(
              "flex items-center text-xs font-semibold px-1.5 py-0.5 rounded-md",
              trend.isPositive
                ? "text-[var(--color-success)] bg-green-50"
                : "text-[var(--color-error)] bg-red-50"
            )}
          >
            {trend.isPositive ? (
              <TrendingUp className="w-3 h-3 mr-1" />
            ) : (
              <TrendingDown className="w-3 h-3 mr-1" />
            )}
            {trend.value}%
          </div>
          <span className="text-xs text-[var(--color-neutral-400)]">
            vs mes anterior
          </span>
        </div>
      )}
    </GlassCard>
  );
}
