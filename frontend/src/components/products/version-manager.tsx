"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { productsApi } from "@/lib/api/products";
import { PlanVersionCreate } from "@/lib/api/products";
import { CurrencyCode } from "@/lib/api/types/catalog";
import { PlanVersion } from "@/lib/api/types/catalog";
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
import { Loader2 } from "lucide-react";

interface VersionManagerProps {
  isOpen: boolean;
  onClose: () => void;
  planId: string;
  version?: PlanVersion;
}

const CURRENCIES: CurrencyCode[] = ["USD", "EUR", "MXN", "COP", "GBP"];

export function VersionManager({ isOpen, onClose, planId, version }: VersionManagerProps) {
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isEditing = !!version;

  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    defaultValues: {
      cost_price: version?.cost_price || 0,
      public_price: version?.public_price || 0,
      currency: version?.currency || "USD",
      max_entry_age: version?.max_entry_age || 75,
      max_renewal_age: version?.max_renewal_age || 85,
      wtime_suicide: version?.wtime_suicide || 90,
      wtime_accident: version?.wtime_accident || 14,
      wtime_preexisting: version?.wtime_preexisting || 180,
    }
  });

  const createMutation = useMutation({
    mutationFn: (data: PlanVersionCreate) => productsApi.createVersion(planId, data),
    onSuccess: () => {
      toast.success("Versión del plan creada exitosamente");
      queryClient.invalidateQueries({ queryKey: ["products"] });
      reset();
      onClose();
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Error al crear versión");
    },
  });

  const onSubmit = async (data: any) => {
    setIsSubmitting(true);
    try {
      // Convert string numbers to actual numbers
      const payload = {
        ...data,
        cost_price: parseFloat(data.cost_price),
        public_price: parseFloat(data.public_price),
        max_entry_age: parseInt(data.max_entry_age),
        max_renewal_age: parseInt(data.max_renewal_age),
        wtime_suicide: parseInt(data.wtime_suicide),
        wtime_accident: parseInt(data.wtime_accident),
        wtime_preexisting: parseInt(data.wtime_preexisting),
      };
      await createMutation.mutateAsync(payload);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? "Editar Versión" : "Crear Nueva Versión"}
          </DialogTitle>
          <DialogDescription>
            Configura los parámetros actuariales y económicos de la versión del plan
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Precios */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="cost-price">Precio de Costo *</Label>
              <Input
                id="cost-price"
                type="number"
                step="0.01"
                placeholder="0.00"
                {...register("cost_price", { required: "Requerido" })}
                disabled={isSubmitting}
                className="h-10"
              />
              {errors.cost_price && (
                <p className="text-sm text-red-500">{errors.cost_price.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="public-price">Precio Público *</Label>
              <Input
                id="public-price"
                type="number"
                step="0.01"
                placeholder="0.00"
                {...register("public_price", { required: "Requerido" })}
                disabled={isSubmitting}
                className="h-10"
              />
              {errors.public_price && (
                <p className="text-sm text-red-500">{errors.public_price.message}</p>
              )}
            </div>
          </div>

          {/* Moneda y Edades */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="currency">Moneda *</Label>
              <select
                id="currency"
                {...register("currency", { required: "Requerido" })}
                disabled={isSubmitting}
                className="w-full h-10 px-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {CURRENCIES.map((curr) => (
                  <option key={curr} value={curr}>
                    {curr}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="max-entry-age">Edad Máx. Entrada *</Label>
              <Input
                id="max-entry-age"
                type="number"
                placeholder="75"
                {...register("max_entry_age", { required: "Requerido" })}
                disabled={isSubmitting}
                className="h-10"
              />
            </div>
          </div>

          {/* Edad Máxima Renovación */}
          <div className="space-y-2">
            <Label htmlFor="max-renewal-age">Edad Máx. Renovación *</Label>
            <Input
              id="max-renewal-age"
              type="number"
              placeholder="85"
              {...register("max_renewal_age", { required: "Requerido" })}
              disabled={isSubmitting}
              className="h-10"
            />
          </div>

          {/* Tiempos de Carencia */}
          <div className="border-t pt-4">
            <h3 className="font-semibold text-neutral-900 mb-4">Tiempos de Carencia (días)</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="wtime-suicide">Suicidio *</Label>
                <Input
                  id="wtime-suicide"
                  type="number"
                  placeholder="90"
                  {...register("wtime_suicide", { required: "Requerido" })}
                  disabled={isSubmitting}
                  className="h-10"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="wtime-accident">Accidente *</Label>
                <Input
                  id="wtime-accident"
                  type="number"
                  placeholder="14"
                  {...register("wtime_accident", { required: "Requerido" })}
                  disabled={isSubmitting}
                  className="h-10"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="wtime-preexisting">Preexistencias *</Label>
                <Input
                  id="wtime-preexisting"
                  type="number"
                  placeholder="180"
                  {...register("wtime_preexisting", { required: "Requerido" })}
                  disabled={isSubmitting}
                  className="h-10"
                />
              </div>
            </div>
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
              {isEditing ? "Actualizar" : "Crear"} Versión
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
