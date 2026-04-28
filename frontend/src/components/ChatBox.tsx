import { useState, useCallback, KeyboardEvent } from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{ content: string; document_id: string }>
}

interface ChatBoxProps {
  messages: Message[]
  onQuery: (question: string) => void
  isLoading: boolean
}

export function ChatBox({ messages, onQuery, isLoading }: ChatBoxProps) {
  const [input, setInput] = useState('')

  const handleSubmit = useCallback(() => {
    if (input.trim() && !isLoading) {
      onQuery(input.trim())
      setInput('')
    }
  }, [input, onQuery, isLoading])

  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }, [handleSubmit])

  return (
    <div className="space-y-4">
      <div className="h-64 overflow-y-auto bg-slate-900 rounded-lg p-4 space-y-3">
        {messages.length === 0 ? (
          <p className="text-slate-500 text-center">Escribe una pregunta sobre tus documentos...</p>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                msg.role === 'user' ? 'bg-cyan-600 text-white' : 'bg-slate-700 text-slate-100'
              }`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-600 text-xs text-slate-400">
                    <p className="font-semibold">Fuentes:</p>
                    {msg.sources.map((s, j) => (
                      <p key={j} className="truncate">• {s.content.substring(0, 100)}...</p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-700 rounded-lg px-4 py-2">
              <p className="text-slate-400 animate-pulse">Procesando...</p>
            </div>
          </div>
        )}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe tu pregunta..."
          disabled={isLoading}
          className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-cyan-500 disabled:opacity-50"
        />
        <button
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading}
          className="bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-700 disabled:cursor-not-allowed px-6 py-2 rounded-lg font-medium transition-colors"
        >
          Enviar
        </button>
      </div>
    </div>
  )
}
