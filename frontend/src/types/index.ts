export type Priority = 'none' | 'low' | 'medium' | 'high' | 'urgent';

export interface Label {
  id: number;
  name: string;
  color: string;
}

export interface Card {
  id: number;
  title: string;
  description?: string;
  priority: Priority;
  labels: Label[];
  column_id: number;
  position: number;
}

export interface Column {
  id: number;
  title: string;
  cards: Card[];
}

export interface Board {
  id: number;
  title: string;
  columns: Column[];
}

export interface BoardDetail extends Board {
  cards: Card[];
}