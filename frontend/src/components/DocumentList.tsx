import { Document } from '../lib/api'

interface DocumentListProps {
  documents: Document[]
  isLoading: boolean
  onDelete: (id: string) => void
}

export function DocumentList({ documents, isLoading, onDelete }: DocumentListProps) {
  if (isLoading) return <p className="text-slate-400">Cargando...</p>
  if (documents.length === 0) return <p className="text-slate-500">No hay documentos</p>

  return (
    <div className="space-y-2">
      {documents.map(doc => (
        <div key={doc.id} className="flex items-center justify-between bg-slate-900 rounded-lg p-3">
          <div className="flex items-center gap-3">
            <span className="font-medium">{doc.filename}</span>
            <span className={`text-xs px-2 py-0.5 rounded ${
              doc.status === 'ready' ? 'bg-green-600' :
              doc.status === 'error' ? 'bg-red-600' :
              doc.status === 'pending' ? 'bg-yellow-600' :
              'bg-blue-600'
            }`}>
              {doc.status}
            </span>
            <span className="text-xs text-slate-500">.{doc.filetype}</span>
          </div>
          <button
            onClick={() => onDelete(doc.id)}
            className="text-red-400 hover:text-red-300 text-sm"
          >
            Eliminar
          </button>
        </div>
      ))}
    </div>
  )
}
