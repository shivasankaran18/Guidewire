export default function LoadingSpinner({ size = 'md', text = 'Loading...' }) {
  const sizes = { sm: 'w-5 h-5', md: 'w-8 h-8', lg: 'w-12 h-12' }
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12">
      <div className={`${sizes[size]} border-2 border-shield-500/30 border-t-shield-500 rounded-full animate-spin`} />
      {text && <p className="text-sm text-gray-400">{text}</p>}
    </div>
  )
}
