"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useTranslations } from "next-intl";
import { useRouter, Link } from "@/navigation";
import { authApi } from "@/lib/api/auth";
import { useAuthStore } from "@/lib/store/auth.store";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Loader2, LogIn } from "lucide-react";

import Cookies from "js-cookie";

const loginSchema = z.object({
  email: z.string().email({ message: "Email inválido" }),
  password: z.string().min(6, { message: "Mínimo 6 caracteres" }),
});

export function LoginForm() {
  const t = useTranslations("auth");
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  async function onSubmit(values: z.infer<typeof loginSchema>) {
    setIsLoading(true);
    try {
      const data = await authApi.login(values);
      // Backend returns TokenResponse { access_token, refresh_token, ... }
      setAuth(data.access_token, null);
      
      // Set cookie for middleware
      Cookies.set("auth_token", data.access_token, { expires: 1 }); // 1 day

      toast.success("Bienvenido de nuevo");
      router.push("/"); // Redirect to dashboard
    } catch (error: any) {
      console.error(error);
      toast.error(
        error.response?.data?.detail || "Error al iniciar sesión. Verifique sus credenciales."
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <GlassCard className="w-full max-w-md p-8">
      <div className="flex flex-col items-center mb-8">
        <div className="w-12 h-12 bg-[var(--color-primary-500)] rounded-xl flex items-center justify-center mb-4 shadow-lg shadow-primary-500/20">
          <LogIn className="text-white w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-[var(--color-neutral-900)]">
          {t("login")}
        </h1>
        <p className="text-[var(--color-neutral-500)] text-sm">
          Yastubo Admin Dashboard
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input
                    placeholder="admin@yastubo.com"
                    {...field}
                    className="bg-white/50 border-[var(--color-neutral-200)] focus:border-[var(--color-primary-500)]"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Contraseña</FormLabel>
                <FormControl>
                  <Input
                    type="password"
                    placeholder="••••••••"
                    {...field}
                    className="bg-white/50 border-[var(--color-neutral-200)] focus:border-[var(--color-primary-500)]"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button
            type="submit"
            disabled={isLoading}
            className="w-full bg-[var(--color-primary-500)] hover:bg-[var(--color-primary-600)] text-white h-11"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Iniciando sesión...
              </>
            ) : (
              t("login")
            )}
          </Button>
        </form>
      </Form>
      <div className="mt-6 text-center text-sm">
        <p className="text-[var(--color-neutral-500)]">
          {t("dont_have_account")}{" "}
          <Link href="/register" className="font-semibold text-primary hover:underline">
            {t("register_link")}
          </Link>
        </p>
      </div>
    </GlassCard>
  );
}
