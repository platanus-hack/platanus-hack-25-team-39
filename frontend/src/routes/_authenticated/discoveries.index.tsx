import { createFileRoute, Link } from "@tanstack/react-router";
import { Eye, X, AlertTriangle, Loader2, FileText } from "lucide-react";
import { useState, useEffect } from "react";
import { listDiscoveries, trackDiscovery, discardDiscovery, type DescubrimientoList } from "../../services/api/conflictDetector";
import { useDiscoveries } from "../../contexts/DiscoveriesContext";

export const Route = createFileRoute("/_authenticated/discoveries/")({
  component: Discoveries,
});

function Discoveries() {
  const [discoveries, setDiscoveries] = useState<DescubrimientoList[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { refreshPendingCount } = useDiscoveries();

  useEffect(() => {
    loadDiscoveries();
  }, []);

  const loadDiscoveries = async () => {
    try {
      setIsLoading(true);
      const data = await listDiscoveries();
      setDiscoveries(data);
    } catch (error) {
      console.error('Error al cargar descubrimientos:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getImpactLevel = (maxRelevancia: number): string => {
    if (maxRelevancia >= 50) return "Alto";
    if (maxRelevancia >= 30) return "Medio";
    return "Bajo";
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "Alto":
        return "bg-[hsl(var(--alert-high))] text-[hsl(var(--alert-high-foreground))]";
      case "Medio":
        return "bg-[hsl(var(--alert-medium))] text-[hsl(var(--alert-medium-foreground))]";
      case "Bajo":
        return "bg-[hsl(var(--alert-low))] text-[hsl(var(--alert-low-foreground))]";
      default:
        return "bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]";
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const handleDiscard = async (discoveryId: number) => {
    try {
      await discardDiscovery(discoveryId);
      // Recargar la lista de descubrimientos y actualizar el contador
      await Promise.all([loadDiscoveries(), refreshPendingCount()]);
    } catch (error) {
      console.error('Error al descartar descubrimiento:', error);
      alert('Error al descartar el descubrimiento. Por favor, intenta nuevamente.');
    }
  };

  const handleTrack = async (discoveryId: number) => {
    try {
      await trackDiscovery(discoveryId);
      // Recargar la lista de descubrimientos y actualizar el contador
      await Promise.all([loadDiscoveries(), refreshPendingCount()]);
    } catch (error) {
      console.error('Error al dar seguimiento:', error);
      alert('Error al dar seguimiento al descubrimiento. Por favor, intenta nuevamente.');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Descubrimientos</h1>
        <p className="text-muted-foreground">
          Proyectos de ley que podrían afectar a tu empresa
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[hsl(var(--primary))]" />
          <span className="ml-3 text-muted-foreground">Cargando descubrimientos...</span>
        </div>
      ) : discoveries.length === 0 ? (
        <div className="text-center py-12 bg-card rounded-lg border border-[hsl(var(--border))]">
          <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
          <h3 className="text-lg font-semibold text-foreground mb-2">No hay descubrimientos</h3>
          <p className="text-muted-foreground">
            Sube documentos para detectar conflictos con proyectos de ley
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {discoveries.map((discovery) => {
            const impactLevel = getImpactLevel(discovery.max_nivel_relevancia);
            return (
              <div
                key={discovery.id}
                className="bg-card rounded-lg border border-[hsl(var(--border))] p-6 hover:shadow-md transition-shadow"
              >
                <div className="space-y-4">
                  <Link
                    to="/discoveries/$id"
                    params={{ id: String(discovery.id) }}
                    search={{ from: undefined }}
                    className="flex items-start justify-between gap-4 block"
                  >
                    <div className="flex-1 space-y-2">
                      <div className="flex items-start gap-3">
                        <AlertTriangle className="h-5 w-5 text-[hsl(var(--alert-medium))] mt-1 flex-shrink-0" />
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg text-foreground mb-1 hover:text-[hsl(var(--primary))] transition-colors">
                            Proyecto {discovery.proyecto_id}
                          </h3>
                          <p className="text-sm text-[hsl(var(--muted-foreground))]">
                            {discovery.proyecto_titulo}
                          </p>
                        </div>
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getImpactColor(impactLevel)}`}>
                      Impacto {impactLevel}
                    </span>
                  </Link>

                  <div className="flex items-center justify-between pt-3 border-t border-[hsl(var(--border))]">
                    <div className="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
                      <span>{discovery.cantidad_impactos} impacto(s) detectado(s)</span>
                      <span>•</span>
                      <span>Analizado: {formatDate(discovery.fecha_analisis)}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleDiscard(discovery.id)}
                        className="px-3 py-1.5 text-sm border border-[hsl(var(--border))] rounded-md hover:bg-[hsl(var(--accent))] flex items-center gap-2"
                      >
                        <X className="h-4 w-4" />
                        Descartar
                      </button>
                      <button
                        onClick={() => handleTrack(discovery.id)}
                        className="px-3 py-1.5 text-sm bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] rounded-md hover:bg-[hsl(var(--primary))]/90 flex items-center gap-2"
                      >
                        <Eye className="h-4 w-4" />
                        Dar Seguimiento
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
