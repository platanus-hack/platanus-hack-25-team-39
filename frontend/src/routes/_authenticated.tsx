import { createFileRoute, Navigate, Outlet } from "@tanstack/react-router";
import { Box } from "@seisveinte/react";
import { useAuth } from "../services/auth";
import { Sidebar } from "../components/Sidebar";

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
    <>
      <Sidebar userEmail={session?.email || ""} />
      <Box style={{ marginLeft: "250px" }}>
        <Outlet />
      </Box>
    </>
  );
}
