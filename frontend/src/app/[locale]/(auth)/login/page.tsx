import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-[var(--color-neutral-50)]">
      <LoginForm />
    </main>
  );
}
