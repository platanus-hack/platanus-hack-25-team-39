import { createFileRoute, Link } from "@tanstack/react-router";
import { Loader2, FileText, CheckCircle2, Clock, AlertCircle, ArrowDown, FastForward } from "lucide-react";
import { useState, useEffect } from "react";
import { listTrackingDiscoveries, advanceTime, type DescubrimientoList } from "../../services/api/conflictDetector";

export const Route = createFileRoute("/_authenticated/tracking")({
  component: Tracking,
});

function Tracking() {
  const [discoveries, setDiscoveries] = useState<DescubrimientoList[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAdvancing, setIsAdvancing] = useState(false);

  useEffect(() => {
    loadTrackingDiscoveries();
  }, []);

  const loadTrackingDiscoveries = async () => {
    try {
      setIsLoading(true);
      const data = await listTrackingDiscoveries();
      setDiscoveries(data);
    } catch (error) {
      console.error('Error al cargar descubrimientos en seguimiento:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdvanceTime = async () => {
    try {
      setIsAdvancing(true);
      await advanceTime();
      await loadTrackingDiscoveries();
    } catch (error) {
      console.error('Error al avanzar el tiempo:', error);
    } finally {
      setIsAdvancing(false);
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-6 w-6 text-[hsl(var(--status-active))]" />;
      case "in-progress":
        return <Clock className="h-6 w-6 text-[hsl(var(--status-pending))]" />;
      case "pending":
        return <AlertCircle className="h-6 w-6 text-[hsl(var(--status-inactive))]" />;
      default:
        return null;
    }
  };

  const getTimelineFromEtapa = (etapa: number | null | undefined, proyectoFecha: string | null | undefined) => {
    const etapaActual = etapa || 1;
    
    // Helper para agregar días a una fecha y formatearla
    const addDaysAndFormat = (dateString: string, days: number): string => {
      const date = new Date(dateString);
      date.setDate(date.getDate() + days);
      return formatDate(date.toISOString());
    };
    
    const fechaIngreso = proyectoFecha ? formatDate(proyectoFecha) : null;
    
    const timeline = [
      { 
        stage: "Ingreso", 
        status: etapaActual >= 1 ? (etapaActual === 1 ? "in-progress" : "completed") : "pending", 
        date: etapaActual > 1 ? fechaIngreso : null
      },
      { 
        stage: "Primera Cámara", 
        status: etapaActual >= 2 ? (etapaActual === 2 ? "in-progress" : "completed") : "pending", 
        date: etapaActual > 2 && proyectoFecha ? addDaysAndFormat(proyectoFecha, 45) : null 
      },
      { 
        stage: "Segunda Cámara", 
        status: etapaActual >= 3 ? (etapaActual === 3 ? "in-progress" : "completed") : "pending", 
        date: etapaActual > 3 && proyectoFecha ? addDaysAndFormat(proyectoFecha, 120) : null 
      },
      { 
        stage: "Promulgación", 
        status: etapaActual >= 4 ? (etapaActual === 4 ? "in-progress" : "completed") : "pending", 
        date: etapaActual > 4 && proyectoFecha ? addDaysAndFormat(proyectoFecha, 180) : null 
      },
    ];

    return timeline;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Seguimiento</h1>
          <p className="text-muted-foreground">
            Proyectos de ley que estás monitoreando activamente
          </p>
        </div>
        <button
          onClick={handleAdvanceTime}
          disabled={isAdvancing || discoveries.length === 0}
          className="flex items-center gap-2 px-4 py-2 bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] rounded-lg hover:bg-[hsl(var(--primary))]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {isAdvancing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Avanzando...
            </>
          ) : (
            <>
              <FastForward className="h-4 w-4" />
              Avanzar Tiempo (Demo)
            </>
          )}
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[hsl(var(--primary))]" />
          <span className="ml-3 text-muted-foreground">Cargando descubrimientos en seguimiento...</span>
        </div>
      ) : discoveries.length === 0 ? (
        <div className="text-center py-12 bg-card rounded-lg border border-[hsl(var(--border))]">
          <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
          <h3 className="text-lg font-semibold text-foreground mb-2">No hay descubrimientos en seguimiento</h3>
          <p className="text-muted-foreground">
            Los descubrimientos que marques como "Dar Seguimiento" aparecerán aquí
          </p>
        </div>
      ) : (
        <div className="grid gap-6">
          {discoveries.map((discovery) => {
            const impactLevel = getImpactLevel(discovery.max_nivel_relevancia);
            const timeline = getTimelineFromEtapa(discovery.proyecto_etapa, discovery.proyecto_fecha || undefined);
            
            return (
              <div key={discovery.id} className="bg-card rounded-lg border border-[hsl(var(--border))] hover:shadow-md transition-shadow">
                <div className="p-6 border-b border-[hsl(var(--border))]">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1 flex-1">
                      <Link
                        to="/discoveries/$id"
                        params={{ id: String(discovery.id) }}
                        search={{ from: 'tracking' }}
                        className="block"
                      >
                        <h3 className="text-xl font-semibold hover:text-[hsl(var(--primary))] transition-colors">
                          Proyecto {discovery.proyecto_id}
                        </h3>
                        <p className="text-sm text-[hsl(var(--muted-foreground))]">
                          {discovery.proyecto_titulo}
                        </p>
                      </Link>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getImpactColor(impactLevel)}`}>
                        Impacto {impactLevel}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="p-6 space-y-6">
                  {/* Timeline */}
                  <div className="relative">
                    {/* Línea punteada a la izquierda con flecha al final */}
                    <div className="absolute top-0 left-0 h-full flex flex-col items-center">
                      <div className="flex-1 w-0.5 border-l-2 border-dashed border-[hsl(var(--border))]" />
                      <div className="-mb-1">
                        <ArrowDown className="h-4 w-4 text-[hsl(var(--border))]" />
                      </div>
                    </div>
                    <div className="pl-20 space-y-4">
                      {timeline.map((milestone, index) => (
                        <div key={index} className="relative flex items-start gap-3">
                          <div className="absolute left-0 -ml-12 bg-card rounded-full z-10">
                            {getStatusIcon(milestone.status)}
                          </div>
                          <div className="flex-1 pt-1">
                            <div className="flex items-center justify-between">
                              <p
                                className={`font-medium text-sm ${
                                  milestone.status === "completed"
                                    ? "text-[hsl(var(--status-active))]"
                                    : milestone.status === "in-progress"
                                    ? "text-[hsl(var(--status-pending))]"
                                    : "text-[hsl(var(--muted-foreground))]"
                                }`}
                              >
                                {milestone.stage}
                              </p>
                              {milestone.date && (
                                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                                  {milestone.date}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
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
