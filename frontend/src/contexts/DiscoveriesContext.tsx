import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { listDiscoveries } from '@/services/api/conflictDetector';

interface DiscoveriesContextType {
  pendingCount: number;
  refreshPendingCount: () => Promise<void>;
  setPendingCount: (count: number) => void;
}

const DiscoveriesContext = createContext<DiscoveriesContextType | undefined>(undefined);

export function DiscoveriesProvider({ children }: { children: ReactNode }) {
  const [pendingCount, setPendingCount] = useState<number>(0);

  const fetchPendingCount = async () => {
    try {
      const discoveries = await listDiscoveries();
      setPendingCount(discoveries.length);
    } catch (error) {
      console.error('Error fetching pending discoveries:', error);
    }
  };

  useEffect(() => {
    fetchPendingCount();
    // Refresh every 30 seconds as backup
    const interval = setInterval(fetchPendingCount, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <DiscoveriesContext.Provider value={{ pendingCount, refreshPendingCount: fetchPendingCount, setPendingCount }}>
      {children}
    </DiscoveriesContext.Provider>
  );
}

export function useDiscoveries() {
  const context = useContext(DiscoveriesContext);
  if (context === undefined) {
    throw new Error('useDiscoveries must be used within a DiscoveriesProvider');
  }
  return context;
}
