/** AuthContext provider for django-allauth headless API backend
 * - Uses Tanstack Router for navigation
 */
import { useEffect, useMemo, useState, createContext, useContext } from "react";

interface AuthenticatedSession {
  authenticated: true;
  id: number;
  email: string;
  display: string;
  [key: string]: unknown;
}

interface AnonymousSession {
  authenticated: false;
  id: null;
  email: null;
  display: null;
}

type Session = AuthenticatedSession | AnonymousSession;

type AllAuthProviderProps = {
  authUrl?: string;
  callbackUrl?: string;
  children: React.ReactNode;
};

type AllAuthConfig = {
  callbackUrl: string;
  loginUrl: string;
  providerLogin?: {
    id: string;
    loginUrl: string;
    callbackUrl: string;
  };
  emailLogin?: {
    id: string;
    login: (email: string, password: string) => Promise<void>;
  };
};

type AuthContextType = {
  config?: AllAuthConfig;
  isConfigured: boolean;
  session: Session;
  updateSession: () => Promise<void>;
  logout: () => Promise<void>;
};

const AUTH_URL = "/.auth/headless";

const ANON: Session = {
  authenticated: false,
  id: null,
  email: null,
  display: null,
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AllAuthProvider({
  authUrl = AUTH_URL,
  callbackUrl = "/login-callback",
  children,
}: AllAuthProviderProps) {
  const [session, setSession] = useState<Session>(ANON);
  const [isConfigured, setIsConfigured] = useState<boolean>(false);
  const [config, setConfig] = useState<AllAuthConfig | null>(null);

  const configUrl = `${authUrl}/browser/v1/config`;
  const sessionUrl = `${authUrl}/browser/v1/auth/session`;

  const updateSession = useMemo(
    () => async () =>
      await fetch(sessionUrl, {
        credentials: "include",
      })
        .then((res) => {
          if (res.status === 200) {
            return res.json();
          }
          throw new Error("Not authenticated");
        })
        .then((data) =>
          setSession({
            ...data,
            authenticated: true,
          })
        )
        .catch(() => {
          setSession(ANON);
        }),
    [sessionUrl]
  );

  const logout = useMemo(
    () => async () => {
      try {
        await fetch(sessionUrl, {
          method: "DELETE",
          credentials: "include",
        });
        setSession(ANON);
      } catch (error) {
        console.error("Logout error:", error);
      }
    },
    [sessionUrl]
  );

  useEffect(() => {
    Promise.allSettled([
      fetch(configUrl).then((res) => res.json()),
      updateSession(),
    ]).then((results) => {
      const configResult = results[0];
      if (configResult.status !== "fulfilled") {
        return;
      }
      if (configResult.value?.data?.socialaccount?.providers?.[0]) {
        setConfig({
          ...configResult.value?.data,
          providerLogin: {
            id: configResult.value?.data?.socialaccount?.providers?.[0]?.id,
            loginUrl: `${authUrl}/browser/v1/auth/provider/redirect`,
            callbackUrl,
          },
        });
      } else if (
        configResult.value?.data?.account?.login_methods.includes("email")
      ) {
        setConfig({
          ...configResult.value?.data,
          emailLogin: {
            id: configResult.value?.data?.account?.login_methods?.[0]?.id,
            login: (email: string, password: string) =>
              fetch(`${authUrl}/browser/v1/auth/login`, {
                method: "POST",
                body: JSON.stringify({ email, password }),
              }).then((res) => res.json()),
          },
        });
      }
      setIsConfigured(true);
    });
  }, [authUrl, callbackUrl, configUrl, updateSession]);

  return (
    <AuthContext.Provider
      value={{
        config: config || undefined,
        isConfigured,
        session,
        updateSession,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
