/**
 * Format INR currency
 */
export function formatCurrency(amount, decimals = 0) {
  if (amount === null || amount === undefined) return '₹0'
  return `₹${Number(amount).toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`
}

export function formatCompact(amount) {
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`
  return formatCurrency(amount)
}
