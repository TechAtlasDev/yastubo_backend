"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { aiApi } from "@/lib/api/modules";
import { 
  FileText, 
  Upload, 
  Trash2, 
  ExternalLink, 
  Plus, 
  Search,
  BookOpen,
  Cpu,
  RefreshCcw,
  Sparkles,
  Loader2,
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function KnowledgeBasePage() {
  const [isUploading, setIsUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const queryClient = useQueryClient();

  const { data: documents, isLoading } = useQuery({
    queryKey: ["knowledge-base"],
    queryFn: () => aiApi.listKnowledge(),
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => aiApi.uploadPDF(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-base"] });
      toast.success("Documento procesado correctamente");
      setIsUploading(false);
    },
    onError: (error: any) => {
      toast.error(error.message || "Error al subir el documento");
      setIsUploading(false);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => aiApi.deleteDocument(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-base"] });
      toast.success("Documento eliminado");
    }
  });

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== "application/pdf") {
        toast.error("Solo se permiten archivos PDF");
        return;
      }
      setIsUploading(true);
      uploadMutation.mutate(file);
    }
  };

  const filteredDocs = documents?.filter(doc => 
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-neutral-900 flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-primary-200">
              <BookOpen className="w-6 h-6" />
            </div>
            Base de Conocimiento
          </h1>
          <p className="text-neutral-500 mt-2">
            Gestiona la documentación técnica para el motor de Inteligencia Artificial (RAG).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" className="h-10 border-neutral-200">
            <RefreshCcw className="w-4 h-4 mr-2" />
            Sincronizar
          </Button>
          <div className="relative">
            <input
              type="file"
              id="pdf-upload"
              className="hidden"
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={isUploading}
            />
            <Button 
                asChild
                className="h-10 bg-primary-600 hover:bg-primary-700 text-white shadow-md cursor-pointer"
            >
              <label htmlFor="pdf-upload">
                {isUploading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Upload className="w-4 h-4 mr-2" />
                )}
                Subir PDF
              </label>
            </Button>
          </div>
        </div>
      </div>

      {/* Stats / Status Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-none shadow-sm bg-indigo-50/50">
          <CardContent className="pt-6">
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="space-y-1">
                <p className="text-xs font-medium text-indigo-600 uppercase tracking-wider">Documentos Activos</p>
                <div className="text-2xl font-bold text-indigo-900">{documents?.length || 0}</div>
              </div>
              <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-sm">
                <FileText className="w-5 h-5 text-indigo-500" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-none shadow-sm bg-emerald-50/50">
          <CardContent className="pt-6">
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="space-y-1">
                <p className="text-xs font-medium text-emerald-600 uppercase tracking-wider">Motor Vectorial</p>
                <div className="text-sm font-bold text-emerald-900 flex items-center gap-1">
                  <Badge variant="outline" className="bg-white text-emerald-700 border-emerald-100">PGVector</Badge>
                  <span className="text-xs text-emerald-600 ml-1">v1.1</span>
                </div>
              </div>
              <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-sm">
                <Cpu className="w-5 h-5 text-emerald-500" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-none shadow-sm bg-amber-50/50">
          <CardContent className="pt-6">
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="space-y-1">
                <p className="text-xs font-medium text-amber-600 uppercase tracking-wider">RAG Status</p>
                <div className="text-sm font-bold text-amber-900 flex items-center gap-2">
                   <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                   Optimizado
                </div>
              </div>
              <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-sm">
                <Sparkles className="w-5 h-5 text-amber-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <Input 
            placeholder="Buscar en el conocimiento..." 
            className="pl-10 h-12 bg-white border-neutral-200 rounded-xl"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {isLoading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-48 rounded-2xl bg-neutral-100 animate-pulse" />
            ))
          ) : filteredDocs?.length === 0 ? (
            <div className="col-span-full py-12 flex flex-col items-center justify-center text-neutral-500 border-2 border-dashed border-neutral-200 rounded-3xl">
              <AlertCircle className="w-12 h-12 mb-4 text-neutral-300" />
              <p className="text-lg font-medium">No se encontraron documentos</p>
              <p className="text-sm">Sube tu primer PDF para entrenar a la IA.</p>
            </div>
          ) : (
            filteredDocs?.map((doc) => (
              <Card key={doc.id} className="group overflow-hidden border-none shadow-sm hover:shadow-md transition-all duration-300 rounded-2xl bg-white/70 border border-neutral-100/50">
                <CardHeader className="pb-3 flex flex-row items-start justify-between space-y-0">
                  <div className="space-y-1">
                    <CardTitle className="text-base font-bold text-neutral-900 line-clamp-1">
                      {doc.title}
                    </CardTitle>
                    <CardDescription className="text-xs font-mono uppercase tracking-tighter">
                      ID: {doc.id.split('-')[0]}...
                    </CardDescription>
                  </div>
                  <div className="w-8 h-8 rounded-lg bg-neutral-100 flex items-center justify-center text-neutral-500 group-hover:bg-primary-50 group-hover:text-primary-600 transition-colors">
                    <FileText className="w-4 h-4" />
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-neutral-600 line-clamp-3 leading-relaxed">
                    {doc.content}
                  </p>
                  
                  <div className="flex items-center gap-2 pt-2">
                    <Badge variant="secondary" className="text-[10px] bg-neutral-100 text-neutral-600 border-none">
                       {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : 'Reciente'}
                    </Badge>
                    {doc.source_url && (
                        <Badge variant="secondary" className="text-[10px] bg-blue-50 text-blue-600 border-none">
                            PDF Externo
                        </Badge>
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-4 gap-2 border-t border-neutral-50">
                    <Button variant="ghost" size="sm" className="h-8 text-neutral-500 hover:text-primary-600 hover:bg-primary-50 px-2">
                      <ExternalLink className="w-3 h-3 mr-1" />
                      Extraer
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => deleteMutation.mutate(doc.id)}
                      className="h-8 text-neutral-400 hover:text-red-600 hover:bg-red-50 px-2"
                    >
                      <Trash2 className="w-3 h-3 mr-1" />
                      Eliminar
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
