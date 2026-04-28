import { useState, useCallback } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, Document, QueryRequest } from './lib/api'
import { UploadZone } from './components/UploadZone'
import { ChatBox } from './components/ChatBox'
import { DocumentList } from './components/DocumentList'
import { DocumentFilter } from './components/DocumentFilter'

export default function App() {
  const queryClient = useQueryClient()
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([])
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string; sources?: Array<{ content: string; document_id: string }> }>>([])

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: api.getDocuments,
  })

  const uploadMutation = useMutation({
    mutationFn: api.uploadDocument,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] }),
  })

  const queryMutation = useMutation({
    mutationFn: api.query,
    onSuccess: (data) => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      }])
    },
  })

  const handleUpload = useCallback((file: File) => {
    uploadMutation.mutate(file)
  }, [uploadMutation])

  const handleQuery = useCallback((question: string) => {
    setMessages(prev => [...prev, { role: 'user', content: question }])
    const request: QueryRequest = {
      question,
      document_ids: selectedDocIds.length > 0 ? selectedDocIds : undefined,
    }
    queryMutation.mutate(request)
  }, [selectedDocIds, queryMutation])

  const handleDelete = useCallback((id: string) => {
    api.deleteDocument(id).then(() => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      setSelectedDocIds(prev => prev.filter(docId => docId !== id))
    })
  }, [queryClient])

  const handleToggleFilter = useCallback((docId: string, checked: boolean) => {
    setSelectedDocIds(prev =>
      checked ? [...prev, docId] : prev.filter(id => id !== docId)
    )
  }, [])

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-center text-cyan-400">RAG Documentos</h1>

        <div className="bg-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-cyan-300">Subir Documentos</h2>
          <UploadZone onUpload={handleUpload} isLoading={uploadMutation.isPending} />
          {uploadMutation.isError && (
            <p className="text-red-400 text-sm">{uploadMutation.error.message}</p>
          )}
        </div>

        <div className="bg-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-cyan-300">Consultar</h2>
          <ChatBox
            messages={messages}
            onQuery={handleQuery}
            isLoading={queryMutation.isPending}
          />
          {documents.length > 0 && (
            <DocumentFilter
              documents={documents}
              selectedIds={selectedDocIds}
              onToggle={handleToggleFilter}
            />
          )}
        </div>

        <div className="bg-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-cyan-300">Documentos</h2>
          <DocumentList
            documents={documents}
            isLoading={isLoading}
            onDelete={handleDelete}
          />
        </div>
      </div>
    </div>
  )
}
