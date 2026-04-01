"use client";

import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { aiApi } from "@/lib/api/modules";
import { 
  Send, 
  Bot, 
  User, 
  Loader2, 
  Sparkles, 
  Maximize2, 
  Minimize2, 
  X,
  MessageSquare,
  Eraser,
  ShieldCheck
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function AIChatAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: 'assistant', 
      content: "¡Hola! Soy el asistente inteligente de Yastubo. Puedo ayudarte con dudas sobre productos, planes o procesos técnicos. ¿En qué puedo apoyarte hoy?",
      timestamp: new Date()
    }
  ]);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  const chatMutation = useMutation({
    mutationFn: (msg: string) => aiApi.chat(msg, sessionId),
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      }]);
    },
    onError: (error: any) => {
      toast.error("Error al conectar con la IA: " + (error.message || "Servicio no disponible"));
      setMessages(prev => prev.slice(0, -1)); // Remove the waiting message or handle error
    }
  });

  const handleSend = () => {
    if (!input.trim() || chatMutation.isPending) return;

    const userMessage = input.trim();
    setInput("");
    
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    }]);

    chatMutation.mutate(userMessage);
  };

  if (!isOpen) {
    return (
      <Button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-primary-600 hover:bg-primary-700 text-white shadow-2xl shadow-primary-500/40 animate-in zoom-in duration-300 z-50 flex items-center justify-center border-4 border-white"
      >
        <MessageSquare className="w-6 h-6" />
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-success-500 rounded-full border-2 border-white shadow-sm" />
      </Button>
    );
  }

  return (
    <Card 
      className={cn(
        "fixed z-50 transition-all duration-300 shadow-2xl border-none overflow-hidden bg-white flex flex-col",
        isMaximized 
          ? "top-6 right-6 bottom-6 left-6 md:left-[20%]" 
          : "bottom-6 right-6 w-[90vw] md:w-[450px] h-[600px] max-h-[85vh] rounded-3xl"
      )}
    >
      {/* Header */}
      <CardHeader className="p-4 bg-primary-600 text-white flex flex-row items-center justify-between space-y-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center backdrop-blur-md">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <CardTitle className="text-sm font-bold flex items-center gap-2">
              IA Assistant
              <Badge className="bg-success-400/20 text-success-50 text-[10px] border-none font-normal">RAG Context</Badge>
            </CardTitle>
            <div className="flex items-center gap-1.5 mt-0.5">
              <div className="w-1.5 h-1.5 rounded-full bg-success-400 animate-pulse" />
              <p className="text-[10px] text-primary-100 font-medium uppercase tracking-wider">Online</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-8 w-8 text-white hover:bg-white/10 rounded-lg"
            onClick={() => setIsMaximized(!isMaximized)}
          >
            {isMaximized ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </Button>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-8 w-8 text-white hover:bg-white/10 rounded-lg"
            onClick={() => setIsOpen(false)}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>

      {/* Messages Area */}
      <CardContent className="flex-1 overflow-hidden p-0 bg-neutral-50/50">
        <ScrollArea className="h-full px-4 py-6">
          <div className="space-y-6">
            {messages.map((msg, i) => (
              <div 
                key={i} 
                className={cn(
                  "flex items-start gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300",
                  msg.role === 'user' ? "flex-row-reverse" : "flex-row"
                )}
              >
                <div className={cn(
                  "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm",
                  msg.role === 'user' ? "bg-indigo-600 text-white" : "bg-white text-primary-600"
                )}>
                  {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
                <div className={cn(
                  "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm border",
                  msg.role === 'user' 
                    ? "bg-indigo-600 text-white border-indigo-500 rounded-tr-none" 
                    : "bg-white text-neutral-800 border-neutral-100 rounded-tl-none"
                )}>
                  {msg.content}
                  <div className={cn(
                    "text-[10px] mt-2 font-medium opacity-60",
                    msg.role === 'user' ? "text-white" : "text-neutral-500"
                  )}>
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            {chatMutation.isPending && (
              <div className="flex items-start gap-3 animate-pulse">
                <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center shadow-sm border border-neutral-100">
                  <Bot className="w-4 h-4 text-primary-600" />
                </div>
                <div className="bg-white border border-neutral-100 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
                  <div className="flex gap-1.5">
                    <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                    <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                    <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce" />
                  </div>
                </div>
              </div>
            )}
            <div ref={scrollRef} />
          </div>
        </ScrollArea>
      </CardContent>

      {/* Footer / Input */}
      <CardFooter className="p-4 bg-white border-t border-neutral-100">
        <form 
          className="w-full flex items-center gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
        >
          <div className="relative flex-1 group">
            <Input 
              placeholder="Escribe tu duda aquí..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="h-12 bg-neutral-50 border-neutral-200 rounded-2xl pl-4 pr-12 focus-visible:ring-primary-500/20 focus-visible:ring-offset-0 focus-visible:border-primary-500"
              disabled={chatMutation.isPending}
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 opacity-0 group-focus-within:opacity-100 transition-opacity">
               <Sparkles className="w-3.5 h-3.5 text-primary-400 animate-pulse" />
            </div>
          </div>
          <Button 
            type="submit"
            size="icon" 
            className="h-12 w-12 rounded-2xl bg-primary-600 hover:bg-primary-700 text-white flex-shrink-0 shadow-lg shadow-primary-600/20"
            disabled={!input.trim() || chatMutation.isPending}
          >
            {chatMutation.isPending ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5 ml-0.5" />
            )}
          </Button>
        </form>
      </CardFooter>

      {/* Hint Bar */}
      <div className="bg-neutral-50 px-4 py-2 border-t border-neutral-100 flex items-center justify-between">
         <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-3 h-3 text-neutral-400" />
            <span className="text-[10px] text-neutral-400 font-medium">Cumple con GDPR/Privacidad</span>
         </div>
         <button 
           onClick={() => {
             setMessages(prev => [prev[0]]);
             setSessionId(undefined);
             toast.info("Conversación reiniciada");
           }}
           className="text-[10px] text-neutral-400 hover:text-red-500 font-bold flex items-center gap-1 transition-colors"
         >
            <Eraser className="w-3 h-3" />
            LIMPIAR CHAT
         </button>
      </div>
    </Card>
  );
}
