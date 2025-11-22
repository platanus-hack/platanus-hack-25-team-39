import { createFileRoute } from "@tanstack/react-router";
import { FileText, Upload, Calendar } from "lucide-react";

export const Route = createFileRoute("/_authenticated/documents")({
  component: Documents,
});

function Documents() {
  const documents = [
    {
      name: "Memoria Anual 2023",
      type: "Reporte Corporativo",
      uploadDate: "15 Ene 2024",
      size: "2.4 MB",
      status: "Procesado",
    },
    {
      name: "Contrato Marco de Servicios",
      type: "Legal",
      uploadDate: "12 Ene 2024",
      size: "890 KB",
      status: "Procesado",
    },
    {
      name: "Política de Privacidad Interna",
      type: "Compliance",
      uploadDate: "10 Ene 2024",
      size: "456 KB",
      status: "Procesado",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Documentos</h1>
          <p className="text-muted-foreground">
            Perfil corporativo y documentación analizada
          </p>
        </div>
        <button className="px-4 py-2 bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] rounded-md hover:bg-[hsl(var(--primary))]/90 flex items-center gap-2">
          <Upload className="h-4 w-4" />
          Subir Documento
        </button>
      </div>

      <div className="grid gap-4">
        {documents.map((doc, index) => (
          <div key={index} className="bg-card rounded-lg border border-[hsl(var(--border))] p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <div className="p-3 bg-[hsl(var(--primary))]/10 rounded-lg">
                  <FileText className="h-6 w-6 text-[hsl(var(--primary))]" />
                </div>
                <div className="space-y-1">
                  <h3 className="font-semibold text-foreground">{doc.name}</h3>
                  <div className="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {doc.uploadDate}
                    </span>
                    <span>{doc.size}</span>
                  </div>
                  <span className="inline-block mt-2 px-2 py-1 text-xs bg-[hsl(var(--secondary))] text-[hsl(var(--secondary-foreground))] rounded">
                    {doc.type}
                  </span>
                </div>
              </div>
              <span className="px-2 py-1 text-xs bg-[hsl(var(--status-active))] text-white rounded">
                {doc.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
