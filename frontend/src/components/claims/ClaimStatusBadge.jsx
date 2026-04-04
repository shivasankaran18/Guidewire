import { fraudTierColor } from '../../utils/trustScoreColor'

export default function ClaimStatusBadge({ status, fraudTier }) {
  const tier = fraudTierColor(fraudTier || 'GREEN')
  const statusMap = {
    PAID: { class: 'badge-green', label: '✓ Paid' },
    APPROVED: { class: 'badge-green', label: '✓ Approved' },
    PENDING: { class: 'badge-amber', label: '⏳ Pending' },
    REJECTED: { class: 'badge-red', label: '✗ Rejected' },
    APPEALED: { class: 'badge-blue', label: '⚡ Appealed' },
  }
  const s = statusMap[status] || statusMap.PENDING

  return (
    <div className="flex items-center gap-2">
      <span className={s.class}>{s.label}</span>
      <span className={`badge ${tier.bg} ${tier.text}`}>{tier.label}</span>
    </div>
  )
}
