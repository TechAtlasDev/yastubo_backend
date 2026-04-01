"use client";

import { useTranslations } from "next-intl";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Plus, Package, Info } from "lucide-react";
import { Link } from "@/navigation";
import { useQuery } from "@tanstack/react-query";
import { productsApi } from "@/lib/api/modules";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

export default function ProductsPage() {
  const t = useTranslations("dashboard");
  const { data: products, isLoading } = useQuery({
    queryKey: ["products"],
    queryFn: productsApi.list,
  });

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[var(--color-neutral-900)] tracking-tight">
            Productos y Planes
          </h1>
          <p className="text-[var(--color-neutral-500)] mt-1">
            Gestiona el catálogo de productos y configuraciones actuariales
          </p>
        </div>
        <Button className="bg-[var(--color-primary-500)] hover:bg-[var(--color-primary-600)] text-white shadow-lg shadow-primary-500/20">
          <Plus className="w-5 h-5 mr-2" />
          Nuevo Producto
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <GlassCard key={i} className="p-6 space-y-4">
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-20 w-full" />
              <div className="flex justify-between">
                <Skeleton className="h-8 w-20" />
                <Skeleton className="h-8 w-24" />
              </div>
            </GlassCard>
          ))
        ) : products?.length > 0 ? (
          products.map((product: any) => (
            <GlassCard key={product.id} className="p-6 group hover:shadow-lg transition-all duration-300 border-none bg-white/60">
              <div className="flex justify-between items-start mb-4">
                <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center text-primary-500 group-hover:scale-110 transition-transform">
                  <Package className="w-6 h-6" />
                </div>
                <Badge variant={product.is_active ? "default" : "secondary"}>
                  {product.is_active ? "Activo" : "Inactivo"}
                </Badge>
              </div>
              <h3 className="text-lg font-bold text-neutral-900 mb-2">{product.name}</h3>
              <p className="text-sm text-neutral-500 line-clamp-2 mb-6 h-10">
                {product.description || "Sin descripción disponible."}
              </p>
              <div className="flex items-center justify-between pt-4 border-t border-neutral-100">
                <span className="text-xs font-medium text-neutral-400">
                  ID: {product.code || product.id.slice(0, 8)}
                </span>
                <Button variant="ghost" size="sm" asChild className="group/btn text-primary-600 hover:text-primary-700 hover:bg-primary-50">
                  <Link href={`/products/${product.id}`}>
                    Detalles
                    <Plus className="w-4 h-4 ml-2 opacity-0 group-hover/btn:opacity-100 transition-opacity" />
                  </Link>
                </Button>
              </div>
            </GlassCard>
          ))
        ) : (
          <GlassCard className="col-span-full p-12 text-center flex flex-col items-center justify-center bg-white/40">
            <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mb-4">
              <Package className="w-8 h-8 text-neutral-300" />
            </div>
            <h3 className="text-xl font-bold text-neutral-900">No hay productos</h3>
            <p className="text-neutral-500 max-w-sm mt-2">
              Comienza creando tu primer producto para definir coberturas y precios.
            </p>
            <Button variant="outline" className="mt-6 border-primary-200 text-primary-600 hover:bg-primary-50">
              Ver Guía de Productos
            </Button>
          </GlassCard>
        )}
      </div>
    </div>
  );
}
