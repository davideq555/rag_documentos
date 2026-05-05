const API_BASE = '/'

export interface Document {
  id: string
  filename: string
  filetype: string
  status: 'pending' | 'processing' | 'ready' | 'error'
  created_at: string
}

export interface UploadResponse {
  document_id: string
  filename: string
  status: string
  num_chunks: number
}

export interface QueryRequest {
  question: string
  document_ids?: string[]
}

export interface Source {
  content: string
  document_id: string
}

export interface QueryResponse {
  answer: string
  sources: Source[]
}

export const api = {
  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_BASE}upload`, { method: 'POST', body: formData })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Upload failed')
    }
    return res.json()
  },

  async getDocuments(): Promise<Document[]> {
    const res = await fetch(`${API_BASE}documents`)
    if (!res.ok) throw new Error('Failed to fetch documents')
    return res.json()
  },

  async getDocument(id: string): Promise<Document> {
    const res = await fetch(`${API_BASE}documents/${id}`)
    if (!res.ok) throw new Error('Document not found')
    return res.json()
  },

  async deleteDocument(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}documents/${id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete document')
  },

  async query(request: QueryRequest): Promise<QueryResponse> {
    const res = await fetch(`${API_BASE}query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
    if (!res.ok) throw new Error('Query failed')
    return res.json()
  },
}
