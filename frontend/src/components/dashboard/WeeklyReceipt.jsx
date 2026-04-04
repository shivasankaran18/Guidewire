import { formatCurrency } from '../../utils/formatCurrency'
import { Receipt } from 'lucide-react'

export default function WeeklyReceipt({ premiumPaid = 59, claimsPaid = 2, totalPayout = 1200 }) {
  return (
    <div className="glass-card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Receipt className="w-5 h-5 text-shield-400" />
        <p className="text-xs text-gray-400 uppercase tracking-wider">Weekly Summary</p>
      </div>
      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Premium Paid</span>
          <span className="text-white font-medium">{formatCurrency(premiumPaid)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Claims This Week</span>
          <span className="text-white font-medium">{claimsPaid}</span>
        </div>
        <div className="flex justify-between text-sm border-t border-white/10 pt-3">
          <span className="text-gray-400">Total Received</span>
          <span className="text-safety-400 font-bold text-lg">{formatCurrency(totalPayout)}</span>
        </div>
      </div>
    </div>
  )
}
