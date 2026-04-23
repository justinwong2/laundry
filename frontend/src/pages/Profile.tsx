import { useProfile, useTransactions } from '../hooks/useMachines'

function Profile() {
  const { data: profile, isLoading: profileLoading } = useProfile()
  const { data: transactions, isLoading: transactionsLoading } = useTransactions()

  const formatReason = (reason: string) => {
    switch (reason) {
      case 'claim':
        return 'Claimed machine'
      case 'release':
        return 'Released machine'
      case 'ping_sent':
        return 'Pinged user'
      case 'ping_received':
        return 'Got pinged'
      default:
        return reason
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (profileLoading) {
    return <div className="loading">Loading profile...</div>
  }

  return (
    <div className="profile">
      <header className="header">
        <h1>👤 Profile</h1>
      </header>

      <main className="content">
        {profile && (
          <div className="profile-card">
            <div className="profile-info">
              <div className="username">@{profile.username || 'Anonymous'}</div>
              <div className="block">Block {profile.block}</div>
            </div>
            <div className="coin-balance">
              <div className="coin-icon">💰</div>
              <div className="coin-amount">{profile.coins}</div>
              <div className="coin-label">coins</div>
            </div>
          </div>
        )}

        <div className="transactions-section">
          <h2>Transaction History</h2>
          {transactionsLoading ? (
            <div className="loading">Loading transactions...</div>
          ) : !transactions || transactions.length === 0 ? (
            <div className="empty-state">No transactions yet</div>
          ) : (
            <ul className="transaction-list">
              {transactions.map((tx) => (
                <li key={tx.id} className="transaction-item">
                  <div className="tx-info">
                    <div className="tx-reason">{formatReason(tx.reason)}</div>
                    <div className="tx-date">{formatDate(tx.created_at)}</div>
                  </div>
                  <div className={`tx-amount ${tx.amount > 0 ? 'positive' : 'negative'}`}>
                    {tx.amount > 0 ? '+' : ''}
                    {tx.amount} 🪙
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  )
}

export default Profile
