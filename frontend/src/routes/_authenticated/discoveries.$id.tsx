import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Eye, X, ArrowLeft, FileText, Scale, Loader2 } from "lucide-react";
import { useState, useEffect, useCallback } from "react";
import { getDiscoveryDetail, trackDiscovery, discardDiscovery, type DescubrimientoDetail } from "../../services/api/conflictDetector";
import { addRecentlyViewedDiscovery, removeRecentlyViewedDiscovery } from "../../lib/utils";
import ReactMarkdown from "react-markdown";
import { useDiscoveries } from "../../contexts/DiscoveriesContext";

export const Route = createFileRoute("/_authenticated/discoveries/$id")({
  component: ProjectDetail,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      from: (search.from as string) || undefined,
    };
  },
});

function ProjectDetail() {
  const navigate = useNavigate();
  const { id } = Route.useParams();
  const search = Route.useSearch();
  const { refreshPendingCount } = useDiscoveries();
  const [discovery, setDiscovery] = useState<DescubrimientoDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [visibleImpactos, setVisibleImpactos] = useState(10);
  const IMPACTOS_PER_PAGE = 10;

  // Determinar si viene de seguimiento
  const fromTracking = search.from === 'tracking';

  const loadDiscovery = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await getDiscoveryDetail(Number(id));
      setDiscovery(data);
      
      // Registrar que este proyecto fue visto
      addRecentlyViewedDiscovery({
        id: data.id,
        proyecto_id: data.proyecto_id,
        proyecto_titulo: data.proyecto_titulo,
        cantidad_impactos: data.impactos.length,
        max_nivel_relevancia: data.max_nivel_relevancia,
        estado: data.estado,
      });
    } catch (err) {
      console.error('Error al cargar descubrimiento:', err);
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadDiscovery();
  }, [loadDiscovery]);

  const getImpactLevel = (maxRelevancia: number): string => {
    if (maxRelevancia >= 50) return "Alto";
    if (maxRelevancia >= 30) return "Medio";
    return "Bajo";
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "Alto":
        return "bg-[hsl(var(--alert-high))] text-white";
      case "Medio":
        return "bg-[hsl(var(--alert-medium))] text-white";
      case "Bajo":
        return "bg-[hsl(var(--alert-low))] text-white";
      default:
        return "bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]";
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const handleDiscard = async () => {
    if (!discovery) return;
    try {
      await discardDiscovery(discovery.id);
      // Eliminar de proyectos vistos recientemente
      removeRecentlyViewedDiscovery(discovery.id);
      // Actualizar el contador de pendientes
      await refreshPendingCount();
      // Redirigir a la lista de descubrimientos
      navigate({ to: "/discoveries" });
    } catch (error) {
      console.error('Error al descartar descubrimiento:', error);
      alert('Error al descartar el descubrimiento. Por favor, intenta nuevamente.');
    }
  };

  const handleTrack = async () => {
    if (!discovery) return;
    try {
      await trackDiscovery(discovery.id);
      // Actualizar el contador de pendientes
      await refreshPendingCount();
      // Redirigir a la vista de seguimiento
      navigate({ to: "/tracking" });
    } catch (error) {
      console.error('Error al dar seguimiento:', error);
      alert('Error al dar seguimiento al descubrimiento. Por favor, intenta nuevamente.');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[hsl(var(--primary))]" />
        <span className="ml-3 text-muted-foreground">Cargando descubrimiento...</span>
      </div>
    );
  }

  if (error || !discovery) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-semibold text-foreground mb-2">Error al cargar</h3>
        <p className="text-muted-foreground">{error || 'No se encontró el descubrimiento'}</p>
        <button
          onClick={() => navigate({ to: fromTracking ? "/tracking" : "/discoveries" })}
          className="mt-4 px-4 py-2 bg-[hsl(var(--primary))] text-white rounded-md"
        >
          {fromTracking ? "Volver a Seguimiento" : "Volver a Descubrimientos"}
        </button>
      </div>
    );
  }

  const impactLevel = getImpactLevel(discovery.max_nivel_relevancia);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate({ to: fromTracking ? "/tracking" : "/discoveries" })}
          className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-[hsl(var(--muted))] rounded-md transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Volver
        </button>
      </div>

      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-[hsl(var(--foreground))]">
            {discovery.proyecto_titulo}
          </h1>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 text-sm border border-[hsl(var(--border))] rounded-md">
              Proyecto {discovery.proyecto_id}
            </span>
            <span
              className={`px-3 py-1 text-sm rounded-md ${getImpactColor(impactLevel)}`}
            >
              Impacto {impactLevel}
            </span>
            <span className="text-sm text-[hsl(var(--muted-foreground))]">
              {discovery.impactos.length} impacto(s) detectado(s)
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {discovery.estado !== 'DISCARDED' && (
            <button
              onClick={handleDiscard}
              className="flex items-center gap-2 px-4 py-2 text-sm border border-[hsl(var(--border))] rounded-md hover:bg-[hsl(var(--muted))] transition-colors"
            >
              <X className="h-4 w-4" />
              Descartar
            </button>
          )}
          {discovery.estado !== 'TRACKING' && (
            <button
              onClick={handleTrack}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-[hsl(var(--primary))] text-white rounded-md hover:opacity-90 transition-opacity"
            >
              <Eye className="h-4 w-4" />
              Dar Seguimiento
            </button>
          )}
        </div>
      </div>

      {/* Análisis Consolidado de Impacto */}
      {discovery.descripcion_impacto_consolidada && (
        <div className="bg-[hsl(var(--card))] rounded-lg border border-[hsl(var(--border))] p-6">
          <div className="mb-4">
            <h2 className="text-lg font-semibold mb-1">Análisis Consolidado de Impacto</h2>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              Resumen general de cómo este proyecto afecta tu documento
            </p>
          </div>
          <div className="markdown-content">
            <ReactMarkdown>{discovery.descripcion_impacto_consolidada}</ReactMarkdown>
          </div>
        </div>
      )}

      {/* Encabezados */}
      <div className="mb-4">
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Mostrando {Math.min(visibleImpactos, discovery.impactos.length)} de {discovery.impactos.length} impactos detectados
        </p>
      </div>

      {/* Impactos en pares alineados */}
      <div className="space-y-6">
        {discovery.impactos.slice(0, visibleImpactos).map((impacto) => (
          <div
            key={impacto.id}
            className="bg-[hsl(var(--card))] rounded-lg border border-[hsl(var(--border))] p-6"
          >
            <div className="grid gap-6 lg:grid-cols-2">
              {/* Extracto del Documento */}
              <div className="space-y-2">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-sm flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Extracto del Documento
                  </h3>
                  <span className="px-2 py-1 text-xs bg-[hsl(var(--muted))] rounded">
                    Relevancia: {impacto.nivel_relevancia}%
                  </span>
                </div>
                <p className="text-sm text-[hsl(var(--muted-foreground))] italic bg-[hsl(var(--muted))]/30 p-3 rounded">
                  {impacto.extracto_interno}
                </p>
              </div>

              {/* Extracto del Artículo */}
              <div className="space-y-2">
                <h3 className="font-semibold text-sm text-[hsl(var(--primary))] flex items-center gap-2 mb-2">
                  <Scale className="h-4 w-4" />
                  Extracto de Artículo {impacto.articulo_numero}
                </h3>
                <p className="text-sm text-[hsl(var(--muted-foreground))] bg-[hsl(var(--primary))]/5 p-3 rounded">
                  {impacto.extracto_articulo}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Botón de paginación centralizado */}
      {discovery.impactos.length > IMPACTOS_PER_PAGE && (
        <div className="flex justify-center">
          {visibleImpactos < discovery.impactos.length ? (
            <button
              onClick={() => setVisibleImpactos(prev => Math.min(prev + IMPACTOS_PER_PAGE, discovery.impactos.length))}
              className="px-6 py-2 bg-[hsl(var(--primary))] text-white rounded hover:opacity-90 transition-opacity"
            >
              Cargar siguientes {Math.min(IMPACTOS_PER_PAGE, discovery.impactos.length - visibleImpactos)} impactos
            </button>
          ) : (
            <button
              onClick={() => setVisibleImpactos(IMPACTOS_PER_PAGE)}
              className="px-6 py-2 bg-[hsl(var(--muted))] text-[hsl(var(--foreground))] rounded hover:bg-[hsl(var(--muted))]/80 transition-colors"
            >
              Volver a ver los primeros {IMPACTOS_PER_PAGE}
            </button>
          )}
        </div>
      )}

      {/* Información General */}
      <div className="bg-[hsl(var(--card))] rounded-lg border border-[hsl(var(--border))] p-6">
        <h2 className="text-lg font-semibold mb-4">Información General</h2>
        <div className="space-y-4">
          <div>
            <p className="text-sm font-medium text-[hsl(var(--muted-foreground))] mb-1">
              Fecha de Análisis
            </p>
            <p className="text-[hsl(var(--foreground))]">
              {formatDate(discovery.fecha_analisis)}
            </p>
          </div>
          <hr className="border-[hsl(var(--border))]" />
          <div>
            <p className="text-sm font-medium text-[hsl(var(--muted-foreground))] mb-1">
              Documento Analizado
            </p>
            <p className="text-[hsl(var(--foreground))]">{discovery.documento.nombre}</p>
          </div>
          <hr className="border-[hsl(var(--border))]" />
          <div>
            <p className="text-sm font-medium text-[hsl(var(--muted-foreground))] mb-1">
              Proyecto de Ley
            </p>
            <p className="text-[hsl(var(--foreground))]">
              {discovery.proyecto_id} - {discovery.proyecto_titulo}
            </p>
          </div>
          <hr className="border-[hsl(var(--border))]" />
          <div>
            <p className="text-sm font-medium text-[hsl(var(--muted-foreground))] mb-2">
              Impactos Detectados
            </p>
            <p className="text-sm text-[hsl(var(--muted-foreground))] leading-relaxed">
              Se detectaron {discovery.impactos.length} impacto(s) con un nivel de relevancia promedio de{' '}
              {Math.round(discovery.impactos.reduce((sum, imp) => sum + imp.nivel_relevancia, 0) / discovery.impactos.length)}%.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
