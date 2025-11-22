import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/settings")({
  component: Settings,
});

function Settings() {
  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Configuración</h1>
        <p className="text-muted-foreground">
          Administra tu cuenta y preferencias
        </p>
      </div>

      <div className="bg-card rounded-lg border border-[hsl(var(--border))]">
        <div className="p-6 border-b border-[hsl(var(--border))]">
          <h3 className="text-lg font-semibold">Información de la Empresa</h3>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Datos corporativos para personalizar el análisis legislativo
          </p>
        </div>
        <div className="p-6 space-y-4">
          <div className="space-y-2">
            <label htmlFor="company" className="text-sm font-medium">Nombre de la Empresa</label>
            <input
              id="company"
              type="text"
              placeholder="TechCorp S.A."
              defaultValue="TechCorp S.A."
              className="w-full px-3 py-2 border border-[hsl(var(--input))] rounded-md bg-background"
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="industry" className="text-sm font-medium">Industria</label>
            <input
              id="industry"
              type="text"
              placeholder="Tecnología"
              defaultValue="Tecnología y Servicios"
              className="w-full px-3 py-2 border border-[hsl(var(--input))] rounded-md bg-background"
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="employees" className="text-sm font-medium">Número de Empleados</label>
            <input
              id="employees"
              type="number"
              placeholder="150"
              defaultValue="150"
              className="w-full px-3 py-2 border border-[hsl(var(--input))] rounded-md bg-background"
            />
          </div>
          <button className="px-4 py-2 bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] rounded-md hover:bg-[hsl(var(--primary))]/90">
            Guardar Cambios
          </button>
        </div>
      </div>

      <div className="bg-card rounded-lg border border-[hsl(var(--border))]">
        <div className="p-6 border-b border-[hsl(var(--border))]">
          <h3 className="text-lg font-semibold">Notificaciones</h3>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Configura cómo y cuándo recibir alertas
          </p>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">Nuevos Descubrimientos</p>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                Recibe alertas cuando se detecten nuevos proyectos de ley relevantes
              </p>
            </div>
            <button className="px-3 py-1.5 text-sm border border-[hsl(var(--border))] rounded-md hover:bg-[hsl(var(--accent))]">
              Activado
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">Actualizaciones de Seguimiento</p>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                Notificaciones sobre cambios en proyectos que sigues
              </p>
            </div>
            <button className="px-3 py-1.5 text-sm border border-[hsl(var(--border))] rounded-md hover:bg-[hsl(var(--accent))]">
              Activado
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
