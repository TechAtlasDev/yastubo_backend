"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "@/navigation";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Building2, Save, X, Loader2, Image as ImageIcon } from "lucide-react";

import { organizationsApi } from "@/lib/api/organizations";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

const companySchema = z.object({
  name: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
  tax_id: z.string().min(5, "Tax ID inválido"),
  email: z.string().email("Email inválido").optional().or(z.literal("")),
  phone: z.string().optional().or(z.literal("")),
  address: z.string().optional().or(z.literal("")),
});

type CompanyFormValues = z.infer<typeof companySchema>;

export default function NewCompanyPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const t = useTranslations("auth"); // Reuse translations where possible or add specific ones
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<CompanyFormValues>({
    resolver: zodResolver(companySchema),
    defaultValues: {
      name: "",
      tax_id: "",
      email: "",
      phone: "",
      address: "",
    },
  });

  const mutation = useMutation({
    mutationFn: organizationsApi.createCompany,
    onSuccess: () => {
      toast.success("Empresa creada exitosamente");
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      router.push("/organizations");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Error al crear la empresa");
      setIsSubmitting(false);
    },
  });

  const onSubmit = (data: CompanyFormValues) => {
    setIsSubmitting(true);
    mutation.mutate(data);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-primary-50 rounded-2xl flex items-center justify-center text-primary-500 shadow-sm border border-primary-100">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-neutral-900">Nueva Empresa</h1>
            <p className="text-neutral-500">Registra una nueva aseguradora en la plataforma</p>
          </div>
        </div>
        <Button variant="ghost" onClick={() => router.back()} className="text-neutral-500">
          <X className="w-5 h-5 mr-2" />
          Cancelar
        </Button>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-8">
            <GlassCard className="p-8 border-none shadow-glass bg-white/70">
              <h3 className="text-lg font-bold text-neutral-900 border-b pb-4 mb-6">Información General</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem className="md:col-span-2">
                      <FormLabel>Nombre de la Empresa</FormLabel>
                      <FormControl>
                        <Input placeholder="Ej. Seguros Atlas S.A." {...field} className="bg-white/50 border-neutral-200 focus:border-primary-500 h-11" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="tax_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Tax ID / NIT</FormLabel>
                      <FormControl>
                        <Input placeholder="123456789-0" {...field} className="bg-white/50 border-neutral-200 focus:border-primary-500 h-11" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                 <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email Corporativo</FormLabel>
                      <FormControl>
                        <Input placeholder="contacto@empresa.com" {...field} className="bg-white/50 border-neutral-200 focus:border-primary-500 h-11" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </GlassCard>

            <GlassCard className="p-8 border-none shadow-glass bg-white/70">
              <h3 className="text-lg font-bold text-neutral-900 border-b pb-4 mb-6">Contacto y Ubicación</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                 <FormField
                  control={form.control}
                  name="phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Teléfono</FormLabel>
                      <FormControl>
                        <Input placeholder="+1..." {...field} className="bg-white/50 border-neutral-200 focus:border-primary-500 h-11" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="address"
                  render={({ field }) => (
                    <FormItem className="md:col-span-2">
                      <FormLabel>Dirección Fiscal</FormLabel>
                      <FormControl>
                        <Input placeholder="Calle 123 # 45-67..." {...field} className="bg-white/50 border-neutral-200 focus:border-primary-500 h-11" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </GlassCard>
          </div>

          <div className="space-y-8">
            <GlassCard className="p-8 border-none shadow-glass bg-white/70">
               <h3 className="text-lg font-bold text-neutral-900 border-b pb-4 mb-6">Branding</h3>
               <div className="space-y-6">
                    <div className="aspect-square rounded-2xl border-2 border-dashed border-neutral-200 flex flex-col items-center justify-center bg-neutral-50/50 group hover:border-primary-300 transition-colors cursor-pointer">
                        <ImageIcon className="w-8 h-8 text-neutral-300 mb-2 group-hover:text-primary-400" />
                        <span className="text-xs font-medium text-neutral-400 group-hover:text-primary-500 text-center px-4">Haz clic para subir el logo corporativo</span>
                    </div>
                    <p className="text-[10px] leading-tight text-neutral-500">
                        Formatos soportados: PNG, JPG, SVG. Máximo 2MB.
                    </p>
               </div>
            </GlassCard>

            <div className="space-y-4">
                <Button 
                    type="submit" 
                    disabled={isSubmitting}
                    className="w-full bg-primary-500 hover:bg-primary-600 text-white h-14 shadow-lg shadow-primary-500/20 text-lg font-bold"
                >
                    {isSubmitting ? (
                        <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Guardando...
                        </>
                    ) : (
                        <>
                            <Save className="w-5 h-5 mr-2" />
                            Registrar Empresa
                        </>
                    )}
                </Button>
                <p className="text-[10px] text-center text-neutral-400 px-4">
                    Al registrar, la empresa quedará en estado "Draft" hasta que se configure al menos una unidad de negocio.
                </p>
            </div>
          </div>
        </form>
      </Form>
    </div>
  );
}
