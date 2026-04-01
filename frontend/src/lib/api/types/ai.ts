export interface KnowledgeDocument {
  id: string;
  company_id: string;
  title: string;
  content: string;
  source_url?: string;
  metadata_json?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CreateKnowledgeDocument {
  title: string;
  content: string;
  source_url?: string;
  metadata_json?: Record<string, any>;
}

export interface ChatConversation {
  id: string;
  session_id: string;
  title?: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}
