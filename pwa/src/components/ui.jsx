// Small shared UI primitives kept dependency-free.

export function Button({ children, variant = 'primary', className = '', ...props }) {
  const base =
    'w-full rounded-xl px-4 py-3 font-semibold transition active:scale-[0.99] disabled:opacity-50'
  const variants = {
    primary: 'bg-gas-navy text-white hover:bg-gas-navy/90',
    secondary: 'bg-gas-sky text-gas-navy hover:bg-gas-blue/40',
    ghost: 'bg-transparent text-gas-navy border border-gas-navy/30'
  }
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  )
}

export function Card({ children, className = '' }) {
  return (
    <div className={`bg-white rounded-2xl shadow-sm border border-slate-100 p-4 ${className}`}>
      {children}
    </div>
  )
}

export function Field({ label, hint, children }) {
  return (
    <label className="block mb-4">
      <span className="block text-sm font-medium text-slate-700 mb-1">{label}</span>
      {children}
      {hint && <span className="block text-xs text-slate-400 mt-1">{hint}</span>}
    </label>
  )
}

export function TextInput(props) {
  return (
    <input
      {...props}
      className={`w-full rounded-xl border border-slate-300 px-3 py-3 focus:outline-none focus:ring-2 focus:ring-gas-blue ${
        props.className || ''
      }`}
    />
  )
}

export function Banner({ tone = 'info', children }) {
  const tones = {
    info: 'bg-gas-sky text-gas-navy',
    warn: 'bg-amber-100 text-amber-800',
    error: 'bg-red-100 text-red-700',
    success: 'bg-green-100 text-green-800'
  }
  return <div className={`rounded-xl px-3 py-2 text-sm ${tones[tone]}`}>{children}</div>
}
