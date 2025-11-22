import { createFileRoute } from "@tanstack/react-router";
import { ExternalLink, CheckCircle2, Clock, AlertCircle } from "lucide-react";

export const Route = createFileRoute("/_authenticated/tracking")({
  component: Tracking,
});

function Tracking() {
  const trackedProjects = [
    {
      id: 1,
      title: "Ley de Protección de Datos Personales",
      impact: "Alto",
      category: "Legal / Compliance",
      timeline: [
        { stage: "Ingreso", status: "completed", date: "10 Dic 2023" },
        { stage: "Comisión", status: "in-progress", date: "15 Ene 2024" },
        { stage: "Cámara de Diputados", status: "pending", date: null },
        { stage: "Senado", status: "pending", date: null },
        { stage: "Promulgación", status: "pending", date: null },
      ],
      lastUpdate: "Hace 2 días",
      updateDescription: "Ingresada indicación del Ejecutivo modificando Artículo 7",
    },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-[hsl(var(--status-active))]" />;
      case "in-progress":
        return <Clock className="h-4 w-4 text-[hsl(var(--status-pending))]" />;
      case "pending":
        return <AlertCircle className="h-4 w-4 text-[hsl(var(--status-inactive))]" />;
      default:
        return null;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "Alto":
        return "bg-[hsl(var(--alert-high))] text-[hsl(var(--alert-high-foreground))]";
      case "Medio":
        return "bg-[hsl(var(--alert-medium))] text-[hsl(var(--alert-medium-foreground))]";
      default:
        return "bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]";
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Seguimiento</h1>
        <p className="text-muted-foreground">
          Proyectos de ley que estás monitoreando activamente
        </p>
      </div>

      <div className="grid gap-6">
        {trackedProjects.map((project) => (
          <div key={project.id} className="bg-card rounded-lg border border-[hsl(var(--border))] hover:shadow-md transition-shadow">
            <div className="p-6 border-b border-[hsl(var(--border))]">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <h3 className="text-xl font-semibold">{project.title}</h3>
                  <p className="text-sm text-[hsl(var(--muted-foreground))]">{project.category}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getImpactColor(project.impact)}`}>
                    Impacto {project.impact}
                  </span>
                  <button className="p-1.5 hover:bg-[hsl(var(--accent))] rounded-md">
                    <ExternalLink className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
            <div className="p-6 space-y-6">
              {/* Timeline */}
              <div className="relative">
                <div className="absolute top-0 left-2 h-full w-0.5 bg-[hsl(var(--border))]" />
                <div className="space-y-4">
                  {project.timeline.map((milestone, index) => (
                    <div key={index} className="relative flex items-start gap-4">
                      <div className="relative z-10 bg-card">
                        {getStatusIcon(milestone.status)}
                      </div>
                      <div className="flex-1 pt-0.5">
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

              {/* Latest Update */}
              <div className="bg-[hsl(var(--muted))]/30 rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-foreground">
                    Última Actualización
                  </p>
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    {project.lastUpdate}
                  </span>
                </div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  {project.updateDescription}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
