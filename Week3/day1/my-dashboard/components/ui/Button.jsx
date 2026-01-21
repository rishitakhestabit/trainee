'use client'

export default function Button({ children, variant = 'primary', size = 'md', onClick }) {
  const variants = {
    primary: 'bg-[#e79cb4] hover:bg-[#913A56] text-white',
    warning: 'bg-[#6b0516da] hover:bg-[#4A0311] text-white',
    success: 'bg-[#570946] hover:bg-[#8C2474] text-white',
    danger: 'bg-[#2e0111] hover:bg-[#662F42] text-white',
    wine: 'hover:bg-opacity-90 text-white',
    gold: 'hover:bg-opacity-90 text-gray-800',
  }

  const sizes = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  }

  const getStyle = () => {
    if (variant === 'wine') return { backgroundColor: '#4A0E2B' }
    if (variant === 'gold') return { backgroundColor: '#D4A574' }
    return {}
  }

  return (
    <button
      onClick={onClick}
      style={getStyle()}
      className={`${variants[variant]} ${sizes[size]} rounded font-medium transition-all duration-200 inline-flex items-center gap-2`}
    >
      {children}
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
      </svg>
    </button>
  )
}