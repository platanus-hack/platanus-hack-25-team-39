import { createFileRoute, Navigate } from "@tanstack/react-router";
import { useAuth } from "../services/auth";
import { useEffect, useState } from "react";
import { Box, Text } from "@seisveinte/react";

export const Route = createFileRoute("/login-callback")({
  component: RouteComponent,
});

function RouteComponent() {
  const [resolved, setResolved] = useState(false);
  const { session, updateSession } = useAuth();

  useEffect(() => {
    if (!resolved) {
      updateSession().finally(() => {
        setResolved(true);
      });
    }
  }, [updateSession, resolved]);

  if (!resolved) {
    return (
      <Box>
        <Text size="3" color="gray" align="center">
          Loading...
        </Text>
      </Box>
    );
  }

  return session.authenticated ? (
    <Navigate to="/" replace />
  ) : (
    <Box>
      <Text size="3" color="gray" align="center">
        Failed to login
      </Text>
    </Box>
  );
}
