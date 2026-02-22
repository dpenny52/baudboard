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
}

export interface Column {
    id: number;
    title: string;
    card_ids: number[];
}

export interface Board {
    id: number;
    title: string;
    column_ids: number[];
}

export interface BoardDetail {
    id: number;
    title: string;
    columns: Column[];
    cards: Card[];
}