"use client";

import { Link, usePathname } from "@/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Building2,
  Package,
  Users,
  FileText,
  BadgeDollarSign,
  History,
  LogOut,
  ShieldCheck,
} from "lucide-react";
import { useAuthStore } from "@/lib/store/auth.store";
import { useTranslations } from "next-intl";

const menuItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/" },
  { icon: Building2, label: "Organizaciones", href: "/organizations" },
  { icon: Package, label: "Productos", href: "/products" },
  { icon: Users, label: "Capitados", href: "/capitados" },
  { icon: FileText, label: "Emisión", href: "/emission" },
  { icon: BadgeDollarSign, label: "Finanzas", href: "/finance" },
  { icon: History, label: "Auditoría", href: "/audit" },
];

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations("auth");
  const logout = useAuthStore((state) => state.logout);

  return (
    <aside className="w-64 flex flex-col h-full bg-white border-r border-[var(--color-neutral-200)] transition-all duration-300">
      <div className="p-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-[var(--color-primary-500)] rounded-lg flex items-center justify-center">
          <ShieldCheck className="text-white w-5 h-5" />
        </div>
        <span className="text-xl font-bold text-[var(--color-neutral-900)] tracking-tight">
          Yastubo
        </span>
      </div>

      <nav className="flex-1 px-4 py-4 space-y-1">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                isActive
                  ? "bg-[var(--color-primary-50)] text-[var(--color-primary-600)] font-medium"
                  : "text-[var(--color-neutral-500)] hover:bg-[var(--color-neutral-50)] hover:text-[var(--color-neutral-900)]"
              )}
            >
              <item.icon
                className={cn(
                  "w-5 h-5 transition-colors",
                  isActive
                    ? "text-[var(--color-primary-600)]"
                    : "text-[var(--color-neutral-300)] group-hover:text-[var(--color-neutral-500)]"
                )}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-[var(--color-neutral-100)]">
        <button
          onClick={() => logout()}
          className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-[var(--color-error)] hover:bg-red-50 transition-all duration-200"
        >
          <LogOut className="w-5 h-5" />
          {t("logout")}
        </button>
      </div>
    </aside>
  );
}
