import type { Metadata } from "next";
import { Outfit, Fira_Code } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";
import { QueryProvider } from "@/providers/query-provider";
import { StripeProvider } from "@/providers/stripe-provider";
import { Toaster } from "sonner";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
});

const firaCode = Fira_Code({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "Yastubo Admin",
  description: "Dashboard de administración de Yastubo",
};

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  
  // Providing all messages to the client
  // side is the easiest way to get started
  let messages;
  try {
    messages = await getMessages();
    
    // Safety check: ensure messages is not an error object
    if (messages && typeof messages === 'object' && 'msg' in messages && 'loc' in messages) {
       console.error("Detected validation error in messages:", messages);
       messages = {}; 
    }
  } catch (error) {
    console.error("Error fetching messages:", error);
    messages = {};
  }

  return (
    <html lang={locale} className={`${outfit.variable} ${firaCode.variable}`}>
      <body className="min-h-screen font-sans bg-[var(--color-neutral-50)] text-[var(--color-neutral-900)]">
        <NextIntlClientProvider locale={locale} messages={messages}>
          <QueryProvider>
            <StripeProvider>
              {children}
            </StripeProvider>
            <Toaster position="top-right" closeButton richColors />
          </QueryProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
