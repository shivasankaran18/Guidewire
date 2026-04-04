export default function ConfirmModal({ isOpen, title, message, onConfirm, onCancel, confirmText = 'Confirm', danger = false }) {
  if (!isOpen) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in" onClick={onCancel}>
      <div className="glass-card p-6 max-w-md w-full mx-4 animate-scale-in" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
        <p className="text-gray-400 text-sm mb-6">{message}</p>
        <div className="flex gap-3 justify-end">
          <button onClick={onCancel} className="btn-secondary text-sm px-4 py-2">Cancel</button>
          <button onClick={onConfirm} className={`${danger ? 'btn-danger' : 'btn-primary'} text-sm px-4 py-2`}>{confirmText}</button>
        </div>
      </div>
    </div>
  )
}
