export interface Note {
  id: number;
  title: string;
  content: string;
  version: number;
  tags: string[];
  created_at?: string | null;
  updated_at?: string | null;
}

export interface NoteList {
  items: Note[];
  total: number;
  skip: number;
  limit: number;
}

export interface NoteVersion {
  _id?: string;
  document_id: number;
  title?: string;
  content: string;
  version: number;
  timestamp: string;
}
