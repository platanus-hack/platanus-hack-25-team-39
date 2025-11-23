import { LayoutDashboard, FileText, Search, Eye, X } from "lucide-react";
import { Link, useMatchRoute } from "@tanstack/react-router";
import { useState } from "react";
import { cn } from "@/lib/utils";
import logoLW from "@/assets/logo_lw.svg";
import { useDiscoveries } from "@/contexts/DiscoveriesContext";

const items = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Documentos", url: "/documents", icon: FileText },
  { title: "Descubrimientos", url: "/discoveries", icon: Search, showBadge: true },
  { title: "Seguimiento", url: "/tracking", icon: Eye },
];

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(true);
  const { pendingCount } = useDiscoveries();
  const matchRoute = useMatchRoute();

  return (
    <>
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 h-screen bg-[hsl(var(--sidebar-background))] text-[hsl(var(--sidebar-foreground))] transition-all duration-300 z-40 flex-shrink-0",
          isOpen ? "w-64" : "w-16"
        )}
      >
        {/* Header */}
        <div className="h-16 flex items-center px-4 border-b border-[hsl(var(--sidebar-border))]">
          {isOpen ? (
            <>
              <div className="flex items-center gap-2 flex-1">
                <h1 className="font-bold text-2xl">LegalWard</h1>
                <div className="h-10 w-10 overflow-hidden flex items-center justify-center flex-shrink-0 mb-2.5">
                  <img
                    src={logoLW}
                    alt="LegalWard Logo"
                    className="h-10 w-10 object-contain"
                  />
                </div>
              </div>
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="p-2 hover:bg-[hsl(var(--sidebar-accent))] rounded-md transition-colors flex-shrink-0"
              >
                <X className="h-5 w-5" />
              </button>
            </>
          ) : (
            <div className="flex items-center justify-center w-full">
              <div className="h-10 w-10 overflow-hidden flex items-center justify-center cursor-pointer" onClick={() => setIsOpen(true)}>
                <img
                  src={logoLW}
                  alt="LegalWard Logo"
                  className="h-10 w-10 object-contain"
                />
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="mt-4 px-2">
          {isOpen && (
            <p className="px-3 mb-2 text-xs font-medium text-[hsl(var(--sidebar-foreground))] opacity-60">
              Navegación
            </p>
          )}
          <ul className="space-y-1">
            {items.map((item) => {
              const isActive = !!matchRoute({ to: item.url, fuzzy: false });
              const Icon = item.icon;
              const showNotification = item.showBadge && pendingCount > 0;

              return (
                <li key={item.title}>
                  <Link
                    to={item.url}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-md transition-colors relative",
                      isActive
                        ? "bg-[hsl(var(--sidebar-accent))] text-[hsl(var(--sidebar-accent-foreground))]"
                        : "hover:bg-[hsl(var(--sidebar-accent))]/50"
                    )}
                  >
                    <Icon className="h-5 w-5 flex-shrink-0" />
                    {isOpen && (
                      <span className="flex-1">{item.title}</span>
                    )}
                    {showNotification && (
                      <span className={cn(
                        "flex items-center justify-center rounded-full bg-red-500 text-white text-xs font-bold min-w-[20px] h-5 px-1.5",
                        !isOpen && "absolute -top-1 -right-1"
                      )}>
                        {pendingCount > 99 ? '99+' : pendingCount}
                      </span>
                    )}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>

      {/* Spacer */}
      <div className={cn("transition-all duration-300 flex-shrink-0", isOpen ? "w-64" : "w-16")} />
    </>
  );
}
