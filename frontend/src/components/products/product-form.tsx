"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { productsApi } from "@/lib/api/products";
import { ProductCreate } from "@/lib/api/products";
import { Product } from "@/lib/api/types/catalog";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Plus, X } from "lucide-react";

interface ProductFormProps {
  isOpen: boolean;
  onClose: () => void;
  product?: Product;
}

export function ProductForm({ isOpen, onClose, product }: ProductFormProps) {
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isEditing = !!product;

  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    defaultValues: {
      name: product?.name || "",
      description: product?.description || "",
      product_type: product?.product_type || "repatriation",
    }
  });

  const createMutation = useMutation({
    mutationFn: (data: ProductCreate) => productsApi.create(data),
    onSuccess: () => {
      toast.success("Producto creado exitosamente");
      queryClient.invalidateQueries({ queryKey: ["products"] });
      reset();
      onClose();
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Error al crear producto");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: any) => productsApi.update(product!.id, data),
    onSuccess: () => {
      toast.success("Producto actualizado exitosamente");
      queryClient.invalidateQueries({ queryKey: ["products"] });
      reset();
      onClose();
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Error al actualizar producto");
    },
  });

  const onSubmit = async (data: any) => {
    setIsSubmitting(true);
    try {
      if (isEditing) {
        await updateMutation.mutateAsync(data);
      } else {
        await createMutation.mutateAsync(data);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? "Editar Producto" : "Crear Nuevo Producto"}
          </DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Modifica los detalles del producto actuarial"
              : "Define un nuevo producto con su tipo y descripción"}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name">Nombre del Producto *</Label>
            <Input
              id="name"
              placeholder="ej. Repatriación Internacional"
              {...register("name", { required: "El nombre es requerido" })}
              disabled={isSubmitting}
              className="h-10"
            />
            {errors.name && (
              <p className="text-sm text-red-500">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="product_type">Tipo de Producto *</Label>
            <Input
              id="product_type"
              placeholder="ej. repatriation"
              {...register("product_type", {
                required: "El tipo de producto es requerido",
              })}
              disabled={isSubmitting}
              className="h-10"
            />
            {errors.product_type && (
              <p className="text-sm text-red-500">{errors.product_type.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Descripción</Label>
            <textarea
              id="description"
              placeholder="Descripción detallada del producto"
              {...register("description")}
              disabled={isSubmitting}
              rows={4}
              className="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none disabled:bg-neutral-50"
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-primary-500 hover:bg-primary-600"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              {isEditing ? "Actualizar" : "Crear"} Producto
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
