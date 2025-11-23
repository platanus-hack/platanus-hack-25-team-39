import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Utilidades para proyectos vistos recientemente
const RECENTLY_VIEWED_KEY = 'recently_viewed_discoveries';
const MAX_RECENT_ITEMS = 10;

export interface RecentlyViewedDiscovery {
  id: number;
  proyecto_id: string;
  proyecto_titulo: string;
  cantidad_impactos: number;
  max_nivel_relevancia: number;
  estado: string;
  viewedAt: string;
}

export function addRecentlyViewedDiscovery(discovery: {
  id: number;
  proyecto_id: string;
  proyecto_titulo: string;
  cantidad_impactos: number;
  max_nivel_relevancia: number;
  estado: string;
}): void {
  try {
    const existing = getRecentlyViewedDiscoveries();
    
    // Remover si ya existe (para evitar duplicados)
    const filtered = existing.filter(item => item.id !== discovery.id);
    
    // Agregar al inicio con timestamp actual
    const newItem: RecentlyViewedDiscovery = {
      ...discovery,
      viewedAt: new Date().toISOString(),
    };
    
    const updated = [newItem, ...filtered].slice(0, MAX_RECENT_ITEMS);
    
    localStorage.setItem(RECENTLY_VIEWED_KEY, JSON.stringify(updated));
  } catch (error) {
    console.error('Error al guardar proyecto visto recientemente:', error);
  }
}

export function getRecentlyViewedDiscoveries(): RecentlyViewedDiscovery[] {
  try {
    const stored = localStorage.getItem(RECENTLY_VIEWED_KEY);
    if (!stored) return [];
    
    const items = JSON.parse(stored) as RecentlyViewedDiscovery[];
    // Validar que los items tengan la estructura correcta
    return items.filter(item => 
      item.id && 
      item.proyecto_id && 
      item.proyecto_titulo && 
      item.viewedAt
    );
  } catch (error) {
    console.error('Error al leer proyectos vistos recientemente:', error);
    return [];
  }
}

export function removeRecentlyViewedDiscovery(discoveryId: number): void {
  try {
    const existing = getRecentlyViewedDiscoveries();
    const filtered = existing.filter(item => item.id !== discoveryId);
    localStorage.setItem(RECENTLY_VIEWED_KEY, JSON.stringify(filtered));
  } catch (error) {
    console.error('Error al eliminar proyecto visto recientemente:', error);
  }
}
