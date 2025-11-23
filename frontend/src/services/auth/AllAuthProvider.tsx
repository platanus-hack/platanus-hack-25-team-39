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

// Backend URL from environment variable
const AUTH_URL = import.meta.env.VITE_BACKEND_URL
  ? `${import.meta.env.VITE_BACKEND_URL}/.auth/headless`
  : "/.auth/headless";

console.log('[AllAuth] Using backend URL:', import.meta.env.VITE_BACKEND_URL || 'relative path (development)');

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
    () => async () => {
      try {

        console.log(`[Auth] Verificando sesión en: ${sessionUrl}`);
        const res = await fetch(sessionUrl, {
          credentials: "include",
        });
        
        console.log(`[Auth] Respuesta de sesión: status=${res.status}, ok=${res.ok}, contentType=${res.headers.get("content-type")}`);
        
        if (res.status === 200) {
          const contentType = res.headers.get("content-type");
          if (!contentType || !contentType.includes("application/json")) {
            const text = await res.text();
            console.error(`[Auth] Respuesta no es JSON. Content-Type: ${contentType}, Body: ${text.substring(0, 200)}`);
            throw new Error(`Expected JSON but got ${contentType}`);
          }

          const data = await res.json();
          console.log(`[Auth] Datos de sesión recibidos:`, data);
          setSession({
            ...data,
            authenticated: true,
          });
        } else if (res.status === 401) {
          // 401 is expected when not authenticated
          console.log(`[Auth] No active session (401 - not authenticated)`);
          setSession(ANON);
        } else {
          const errorText = await res.text().catch(() => "No se pudo leer el error");
          console.warn(`[Auth] Session check failed with status ${res.status}:`, errorText);
          setSession(ANON);
          throw new Error(`Session check failed: ${res.status} ${errorText}`);
        }
      } catch (error) {
        console.error("[Auth] Error fetching session:", error);
        setSession(ANON);
        throw error;
      }
    },
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
      fetch(configUrl, { credentials: "include" }).then((res) => res.json()),
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
                headers: {
                  "Content-Type": "application/json",
                },
                credentials: "include",
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
