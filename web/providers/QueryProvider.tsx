'use client';

/**
 * Provider React Query pour le data fetching.
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Données financières : stale après 5 minutes
            staleTime: 5 * 60 * 1000,
            // Retry 2 fois en cas d'erreur
            retry: 2,
            // Pas de refetch automatique au focus (données historiques)
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
