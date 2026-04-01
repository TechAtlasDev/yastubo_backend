"use client";

import { useAuthStore } from "@/lib/store/auth.store";
import { useMe } from "@/hooks/use-auth";
import { Bell, Search, User as UserIcon } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export function Header() {
  const { data: user, isLoading } = useMe();

  return (
    <header className="h-20 bg-white/80 backdrop-blur-md border-b border-[var(--color-neutral-100)] px-8 flex items-center justify-between sticky top-0 z-30">
      <div className="flex-1 max-w-xl">
        <div className="relative group">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-neutral-300)] group-focus-within:text-[var(--color-primary-500)] transition-colors" />
          <input
            type="text"
            placeholder="Buscar pólizas, empresas o productos..."
            className="w-full bg-[var(--color-neutral-50)] border-none rounded-xl py-3 pl-11 pr-4 text-sm focus:ring-2 focus:ring-[var(--color-primary-100)] transition-all outline-none"
          />
        </div>
      </div>

      <div className="flex items-center gap-6">
        <button className="relative p-2 text-[var(--color-neutral-400)] hover:text-[var(--color-neutral-900)] transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-[var(--color-error)] rounded-full border-2 border-white" />
        </button>

        <div className="h-8 w-[1px] bg-[var(--color-neutral-200)]" />

        <div className="flex items-center gap-3">
          <div className="text-right">
            {isLoading ? (
              <div className="space-y-1">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-3 w-16" />
              </div>
            ) : (
              <>
                <p className="text-sm font-semibold text-[var(--color-neutral-900)]">
                  {user?.full_name || "Admin"}
                </p>
                <p className="text-xs text-[var(--color-neutral-500)] uppercase tracking-wider font-medium">
                  {user?.roles?.[0] || "Administrador"}
                </p>
              </>
            )}
          </div>
          <div className="w-10 h-10 rounded-xl bg-[var(--color-primary-50)] flex items-center justify-center border border-[var(--color-primary-100)]">
            <UserIcon className="w-5 h-5 text-[var(--color-primary-500)]" />
          </div>
        </div>
      </div>
    </header>
  );
}
