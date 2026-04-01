import { cn } from "@/lib/utils";
import React from "react";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  blur?: "sm" | "md" | "lg";
}

export function GlassCard({ className, blur = "md", ...props }: GlassCardProps) {
  return (
    <div
      className={cn(
        "rounded-[var(--radius-lg)]",
        "bg-[var(--glass-background)]",
        "border border-[var(--glass-border)]",
        "shadow-[var(--shadow-glass)]",
        blur === "sm" && "backdrop-blur-sm",
        blur === "md" && "backdrop-blur-md",
        blur === "lg" && "backdrop-blur-lg",
        "transition-all duration-[var(--transition-normal)]",
        className
      )}
      {...props}
    />
  );
}
