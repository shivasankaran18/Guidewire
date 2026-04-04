import { useState, useRef, useEffect } from 'react'

export default function OTPInput({ length = 6, onComplete }) {
  const [values, setValues] = useState(Array(length).fill(''))
  const refs = useRef([])

  const handleChange = (i, val) => {
    if (!/^\d*$/.test(val)) return
    const next = [...values]
    next[i] = val.slice(-1)
    setValues(next)
    if (val && i < length - 1) refs.current[i + 1]?.focus()
    const otp = next.join('')
    if (otp.length === length) onComplete?.(otp)
  }

  const handleKeyDown = (i, e) => {
    if (e.key === 'Backspace' && !values[i] && i > 0) refs.current[i - 1]?.focus()
  }

  return (
    <div className="flex gap-3 justify-center">
      {values.map((v, i) => (
        <input
          key={i}
          ref={el => refs.current[i] = el}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={v}
          onChange={e => handleChange(i, e.target.value)}
          onKeyDown={e => handleKeyDown(i, e)}
          className="w-12 h-14 text-center text-2xl font-bold bg-white/5 border border-white/20 rounded-xl text-white focus:border-shield-500 focus:ring-2 focus:ring-shield-500/20 outline-none transition-all"
        />
      ))}
    </div>
  )
}
