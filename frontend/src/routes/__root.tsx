import { Outlet, createRootRoute } from "@tanstack/react-router";
import { AllAuthProvider } from "../services/auth";
import { StrictMode } from "react";
import { Theme } from "@seisveinte/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  return (
    <StrictMode>
      <Theme>
        <QueryClientProvider client={queryClient}>
          <AllAuthProvider>
            <Outlet />
          </AllAuthProvider>
        </QueryClientProvider>
      </Theme>
    </StrictMode>
  );
}
