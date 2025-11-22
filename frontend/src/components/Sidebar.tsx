import {
  Box,
  Flex,
  Button,
  Text,
  Avatar,
  Separator,
  ScrollArea,
  Popover,
} from "@seisveinte/react";
import { Link, useMatchRoute, useNavigate } from "@tanstack/react-router";
import { useAuth } from "../services/auth";

interface SidebarProps {
  userEmail: string;
}

export function Sidebar({ userEmail }: SidebarProps) {
  const { logout } = useAuth();
  const matchRoute = useMatchRoute();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout?.();
      navigate({ to: "/login" });
    } catch (err) {
      console.error("Error logging out:", err);
    }
  };

  // Helper to check if route is active
  const isActive = (path: string, fuzzy?: boolean) => {
    return !!matchRoute({ to: path, fuzzy });
  };

  return (
    <Box
      style={{
        width: "250px",
        height: "100vh",
        borderRight: "1px solid var(--gray-a5)",
        backgroundColor: "var(--color-panel)",
        position: "fixed",
        left: 0,
        top: 0,
      }}
    >
      <Flex direction="column" style={{ height: "100%" }}>
        {/* Header/Logo */}

        {/* TODO: Add header/logo */}

        {/* Navigation */}
        <ScrollArea style={{ flex: 1 }}>
          <Flex direction="column" gap="2" p="3">
            <Link to="/">
              <Button
                variant={isActive("/") ? "soft" : "ghost"}
                style={{ justifyContent: "flex-start", width: "100%" }}
              >
                Home
              </Button>
            </Link>
            <Link to="/tab2">
              <Button
                variant={isActive("/tab2") ? "soft" : "ghost"}
                style={{ justifyContent: "flex-start", width: "100%" }}
              >
                Tab 2
              </Button>
            </Link>
            <Link to="/tab3">
              <Button
                variant={isActive("/tab3") ? "soft" : "ghost"}
                style={{ justifyContent: "flex-start", width: "100%" }}
              >
                Tab 3
              </Button>
            </Link>
          </Flex>
        </ScrollArea>

        <Separator size="4" />

        {/* User Profile */}
        <Box p="3">
          <Popover.Root>
            <Popover.Trigger>
              <Flex gap="3" align="center" style={{ cursor: "pointer" }}>
                <Avatar
                  size="2"
                  fallback={userEmail.charAt(0).toUpperCase()}
                  radius="full"
                />
                <Flex direction="column" gap="1">
                  <Text size="2" weight="medium">
                    {userEmail.split("@")[0]}
                  </Text>
                  <Text size="1" color="gray">
                    {userEmail}
                  </Text>
                </Flex>
              </Flex>
            </Popover.Trigger>
            <Popover.Content style={{ width: "200px" }}>
              <Flex direction="column" gap="2">
                <Link to="/profile">
                  <Button
                    variant="ghost"
                    style={{ justifyContent: "flex-start", width: "100%" }}
                  >
                    Profile
                  </Button>
                </Link>
                <Button
                  variant="ghost"
                  style={{ justifyContent: "flex-start" }}
                >
                  Settings
                </Button>
                <Separator size="4" />
                <Button
                  variant="ghost"
                  color="red"
                  style={{ justifyContent: "flex-start" }}
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </Flex>
            </Popover.Content>
          </Popover.Root>
        </Box>
      </Flex>
    </Box>
  );
}
