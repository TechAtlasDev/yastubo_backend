import { GlassCard } from "@/components/ui/glass-card";
import { Skeleton } from "@/components/ui/skeleton";
import { Circle, User, Package, Building2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";

interface Activity {
  id: string;
  action: string;
  user_name: string;
  module: string;
  created_at: string;
}

interface ActivityFeedProps {
  activities?: Activity[];
  isLoading?: boolean;
}

const getIcon = (module: string) => {
  switch (module.toLowerCase()) {
    case "auth":
      return User;
    case "products":
      return Package;
    case "organizations":
      return Building2;
    default:
      return Circle;
  }
};

const getColor = (module: string) => {
  switch (module.toLowerCase()) {
    case "auth":
      return "text-blue-500 bg-blue-50";
    case "products":
      return "text-purple-500 bg-purple-50";
    case "organizations":
      return "text-amber-500 bg-amber-50";
    default:
      return "text-gray-500 bg-gray-50";
  }
};

export function ActivityFeed({ activities, isLoading }: ActivityFeedProps) {
  return (
    <GlassCard className="p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-[var(--color-neutral-900)]">
          Actividad Reciente
        </h3>
        <button className="text-sm text-[var(--color-primary-500)] font-medium hover:underline">
          Ver todo
        </button>
      </div>

      <div className="flex-1 space-y-6">
        {isLoading
          ? Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex gap-4">
                <Skeleton className="w-10 h-10 rounded-full" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/4" />
                </div>
              </div>
            ))
          : activities?.map((activity) => {
              const Icon = getIcon(activity.module);
              const colorClass = getColor(activity.module);
              return (
                <div key={activity.id} className="flex gap-4 group">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-110 ${colorClass}`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-[var(--color-neutral-900)] truncate">
                      <span className="font-bold">{typeof activity.user_name === 'string' ? activity.user_name : "Usuario"}</span>{" "}
                      {typeof activity.action === 'string' ? activity.action : "realizó una acción"}
                    </p>
                    <p className="text-xs text-[var(--color-neutral-400)] mt-1">
                      {formatDistanceToNow(new Date(activity.created_at), {
                        addSuffix: true,
                        locale: es,
                      })}
                    </p>
                  </div>
                </div>
              );
            })}
      </div>
    </GlassCard>
  );
}
