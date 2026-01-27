export default function Badge({ children, variant = 'primary' }) {
  const variants = {
    primary: 'bg-blue-600 text-blue-200',
    warning: 'bg-yellow-600 text-yellow-200',
    success: 'bg-green-600 text-green-200',
    danger: 'bg-red-600 text-red-200',
    wine: 'text-white',
  }

  const getStyle = () => {
    if (variant === 'wine') return { backgroundColor: '#4A0E2B' }
    return {}
  }

  return (
    <span 
      className={`${variants[variant]} text-xs font-semibold px-2.5 py-1 rounded inline-block`}
      style={getStyle()}
    >
      {children}
    </span>
  )
}