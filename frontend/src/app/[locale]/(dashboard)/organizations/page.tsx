"use client";

import { useCompanies } from "@/hooks/use-organizations";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Plus,
  MoreVertical,
  Building2,
  Mail,
  ExternalLink,
  ChevronRight,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Link } from "@/navigation";

export default function OrganizationsPage() {
  const { data: companies, isLoading } = useCompanies();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[var(--color-neutral-900)] tracking-tight">
            Organizaciones
          </h1>
          <p className="text-[var(--color-neutral-500)] mt-1">
            Gestiona las aseguradoras y sus unidades de negocio
          </p>
        </div>
        <Button
          asChild
          className="bg-[var(--color-primary-500)] hover:bg-[var(--color-primary-600)] text-white shadow-lg shadow-primary-500/20"
        >
          <Link href="/organizations/new">
            <Plus className="w-5 h-5 mr-2" />
            Nueva Empresa
          </Link>
        </Button>
      </div>

      <GlassCard className="overflow-hidden border-none shadow-glass">
        <Table>
          <TableHeader className="bg-[var(--color-neutral-50)]/50">
            <TableRow className="hover:bg-transparent border-none">
              <TableHead className="w-[400px]">Empresa</TableHead>
              <TableHead>Tax ID</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead>Fecha Creación</TableHead>
              <TableHead className="text-right">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Skeleton className="w-10 h-10 rounded-lg" />
                      <div className="space-y-1">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-48" />
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-24" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-6 w-16 rounded-full" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-24" />
                  </TableCell>
                  <TableCell className="text-right">
                    <Skeleton className="h-8 w-8 ml-auto rounded-md" />
                  </TableCell>
                </TableRow>
              ))
            ) : companies?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-64 text-center">
                  <div className="flex flex-col items-center justify-center text-[var(--color-neutral-400)]">
                    <Building2 className="w-12 h-12 mb-4 opacity-20" />
                    <p>No se encontraron empresas</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              companies?.map((company) => (
                <TableRow
                  key={company.id}
                  className="group hover:bg-[var(--color-primary-50)]/30 transition-colors border-b border-[var(--color-neutral-100)]"
                >
                  <TableCell className="py-4">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-xl bg-white border border-[var(--color-neutral-200)] flex items-center justify-center text-[var(--color-primary-500)] shadow-sm group-hover:scale-110 transition-transform">
                        <Building2 className="w-5 h-5" />
                      </div>
                      <div className="flex flex-col">
                        <span className="font-bold text-[var(--color-neutral-900)]">
                          {company.name}
                        </span>
                        <div className="flex items-center gap-1.5 text-xs text-[var(--color-neutral-400)]">
                          <Mail className="w-3 h-3" />
                          {company.email}
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="font-mono text-xs text-[var(--color-neutral-500)]">
                    {company.tax_id}
                  </TableCell>
                  <TableCell>
                    <Badge
                      className={
                        company.is_active
                          ? "bg-green-100 text-green-700 hover:bg-green-100 border-none px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-100 border-none px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider"
                      }
                    >
                      {company.is_active ? "Activa" : "Inactiva"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-[var(--color-neutral-500)]">
                    {new Date(company.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        asChild
                        className="opacity-0 group-hover:opacity-100 transition-opacity text-[var(--color-primary-500)] hover:text-[var(--color-primary-600)] hover:bg-white"
                      >
                        <Link href={`/organizations/${company.id}`}>
                          Ver Detalle
                          <ChevronRight className="w-4 h-4 ml-1" />
                        </Link>
                      </Button>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 rounded-lg hover:bg-white"
                          >
                            <MoreVertical className="w-4 h-4 text-[var(--color-neutral-400)]" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent
                          align="end"
                          className="w-48 rounded-xl border-[var(--color-neutral-200)] shadow-lg"
                        >
                          <DropdownMenuItem className="py-2.5 rounded-lg focus:bg-[var(--color-primary-50)] cursor-pointer">
                            <ExternalLink className="w-4 h-4 mr-2" />
                            Editar Empresa
                          </DropdownMenuItem>
                          <DropdownMenuItem className="py-2.5 rounded-lg focus:bg-red-50 text-red-600 cursor-pointer">
                            Desactivar
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </GlassCard>
    </div>
  );
}
