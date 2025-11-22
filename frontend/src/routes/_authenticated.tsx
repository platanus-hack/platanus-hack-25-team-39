import { createFileRoute, Navigate, Outlet } from "@tanstack/react-router";
import { useAuth } from "../services/auth";
import Layout from "../components/Layout";

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
    <Layout>
      <Outlet />
    </Layout>
  );
}
