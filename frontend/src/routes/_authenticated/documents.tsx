import { createFileRoute } from "@tanstack/react-router";
import { FileText, Upload, Calendar, AlertCircle, Loader2, Trash2, CheckCircle2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import {
  detectConflicts,
  listDocuments,
  deleteDocument,
  type DetectConflictsResponse,
  type DocumentoList
} from "../../services/api/conflictDetector";
import { ConfirmDialog } from "../../components/ConfirmDialog";
import { useDiscoveries } from "../../contexts/DiscoveriesContext";

export const Route = createFileRoute("/_authenticated/documents")({
  component: Documents,
});

function Documents() {
  const { setPendingCount } = useDiscoveries();
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<DetectConflictsResponse | null>(null);
  const [documents, setDocuments] = useState<DocumentoList[]>([]);
  const [showUploadMenu, setShowUploadMenu] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<{ id: number; nombre: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Cargar documentos al montar el componente
  useEffect(() => {
    loadDocuments();
  }, []);

  // Cerrar el menú al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showUploadMenu && !(event.target as Element).closest('.relative')) {
        setShowUploadMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showUploadMenu]);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const docs = await listDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error al cargar documentos:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validar que sea un PDF
    if (file.type !== 'application/pdf') {
      setUploadError('Por favor selecciona un archivo PDF');
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setDetectionResult(null);

    try {
      const result = await detectConflicts(file);
      setDetectionResult(result);
      // Actualizar el contador de pendientes con el valor del servidor
      setPendingCount(result.pending_discoveries_count);
      // Recargar la lista de documentos
      await loadDocuments();
    } catch (error) {
      console.error('Error al subir documento:', error);
      setUploadError(error instanceof Error ? error.message : 'Error desconocido al procesar el documento');
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDeleteDocument = (documentId: number, documentName: string) => {
    setDocumentToDelete({ id: documentId, nombre: documentName });
    setShowDeleteDialog(true);
  };

  const confirmDeleteDocument = async () => {
    if (!documentToDelete) return;

    try {
      await deleteDocument(documentToDelete.id);
      // Recargar la lista de documentos
      await loadDocuments();
    } catch (error) {
      console.error('Error al eliminar documento:', error);
      setUploadError(error instanceof Error ? error.message : 'Error al eliminar el documento');
    } finally {
      setDocumentToDelete(null);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
    setShowUploadMenu(false);
  };

  const handleUseSamplePDF = async () => {
    setShowUploadMenu(false);
    setIsUploading(true);
    setUploadError(null);
    setDetectionResult(null);

    try {
      // Importar el PDF de prueba dinámicamente
      const pdfModule = await import('../../assets/memoria_cristaleria.pdf?url');
      const response = await fetch(pdfModule.default);
      const blob = await response.blob();
      const file = new File([blob], 'memoria_cristaleria.pdf', { type: 'application/pdf' });

      const result = await detectConflicts(file);
      setDetectionResult(result);
      // Actualizar el contador de pendientes con el valor del servidor
      setPendingCount(result.pending_discoveries_count);
      await loadDocuments();
    } catch (error) {
      console.error('Error al usar PDF de prueba:', error);
      setUploadError(error instanceof Error ? error.message : 'Error desconocido al procesar el documento');
    } finally {
      setIsUploading(false);
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Documentos</h1>
          <p className="text-muted-foreground">
            Perfil corporativo y documentación analizada
          </p>
        </div>
        <div className="relative">
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileUpload}
            className="hidden"
          />
          <button
            onClick={() => setShowUploadMenu(!showUploadMenu)}
            disabled={isUploading}
            className="px-4 py-2 bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] rounded-md hover:bg-[hsl(var(--primary))]/90 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Procesando...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                Subir Documento
              </>
            )}
          </button>

          {/* Menú desplegable */}
          {showUploadMenu && !isUploading && (
            <div className="absolute right-0 mt-2 w-56 bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-md shadow-lg z-10">
              <button
                onClick={handleUseSamplePDF}
                className="w-full text-left px-4 py-3 hover:bg-[hsl(var(--accent))] flex items-center gap-2 border-b border-[hsl(var(--border))]"
              >
                <FileText className="h-4 w-4" />
                <div>
                  <div className="font-medium text-sm">Usar PDF de prueba</div>
                  <div className="text-xs text-[hsl(var(--muted-foreground))]">memoria_cristaleria.pdf</div>
                </div>
              </button>
              <button
                onClick={handleUploadClick}
                className="w-full text-left px-4 py-3 hover:bg-[hsl(var(--accent))] flex items-center gap-2"
              >
                <Upload className="h-4 w-4" />
                <div className="font-medium text-sm">Elegir mi propio archivo</div>
              </button>
            </div>
          )}
        </div>
      </div>

      {uploadError && (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-md p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold">Error al procesar documento</h3>
            <p className="text-sm mt-1">{uploadError}</p>
          </div>
        </div>
      )}

      {detectionResult && (
        <div className="bg-green-50 border border-green-200 text-green-800 rounded-md p-3 flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 flex-shrink-0" />
          <p className="text-sm">Documento procesado exitosamente</p>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[hsl(var(--primary))]" />
          <span className="ml-3 text-muted-foreground">Cargando documentos...</span>
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-12 bg-card rounded-lg border border-[hsl(var(--border))]">
          <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
          <h3 className="text-lg font-semibold text-foreground mb-2">No hay documentos</h3>
          <p className="text-muted-foreground">
            Comienza subiendo tu primer documento para detectar conflictos
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {documents.map((doc) => (
            <div key={doc.id} className="bg-card rounded-lg border border-[hsl(var(--border))] p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="p-3 bg-[hsl(var(--primary))]/10 rounded-lg">
                    <FileText className="h-6 w-6 text-[hsl(var(--primary))]" />
                  </div>
                  <div className="space-y-1 flex-1">
                    <h3 className="font-semibold text-foreground">{doc.nombre}</h3>
                    <div className="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(doc.fecha_carga)}
                      </span>
                      <span>
                        {doc.cantidad_descubrimientos} descubrimiento(s)
                      </span>
                    </div>
                    {doc.cantidad_descubrimientos > 0 && (
                      <span className="inline-block mt-2 px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
                        Conflictos detectados
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 text-xs bg-[hsl(var(--status-active))] text-white rounded">
                    Procesado
                  </span>
                  <button
                    onClick={() => handleDeleteDocument(doc.id, doc.nombre)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                    title="Eliminar documento"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        isOpen={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        onConfirm={confirmDeleteDocument}
        title="Eliminar documento"
        message={`¿Estás seguro de eliminar el documento "${documentToDelete?.nombre}"? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        variant="danger"
      />
    </div>
  );
}
