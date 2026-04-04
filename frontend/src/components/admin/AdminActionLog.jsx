import { ScrollText, Shield, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

const demoLogs = [
  { id: 1, action: 'CLAIM_APPROVED', entity_type: 'CLAIM', actor: 'System (Auto)', detail: 'Green-tier claim auto-approved. Payout: ₹1,120 via UPI.', time: '2 min ago', icon: CheckCircle, color: 'text-safety-400' },
  { id: 2, action: 'TRIGGER_FIRED', entity_type: 'TRIGGER', actor: 'System', detail: 'HEAVY_RAIN trigger fired for CHN-VEL-4B. 95.5mm/hr. 3/3 sources agree.', time: '5 min ago', icon: AlertTriangle, color: 'text-alert-400' },
  { id: 3, action: 'CLAIM_REJECTED', entity_type: 'CLAIM', actor: 'Admin Priya', detail: 'Red-tier claim rejected. GPS spoof detected (velocity: 145 km/h). Strike applied.', time: '12 min ago', icon: XCircle, color: 'text-danger-400' },
  { id: 4, action: 'FRAUD_RING_DETECTED', entity_type: 'FRAUD_RING', actor: 'DBSCAN Engine', detail: 'Ring of 7 accounts detected in CHN-VEL-4B. 85% confidence. Accounts frozen.', time: '25 min ago', icon: AlertTriangle, color: 'text-danger-400' },
  { id: 5, action: 'POLICY_ACTIVATED', entity_type: 'POLICY', actor: 'Worker (Ravi Kumar)', detail: 'Standard Shield activated. Premium: ₹59. Coverage: ₹6,300.', time: '1 hr ago', icon: Shield, color: 'text-shield-400' },
  { id: 6, action: 'APPEAL_APPROVED', entity_type: 'CLAIM', actor: 'Admin Priya', detail: 'Amber claim appeal approved after manual review. ₹50 goodwill credit added.', time: '1 hr ago', icon: CheckCircle, color: 'text-safety-400' },
  { id: 7, action: 'WORKER_REGISTERED', entity_type: 'WORKER', actor: 'System', detail: 'New worker registered: Vijay Singh (ZW890123). 2-week probation started.', time: '2 hr ago', icon: Shield, color: 'text-shield-400' },
  { id: 8, action: 'CLAIM_APPROVED', entity_type: 'CLAIM', actor: 'System (Auto)', detail: 'Green-tier claim auto-approved for FLOOD trigger. Payout: ₹1,600.', time: '3 hr ago', icon: CheckCircle, color: 'text-safety-400' },
]

export default function AdminActionLog() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <ScrollText className="w-5 h-5 text-shield-400" /> Immutable Audit Log
        </h2>
        <span className="text-xs text-gray-400">SHA-256 hash chain verified</span>
      </div>

      <div className="glass-card overflow-hidden">
        <div className="divide-y divide-white/5">
          {demoLogs.map(log => (
            <div key={log.id} className="flex items-start gap-4 p-4 hover:bg-white/5 transition-colors">
              <div className={`w-9 h-9 rounded-lg bg-white/10 flex items-center justify-center shrink-0 mt-0.5`}>
                <log.icon className={`w-4 h-4 ${log.color}`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-sm font-semibold text-white">{log.action.replace(/_/g, ' ')}</span>
                  <span className="badge-blue text-[9px]">{log.entity_type}</span>
                </div>
                <p className="text-sm text-gray-400">{log.detail}</p>
                <p className="text-xs text-gray-500 mt-1">By: {log.actor} • {log.time}</p>
              </div>
              <div className="text-[10px] text-gray-600 font-mono mt-1 shrink-0">
                #{String(log.id).padStart(4, '0')}
              </div>
            </div>
          ))}
        </div>
      </div>

      <p className="text-xs text-gray-500 text-center">
        🔒 All entries are immutable and verified via SHA-256 hash chain. Tampering is detectable.
      </p>
    </div>
  )
}
