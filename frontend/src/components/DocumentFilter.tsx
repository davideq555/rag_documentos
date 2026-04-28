import { Document } from '../lib/api'

interface DocumentFilterProps {
  documents: Document[]
  selectedIds: string[]
  onToggle: (docId: string, checked: boolean) => void
}

export function DocumentFilter({ documents, selectedIds, onToggle }: DocumentFilterProps) {
  return (
    <div className="space-y-2">
      <p className="text-sm text-slate-400">Filtrar por documentos:</p>
      <div className="flex flex-wrap gap-2">
        {documents.map(doc => (
          <label key={doc.id} className="flex items-center gap-1 cursor-pointer">
            <input
              type="checkbox"
              checked={selectedIds.includes(doc.id)}
              onChange={e => onToggle(doc.id, e.target.checked)}
              className="rounded border-slate-600 bg-slate-900 text-cyan-500 focus:ring-cyan-500"
            />
            <span className="text-sm text-slate-300">{doc.filename}</span>
          </label>
        ))}
      </div>
    </div>
  )
}
