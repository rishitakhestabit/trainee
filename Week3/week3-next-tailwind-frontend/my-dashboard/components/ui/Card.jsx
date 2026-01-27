export default function Card({ title, children, variant = 'primary' }) {
  const variants = {
    primary: { bg: '#e79cb4', text: 'text-white' },
    warning: { bg: '#6b0516da', text: 'text-white' },
    success: { bg: '#570946', text: 'text-white' },
    danger: { bg: '#2e0111', text: 'text-white' },
  }

  const currentVariant = variants[variant]

  return (
    <div className="rounded-lg shadow-lg overflow-hidden">
      {/* Card Header */}
      <div 
        className={`px-6 py-4 ${currentVariant.text} font-semibold`}
        style={{ backgroundColor: currentVariant.bg }}
      >
        {title}
      </div>
      
      {/* Card Body */}
      <div className="bg-white px-6 py-4">
        {children}
      </div>
    </div>
  )
}