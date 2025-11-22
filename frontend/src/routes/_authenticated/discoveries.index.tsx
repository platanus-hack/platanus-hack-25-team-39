import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Eye, X, ExternalLink, AlertTriangle } from "lucide-react";

export const Route = createFileRoute("/_authenticated/discoveries/")({
  component: Discoveries,
});

function Discoveries() {
  const navigate = useNavigate();

  const discoveries = [
    {
      id: 1,
      title: "Ley de Protección de Datos Personales",
      description: "Regula el tratamiento de datos personales y establece nuevas obligaciones para empresas que procesan información de clientes.",
      impact: "Alto",
      category: "Legal / Compliance",
      affectedDocs: 3,
      date: "Ingresado: 10 Dic 2023",
    },
    {
      id: 2,
      title: "Reforma Laboral - Artículo 152",
      description: "Modifica los requisitos de contratos a plazo fijo y establece nuevas condiciones para terminación de contrato.",
      impact: "Alto",
      category: "Recursos Humanos",
      affectedDocs: 2,
      date: "Ingresado: 05 Ene 2024",
    },
    {
      id: 3,
      title: "Ley de Transparencia Corporativa",
      description: "Requiere divulgación pública de información financiera y estructura organizacional de empresas medianas y grandes.",
      impact: "Medio",
      category: "Financiero / Legal",
      affectedDocs: 4,
      date: "Ingresado: 20 Nov 2023",
    },
  ];

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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Descubrimientos</h1>
        <p className="text-muted-foreground">
          Proyectos de ley que podrían afectar a tu empresa
        </p>
      </div>

      <div className="grid gap-4">
        {discoveries.map((discovery) => (
          <div
            key={discovery.id}
            className="bg-card rounded-lg border border-[hsl(var(--border))] p-6 hover:shadow-md transition-shadow"
          >
            <div className="space-y-4">
              <Link
                to="/discoveries/$id"
                params={{ id: String(discovery.id) }}
                className="flex items-start justify-between gap-4 block"
              >
                <div className="flex-1 space-y-2">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-[hsl(var(--alert-medium))] mt-1 flex-shrink-0" />
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg text-foreground mb-1 hover:text-[hsl(var(--primary))] transition-colors">
                        {discovery.title}
                      </h3>
                      <p className="text-sm text-[hsl(var(--muted-foreground))]">
                        {discovery.description}
                      </p>
                    </div>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded ${getImpactColor(discovery.impact)}`}>
                  Impacto {discovery.impact}
                </span>
              </Link>

              <div className="flex items-center justify-between pt-3 border-t border-[hsl(var(--border))]">
                <div className="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
                  <span>{discovery.category}</span>
                  <span>•</span>
                  <span>{discovery.affectedDocs} documentos afectados</span>
                  <span>•</span>
                  <span>{discovery.date}</span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    className="px-3 py-1.5 text-sm border border-[hsl(var(--border))] rounded-md hover:bg-[hsl(var(--accent))] flex items-center gap-2"
                  >
                    <X className="h-4 w-4" />
                    Descartar
                  </button>
                  <button
                    className="px-3 py-1.5 text-sm bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] rounded-md hover:bg-[hsl(var(--primary))]/90 flex items-center gap-2"
                    onClick={() => navigate({ to: "/tracking" })}
                  >
                    <Eye className="h-4 w-4" />
                    Dar Seguimiento
                  </button>
                  <button
                    className="p-1.5 hover:bg-[hsl(var(--accent))] rounded-md"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
