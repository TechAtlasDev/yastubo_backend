"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { LayoutGrid, Save, Loader2 } from "lucide-react";

import { organizationsApi } from "@/lib/api/organizations";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

const unitSchema = z.object({
  name: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
  code: z.string().min(2, "El código debe tener al menos 2 caracteres"),
  type: z.enum(["office", "agency"]),
});

type UnitFormValues = z.infer<typeof unitSchema>;

interface CreateUnitModalProps {
  companyId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function CreateUnitModal({ companyId, isOpen, onClose }: CreateUnitModalProps) {
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<UnitFormValues>({
    resolver: zodResolver(unitSchema),
    defaultValues: {
      name: "",
      code: "",
      type: "office",
    },
  });

  const mutation = useMutation({
    mutationFn: (data: UnitFormValues) => 
      organizationsApi.createBusinessUnit(companyId, data),
    onSuccess: () => {
      toast.success("Unidad de negocio creada exitosamente");
      queryClient.invalidateQueries({ queryKey: ["business-units", companyId] });
      form.reset();
      onClose();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Error al crear la unidad");
    },
    onSettled: () => {
      setIsSubmitting(false);
    }
  });

  const onSubmit = (data: UnitFormValues) => {
    setIsSubmitting(true);
    mutation.mutate(data);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center text-primary-500 mb-4">
            <LayoutGrid className="w-6 h-6" />
          </div>
          <DialogTitle className="text-2xl">Nueva Unidad</DialogTitle>
          <DialogDescription>
            Registra una oficina o agencia bajo esta empresa para autorizar operaciones.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 py-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nombre de la Unidad</FormLabel>
                  <FormControl>
                    <Input placeholder="Ej. Agencia Central Madrid" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Código Interno</FormLabel>
                  <FormControl>
                    <Input placeholder="Ej. MAD-001" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="type"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tipo de Unidad</FormLabel>
                  <FormControl>
                    <select
                      {...field}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <option value="office">Oficina (Principal)</option>
                      <option value="agency">Agencia (Punto de Venta)</option>
                    </select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter className="pt-6">
              <Button type="button" variant="ghost" onClick={onClose} disabled={isSubmitting}>
                Cancelar
              </Button>
              <Button type="submit" disabled={isSubmitting} className="bg-primary-500 hover:bg-primary-600 text-white shadow-lg shadow-primary-500/20">
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creando...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Guardar Unidad
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
