"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Plus, Package, Trash2, Edit2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { productsApi } from "@/lib/api/products";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { ProductDeepView } from "@/components/products/product-deep-view";
import { ProductForm } from "@/components/products/product-form";
import { Product } from "@/lib/api/types/catalog";
import { toast } from "sonner";

export default function ProductsPage() {
  const t = useTranslations("dashboard");
  const [isProductFormOpen, setIsProductFormOpen] = useState(false);
  const [selectedProductForEdit, setSelectedProductForEdit] = useState<Product | undefined>();

  const { data: products, isLoading, refetch } = useQuery<Product[]>({
    queryKey: ["products"],
    queryFn: () => productsApi.list(true),
  });

  const handleCreateProduct = () => {
    setSelectedProductForEdit(undefined);
    setIsProductFormOpen(true);
  };

  const handleEditProduct = (product: Product) => {
    setSelectedProductForEdit(product);
    setIsProductFormOpen(true);
  };

  const handleDeleteProduct = async (productId: string) => {
    if (confirm("¿Estás seguro de que deseas eliminar este producto y toda su jerarquía?")) {
      try {
        await productsApi.delete(productId);
        toast.success("Producto eliminado exitosamente");
        refetch();
      } catch (error: any) {
        toast.error(error?.response?.data?.detail || "Error al eliminar producto");
      }
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <ProductForm
        isOpen={isProductFormOpen}
        onClose={() => {
          setIsProductFormOpen(false);
          setSelectedProductForEdit(undefined);
        }}
        product={selectedProductForEdit}
      />

      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-primary-50 rounded-2xl flex items-center justify-center text-primary-500 shadow-sm border border-primary-100 flex-shrink-0">
            <Package className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-neutral-900 tracking-tight">
              Configuraciones Actuariales
            </h1>
            <p className="text-neutral-500 mt-1">
              Catálogo técnico de 5 niveles para la gestión de productos y planes de seguro
            </p>
          </div>
        </div>
        <Button
          onClick={handleCreateProduct}
          className="bg-primary-500 hover:bg-primary-600 text-white shadow-xl shadow-primary-500/20 h-12 px-6 font-bold transition-all hover:scale-105 active:scale-95"
        >
          <Plus className="w-5 h-5 mr-2" />
          Ingeniería de Producto
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-12">
        {isLoading ? (
          Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="space-y-6">
              <Skeleton className="h-10 w-1/4 rounded-xl" />
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Skeleton className="h-64 w-full rounded-3xl" />
                <Skeleton className="h-64 w-full rounded-3xl" />
                <Skeleton className="h-64 w-full rounded-3xl" />
              </div>
            </div>
          ))
        ) : products?.length ? (
          products.map((product) => (
            <div key={product.id} className="space-y-6">
              <div className="flex items-center justify-between group">
                <div className="flex items-center gap-3">
                  <h2 className="text-2xl font-bold text-neutral-900 group-hover:text-primary-600 transition-colors">
                    {product.name}
                  </h2>
                  <Badge className="bg-neutral-100 text-neutral-500 hover:bg-neutral-100 border-none px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider">
                    {product.product_type}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEditProduct(product)}
                    className="text-neutral-500 hover:text-neutral-700"
                  >
                    <Edit2 className="w-4 h-4 mr-1" />
                    Editar
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteProduct(product.id)}
                    className="text-neutral-500 hover:text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <ProductDeepView product={product} />

              <div className="h-px bg-neutral-200/50 w-full mt-12 mb-8 last:hidden" />
            </div>
          ))
        ) : (
          <GlassCard className="p-20 text-center flex flex-col items-center justify-center bg-white/40 border-dashed border-2 border-neutral-200 shadow-none">
            <div className="w-20 h-20 bg-neutral-100 rounded-3xl flex items-center justify-center mb-6">
              <Package className="w-10 h-10 text-neutral-300" />
            </div>
            <h3 className="text-2xl font-bold text-neutral-900">Catálogo vacío</h3>
            <p className="text-neutral-500 max-w-sm mt-3 text-lg leading-relaxed">
              No hay productos configurados en la jerarquía técnica actual.
            </p>
            <Button
              onClick={handleCreateProduct}
              className="mt-8 bg-primary-500 hover:bg-primary-600 text-white font-bold h-12 px-8 shadow-lg shadow-primary-500/20"
            >
              Configurar Primer Producto
            </Button>
          </GlassCard>
        )}
      </div>
    </div>
  );
}
