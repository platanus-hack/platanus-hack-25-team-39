import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Eye, X, ArrowLeft, FileText, Scale } from "lucide-react";

export const Route = createFileRoute("/_authenticated/discoveries/$id")({
  component: ProjectDetail,
});

function ProjectDetail() {
  const navigate = useNavigate();
  const { id } = Route.useParams();

  // Mock data - en producción vendría de una API
  const project = {
    title: "Ley de Protección de Datos Personales",
    status: "En Comisión - Cámara de Diputados",
    impact: "Alto",
    category: "Legal / Compliance",
    dateIntroduced: "10 Diciembre 2023",
    fullText:
      "Esta ley tiene por objeto regular el tratamiento de los datos personales en posesión de particulares y entidades gubernamentales, con el fin de proteger los derechos de privacidad y autodeterminación informativa de las personas...",
    aiAnalysis:
      "Este proyecto de ley impacta directamente las operaciones de tu empresa en los siguientes aspectos: (1) Requerirá implementar nuevos controles de acceso y cifrado para datos de clientes, (2) Obligará a obtener consentimiento explícito para cualquier tratamiento de datos personales, (3) Establecerá responsabilidad administrativa con multas de hasta 5% de facturación anual por incumplimiento. Se recomienda iniciar auditoría de prácticas actuales de manejo de datos y preparar plan de implementación con plazos de 6 meses desde promulgación.",
    affectedDocuments: [
      {
        name: "Política de Privacidad Interna",
        chunk:
          "...La empresa recopila y procesa datos personales de clientes incluyendo nombre, email, dirección, número de teléfono y datos de pago. Esta información se utiliza para procesamiento de pedidos, comunicaciones de marketing y análisis de comportamiento del usuario...",
        relevance: 95,
      },
      {
        name: "Manual de RRHH",
        chunk:
          "...Se mantienen registros de empleados que incluyen datos personales, información médica, evaluaciones de desempeño y datos bancarios para procesamiento de nómina. El acceso a esta información está limitado al departamento de Recursos Humanos...",
        relevance: 87,
      },
      {
        name: "Contrato Marco de Servicios",
        chunk:
          "...El proveedor tendrá acceso a datos de clientes finales únicamente para efectos de prestación del servicio contratado, comprometiéndose a mantener confidencialidad de la información...",
        relevance: 78,
      },
    ],
    lawChunks: [
      {
        article: "Artículo 7",
        content:
          "El tratamiento de datos personales deberá contar con el consentimiento previo, expreso e informado del titular. El consentimiento deberá constar por escrito o por medios electrónicos equivalentes.",
      },
      {
        article: "Artículo 15",
        content:
          "Los responsables del tratamiento de datos deberán implementar medidas de seguridad técnicas y organizativas apropiadas para proteger los datos personales contra el acceso no autorizado, la pérdida, alteración o divulgación.",
      },
    ],
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

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate({ to: "/discoveries" })}
          className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-[hsl(var(--muted))] rounded-md transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Volver
        </button>
      </div>

      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-[hsl(var(--foreground))]">
            {project.title}
          </h1>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 text-sm border border-[hsl(var(--border))] rounded-md">
              {project.status}
            </span>
            <span
              className={`px-3 py-1 text-sm rounded-md ${getImpactColor(project.impact)}`}
            >
              Impacto {project.impact}
            </span>
            <span className="text-sm text-[hsl(var(--muted-foreground))]">
              {project.category}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-4 py-2 text-sm border border-[hsl(var(--border))] rounded-md hover:bg-[hsl(var(--muted))] transition-colors">
            <X className="h-4 w-4" />
            Descartar
          </button>
          <button className="flex items-center gap-2 px-4 py-2 text-sm bg-[hsl(var(--primary))] text-white rounded-md hover:opacity-90 transition-opacity">
            <Eye className="h-4 w-4" />
            Dar Seguimiento
          </button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Documentos Afectados */}
        <div className="bg-[hsl(var(--card))] rounded-lg border border-[hsl(var(--border))] p-6">
          <div className="mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-1">
              <FileText className="h-5 w-5" />
              Documentos Afectados
            </h2>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              Secciones de tus documentos que se relacionan con este proyecto de
              ley
            </p>
          </div>
          <div className="space-y-4">
            {project.affectedDocuments.map((doc, index) => (
              <div
                key={index}
                className="space-y-2 pb-4 border-b border-[hsl(var(--border))] last:border-0 last:pb-0"
              >
                <div className="flex items-start justify-between">
                  <p className="font-semibold text-sm">{doc.name}</p>
                  <span className="px-2 py-1 text-xs bg-[hsl(var(--muted))] rounded">
                    {doc.relevance}% relevancia
                  </span>
                </div>
                <p className="text-sm text-[hsl(var(--muted-foreground))] italic bg-[hsl(var(--muted))]/30 p-3 rounded">
                  {doc.chunk}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Artículos Relevantes */}
        <div className="bg-[hsl(var(--card))] rounded-lg border border-[hsl(var(--border))] p-6">
          <div className="mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-1">
              <Scale className="h-5 w-5" />
              Artículos Relevantes del Proyecto
            </h2>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              Secciones del proyecto de ley que impactan tu operación
            </p>
          </div>
          <div className="space-y-4">
            {project.lawChunks.map((chunk, index) => (
              <div
                key={index}
                className="space-y-2 pb-4 border-b border-[hsl(var(--border))] last:border-0 last:pb-0"
              >
                <p className="font-semibold text-sm text-[hsl(var(--primary))]">
                  {chunk.article}
                </p>
                <p className="text-sm text-[hsl(var(--muted-foreground))] bg-[hsl(var(--primary))]/5 p-3 rounded">
                  {chunk.content}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Análisis de Impacto */}
      <div className="bg-[hsl(var(--card))] rounded-lg border border-[hsl(var(--border))] p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold mb-1">Análisis de Impacto (IA)</h2>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Análisis generado automáticamente sobre cómo este proyecto afecta tu
            empresa
          </p>
        </div>
        <div className="prose prose-sm max-w-none">
          <p className="text-[hsl(var(--foreground))] leading-relaxed">
            {project.aiAnalysis}
          </p>
        </div>
      </div>

      {/* Información General */}
      <div className="bg-[hsl(var(--card))] rounded-lg border border-[hsl(var(--border))] p-6">
        <h2 className="text-lg font-semibold mb-4">Información General</h2>
        <div className="space-y-4">
          <div>
            <p className="text-sm font-medium text-[hsl(var(--muted-foreground))] mb-1">
              Fecha de Ingreso
            </p>
            <p className="text-[hsl(var(--foreground))]">
              {project.dateIntroduced}
            </p>
          </div>
          <hr className="border-[hsl(var(--border))]" />
          <div>
            <p className="text-sm font-medium text-[hsl(var(--muted-foreground))] mb-1">
              Estado Actual
            </p>
            <p className="text-[hsl(var(--foreground))]">{project.status}</p>
          </div>
          <hr className="border-[hsl(var(--border))]" />
          <div>
            <p className="text-sm font-medium text-[hsl(var(--muted-foreground))] mb-2">
              Texto del Proyecto
            </p>
            <p className="text-sm text-[hsl(var(--muted-foreground))] leading-relaxed">
              {project.fullText}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
