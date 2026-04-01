"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { productsApi } from "@/lib/api/products";
import { PlanCreate } from "@/lib/api/products";
import { Plan } from "@/lib/api/types/catalog";
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
import { Loader2, Trash2 } from "lucide-react";

interface PlanManagerProps {
  isOpen: boolean;
  onClose: () => void;
  productId: string;
  plan?: Plan;
}

export function PlanManager({ isOpen, onClose, productId, plan }: PlanManagerProps) {
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isEditing = !!plan;

  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    defaultValues: {
      name: plan?.name || "",
      description: plan?.description || "",
      company_id: plan?.company_id || "",
    }
  });

  const createMutation = useMutation({
    mutationFn: (data: PlanCreate) => productsApi.createPlan(productId, data),
    onSuccess: () => {
      toast.success("Plan creado exitosamente");
      queryClient.invalidateQueries({ queryKey: ["products"] });
      reset();
      onClose();
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Error al crear plan");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: any) => productsApi.updatePlan(plan!.id, data),
    onSuccess: () => {
      toast.success("Plan actualizado exitosamente");
      queryClient.invalidateQueries({ queryKey: ["products"] });
      reset();
      onClose();
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Error al actualizar plan");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => productsApi.deletePlan(plan!.id),
    onSuccess: () => {
      toast.success("Plan eliminado exitosamente");
      queryClient.invalidateQueries({ queryKey: ["products"] });
      onClose();
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Error al eliminar plan");
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

  const handleDelete = async () => {
    if (confirm("¿Estás seguro de que deseas eliminar este plan?")) {
      await deleteMutation.mutateAsync();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? "Editar Plan" : "Crear Nuevo Plan"}
          </DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Modifica los detalles del plan comercial"
              : "Define un nuevo plan dentro del producto"}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="plan-name">Nombre del Plan *</Label>
            <Input
              id="plan-name"
              placeholder="ej. Plan Familiar Senior"
              {...register("name", { required: "El nombre es requerido" })}
              disabled={isSubmitting}
              className="h-10"
            />
            {errors.name && (
              <p className="text-sm text-red-500">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="plan-description">Descripción</Label>
            <textarea
              id="plan-description"
              placeholder="Descripción del plan"
              {...register("description")}
              disabled={isSubmitting}
              rows={3}
              className="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none disabled:bg-neutral-50"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="company-id">ID de Empresa (Opcional)</Label>
            <Input
              id="company-id"
              placeholder="UUID de la empresa propietaria"
              {...register("company_id")}
              disabled={isSubmitting}
              className="h-10"
            />
          </div>

          <DialogFooter className="flex items-center justify-between">
            <div>
              {isEditing && (
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  onClick={handleDelete}
                  disabled={isSubmitting || deleteMutation.isPending}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Eliminar
                </Button>
              )}
            </div>
            <div className="flex gap-2">
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
                {isEditing ? "Actualizar" : "Crear"} Plan
              </Button>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
