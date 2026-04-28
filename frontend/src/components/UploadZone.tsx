import { useState, useCallback, useRef } from 'react'

interface UploadZoneProps {
  onUpload: (file: File) => void
  isLoading: boolean
}

const ALLOWED_TYPES = ['.pdf', '.docx', '.md', '.txt']

export function UploadZone({ onUpload, isLoading }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) onUpload(file)
  }, [onUpload])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onUpload(file)
  }, [onUpload])

  const handleClick = useCallback(() => {
    inputRef.current?.click()
  }, [])

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        isDragging ? 'border-cyan-400 bg-cyan-400/10' : 'border-slate-600 hover:border-slate-500'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ALLOWED_TYPES.join(',')}
        onChange={handleChange}
        className="hidden"
      />
      {isLoading ? (
        <p className="text-cyan-400">Procesando...</p>
      ) : (
        <>
          <p className="text-slate-400">Arrastra archivos aquí o haz clic para seleccionar</p>
          <p className="text-xs text-slate-500 mt-2">PDF, DOCX, MD, TXT</p>
        </>
      )}
    </div>
  )
}
