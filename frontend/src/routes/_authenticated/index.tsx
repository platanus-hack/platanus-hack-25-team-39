import { createFileRoute } from "@tanstack/react-router";
import { AlertTriangle, FileText, Eye, TrendingUp } from "lucide-react";

export const Route = createFileRoute("/_authenticated/")({
  component: Dashboard,
});

function Dashboard() {
  const stats = [
    {
      title: "Documentos Subidos",
      value: "24",
      description: "En tu perfil corporativo",
      icon: FileText,
      color: "text-primary",
    },
    {
      title: "Descubrimientos Activos",
      value: "8",
      description: "Proyectos de ley detectados",
      icon: AlertTriangle,
      color: "text-[hsl(var(--alert-medium))]",
    },
    {
      title: "En Seguimiento",
      value: "5",
      description: "Proyectos monitoreados",
      icon: Eye,
      color: "text-[hsl(var(--status-active))]",
    },
    {
      title: "Alto Impacto",
      value: "2",
      description: "Requieren atención urgente",
      icon: TrendingUp,
      color: "text-[hsl(var(--alert-high))]",
    },
  ];

  const recentActivity = [
    {
      project: "Ley de Protección de Datos Personales",
      status: "Nueva coincidencia",
      impact: "Alto",
      date: "Hace 2 horas",
    },
    {
      project: "Reforma Laboral - Art. 152",
      status: "Actualización disponible",
      impact: "Medio",
      date: "Hace 5 horas",
    },
    {
      project: "Ley de Transparencia Corporativa",
      status: "Votación en Senado",
      impact: "Alto",
      date: "Hace 1 día",
    },
  ];

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
          <h3 className="text-lg font-semibold">Actividad Reciente</h3>
          <p className="text-sm text-muted-foreground">
            Últimas actualizaciones en proyectos de ley relevantes
          </p>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div
                key={index}
                className="flex items-start justify-between border-b border-border pb-4 last:border-0 last:pb-0"
              >
                <div className="space-y-1">
                  <p className="font-medium text-foreground">{activity.project}</p>
                  <p className="text-sm text-muted-foreground">{activity.status}</p>
                </div>
                <div className="text-right space-y-1">
                  <span
                    className={`inline-block px-2 py-1 text-xs font-medium rounded ${
                      activity.impact === "Alto"
                        ? "bg-[hsl(var(--alert-high))] text-[hsl(var(--alert-high-foreground))]"
                        : "bg-[hsl(var(--alert-medium))] text-[hsl(var(--alert-medium-foreground))]"
                    }`}
                  >
                    {activity.impact}
                  </span>
                  <p className="text-xs text-muted-foreground">{activity.date}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
