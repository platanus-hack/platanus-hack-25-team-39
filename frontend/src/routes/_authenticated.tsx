import { createFileRoute, Navigate, Outlet } from "@tanstack/react-router";
import { useAuth } from "../services/auth";
import { Sidebar } from "../components/Sidebar";
import { DiscoveriesProvider } from "../contexts/DiscoveriesContext";

export const Route = createFileRoute("/_authenticated")({
  component: AuthenticatedContent,
});

function AuthenticatedContent() {
  const { session, isConfigured } = useAuth();

  if (!isConfigured) {
    return <div>Loading...</div>;
  }

  if (!session.authenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <DiscoveriesProvider>
      <div className="min-h-screen flex bg-background">
        <Sidebar />
        <main className="flex-1 p-6 min-w-0">
          <Outlet />
        </main>
      </div>
    </DiscoveriesProvider>
  );
}
