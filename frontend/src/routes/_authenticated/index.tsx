import { createFileRoute, Link } from "@tanstack/react-router";
import { AlertTriangle, FileText, Eye, TrendingUp, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { 
  listDocuments, 
  listDiscoveries, 
  listTrackingDiscoveries,
  type DescubrimientoList 
} from "../../services/api/conflictDetector";
import { 
  getRecentlyViewedDiscoveries, 
  type RecentlyViewedDiscovery 
} from "../../lib/utils";

export const Route = createFileRoute("/_authenticated/")({
  component: Dashboard,
});

function Dashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [documentsCount, setDocumentsCount] = useState(0);
  const [activeDiscoveries, setActiveDiscoveries] = useState<DescubrimientoList[]>([]);
  const [trackingDiscoveries, setTrackingDiscoveries] = useState<DescubrimientoList[]>([]);
  const [recentlyViewed, setRecentlyViewed] = useState<RecentlyViewedDiscovery[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  // Actualizar proyectos vistos recientemente cuando cambian los descubrimientos
  useEffect(() => {
    const viewed = getRecentlyViewedDiscoveries();
    
    // Crear un mapa con la información más reciente de descubrimientos activos y en seguimiento
    const discoveriesMap = new Map<number, DescubrimientoList>();
    [...activeDiscoveries, ...trackingDiscoveries].forEach(d => {
      discoveriesMap.set(d.id, d);
    });
    
    // Filtrar y actualizar solo los que están presentes en descubrimientos activos o seguimiento
    // Actualizar la información con los datos más recientes
    const sorted = viewed
      .filter(item => discoveriesMap.has(item.id))
      .map(item => {
        const currentDiscovery = discoveriesMap.get(item.id)!;
        // Actualizar con información más reciente, pero mantener viewedAt
        return {
          ...item,
          max_nivel_relevancia: currentDiscovery.max_nivel_relevancia,
          cantidad_impactos: currentDiscovery.cantidad_impactos,
          estado: currentDiscovery.estado,
        };
      })
      .sort((a, b) => {
        return new Date(b.viewedAt).getTime() - new Date(a.viewedAt).getTime();
      });
    
    setRecentlyViewed(sorted);
  }, [activeDiscoveries, trackingDiscoveries]);

  useEffect(() => {
    // Función para actualizar proyectos vistos recientemente
    const updateRecentlyViewed = () => {
      const viewed = getRecentlyViewedDiscoveries();
      
      // Crear un mapa con la información más reciente de descubrimientos activos y en seguimiento
      const discoveriesMap = new Map<number, DescubrimientoList>();
      [...activeDiscoveries, ...trackingDiscoveries].forEach(d => {
        discoveriesMap.set(d.id, d);
      });
      
      // Filtrar y actualizar solo los que están presentes en descubrimientos activos o seguimiento
      // Actualizar la información con los datos más recientes
      const sorted = viewed
        .filter(item => discoveriesMap.has(item.id))
        .map(item => {
          const currentDiscovery = discoveriesMap.get(item.id)!;
          // Actualizar con información más reciente, pero mantener viewedAt
          return {
            ...item,
            max_nivel_relevancia: currentDiscovery.max_nivel_relevancia,
            cantidad_impactos: currentDiscovery.cantidad_impactos,
            estado: currentDiscovery.estado,
          };
        })
        .sort((a, b) => {
          return new Date(b.viewedAt).getTime() - new Date(a.viewedAt).getTime();
        });
      
      setRecentlyViewed(sorted);
    };
    
    // Actualizar cuando la página se vuelve visible (cuando se vuelve de otra página)
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        updateRecentlyViewed();
      }
    };
    
    // Actualizar cuando se hace focus en la ventana
    const handleFocus = () => {
      updateRecentlyViewed();
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, [activeDiscoveries, trackingDiscoveries]);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [documents, discoveries, tracking] = await Promise.all([
        listDocuments(),
        listDiscoveries(),
        listTrackingDiscoveries(),
      ]);

      setDocumentsCount(documents.length);
      setActiveDiscoveries(discoveries);
      setTrackingDiscoveries(tracking);

      // Los proyectos vistos recientemente se actualizarán automáticamente
      // cuando se actualicen activeDiscoveries y trackingDiscoveries
      // a través del useEffect que depende de ellos
    } catch (error) {
      console.error('Error al cargar datos del dashboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getImpactLevel = (maxRelevancia: number): string => {
    if (maxRelevancia >= 50) return "Alto";
    if (maxRelevancia >= 30) return "Medio";
    return "Bajo";
  };

  const formatRelativeTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Hace menos de un minuto";
    if (diffMins < 60) return `Hace ${diffMins} ${diffMins === 1 ? 'minuto' : 'minutos'}`;
    if (diffHours < 24) return `Hace ${diffHours} ${diffHours === 1 ? 'hora' : 'horas'}`;
    if (diffDays < 7) return `Hace ${diffDays} ${diffDays === 1 ? 'día' : 'días'}`;
    
    return date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  // Calcular estadísticas
  // Alto impacto: descubrimientos con max_nivel_relevancia >= 50 tanto en activos como en seguimiento
  const highImpactCount = [
    ...activeDiscoveries,
    ...trackingDiscoveries
  ].filter(d => d.max_nivel_relevancia >= 50).length;

  const stats = [
    {
      title: "Documentos Subidos",
      value: documentsCount.toString(),
      description: "En tu perfil corporativo",
      icon: FileText,
      color: "text-primary",
    },
    {
      title: "Descubrimientos Activos",
      value: activeDiscoveries.length.toString(),
      description: "Proyectos de ley detectados",
      icon: AlertTriangle,
      color: "text-[hsl(var(--alert-medium))]",
    },
    {
      title: "En Seguimiento",
      value: trackingDiscoveries.length.toString(),
      description: "Proyectos monitoreados",
      icon: Eye,
      color: "text-[hsl(var(--status-active))]",
    },
    {
      title: "Alto Impacto",
      value: highImpactCount.toString(),
      description: "Requieren atención urgente",
      icon: TrendingUp,
      color: "text-[hsl(var(--alert-high))]",
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[hsl(var(--primary))]" />
        <span className="ml-3 text-muted-foreground">Cargando dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Dashboard</h1>
        <p className="text-muted-foreground">
          Resumen de tu radar legislativo corporativo
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.title} className="bg-card rounded-lg border border-border p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium">{stat.title}</p>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </div>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
            </div>
          );
        })}
      </div>

      <div className="bg-card rounded-lg border border-border">
        <div className="p-6 border-b border-border">
          <h3 className="text-lg font-semibold">Proyectos Vistos Recientemente</h3>
          <p className="text-sm text-muted-foreground">
            Proyectos de ley que has consultado recientemente
          </p>
        </div>
        <div className="p-6">
          {recentlyViewed.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No has visto ningún proyecto recientemente</p>
              <p className="text-xs text-muted-foreground mt-2">
                Los proyectos que consultes aparecerán aquí
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {recentlyViewed.slice(0, 5).map((item) => {
                const impactLevel = getImpactLevel(item.max_nivel_relevancia);
                const status = item.estado === 'TRACKING' 
                  ? 'En seguimiento' 
                  : item.estado === 'DISCARDED'
                  ? 'Descartado'
                  : 'Pendiente';
                
                return (
                  <Link
                    key={item.id}
                    to="/discoveries/$id"
                    params={{ id: String(item.id) }}
                    search={{ from: undefined }}
                    className="block"
                  >
                    <div className="flex items-start justify-between border-b border-border pb-4 last:border-0 last:pb-0 hover:bg-[hsl(var(--muted))]/30 -mx-2 px-2 py-2 rounded transition-colors">
                      <div className="space-y-1 flex-1">
                        <p className="font-medium text-foreground">{item.proyecto_titulo}</p>
                        <p className="text-sm text-muted-foreground">{status}</p>
                      </div>
                      <div className="text-right space-y-1">
                        <span
                          className={`inline-block px-2 py-1 text-xs font-medium rounded ${
                            impactLevel === "Alto"
                              ? "bg-[hsl(var(--alert-high))] text-[hsl(var(--alert-high-foreground))]"
                              : impactLevel === "Medio"
                              ? "bg-[hsl(var(--alert-medium))] text-[hsl(var(--alert-medium-foreground))]"
                              : "bg-[hsl(var(--alert-low))] text-[hsl(var(--alert-low-foreground))]"
                          }`}
                        >
                          {impactLevel}
                        </span>
                        <p className="text-xs text-muted-foreground">
                          {formatRelativeTime(item.viewedAt)}
                        </p>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
