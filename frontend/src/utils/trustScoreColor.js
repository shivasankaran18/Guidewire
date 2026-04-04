/**
 * Trust Score → Color mapping
 */
export function trustScoreColor(score) {
  if (score >= 80) return { bg: 'bg-safety-500/20', text: 'text-safety-400', border: 'border-safety-500/30', label: 'Verified Partner ⭐' }
  if (score >= 60) return { bg: 'bg-shield-500/20', text: 'text-shield-400', border: 'border-shield-500/30', label: 'Trusted' }
  if (score >= 40) return { bg: 'bg-alert-500/20', text: 'text-alert-400', border: 'border-alert-500/30', label: 'Standard' }
  return { bg: 'bg-danger-500/20', text: 'text-danger-400', border: 'border-danger-500/30', label: 'Under Review' }
}

export function fraudTierColor(tier) {
  const map = {
    GREEN: { bg: 'bg-safety-500/20', text: 'text-safety-400', label: '🟢 Auto-Approved' },
    AMBER: { bg: 'bg-alert-500/20', text: 'text-alert-400', label: '🟡 Soft Verify' },
    RED: { bg: 'bg-danger-500/20', text: 'text-danger-400', label: '🔴 Manual Review' },
  }
  return map[tier] || map.GREEN
}

export function riskLevelColor(level) {
  const map = {
    LOW: 'text-safety-400',
    MEDIUM: 'text-alert-400',
    HIGH: 'text-danger-400',
    CRITICAL: 'text-danger-300 font-bold',
  }
  return map[level] || map.MEDIUM
}
