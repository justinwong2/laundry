/**
 * Powerups page - shop and inventory for powerups.
 *
 * Layout:
 * - Header with title and coin balance
 * - Shop section: Grid of powerups available to buy
 * - Inventory section: Powerups the user owns
 *
 * Key interactions:
 * - Tap "BUY" to purchase a powerup (deducts coins)
 * - Powerups are used from the PingModal (when tapping on a machine)
 */

import { useProfile } from '../hooks/useMachines'
import { usePowerups, useInventory, useBuyPowerup, getPowerupQuantity } from '../hooks/usePowerups'

function Powerups() {
  // Fetch data using React Query hooks
  const { data: profile, isLoading: profileLoading } = useProfile()
  const { data: powerups, isLoading: powerupsLoading } = usePowerups()
  const { data: inventory, isLoading: inventoryLoading } = useInventory()

  // Mutation hook for buying powerups
  const buyMutation = useBuyPowerup()

  /**
   * Handle buying a powerup.
   *
   * Flow:
   * 1. Check if user has enough coins (client-side validation)
   * 2. Call API to buy (server validates again)
   * 3. Show success/error feedback
   * 4. React Query automatically refetches inventory and profile
   */
  const handleBuy = async (powerupType: string, cost: number, name: string) => {
    // Client-side validation (server also validates)
    if (!profile || profile.coins < cost) {
      alert(`Not enough coins! Need ${cost}, have ${profile?.coins ?? 0}`)
      return
    }

    // Confirmation dialog
    const confirmed = window.confirm(
      `Buy ${name} for ${cost} coins?\n\nYou have ${profile.coins} coins.`
    )
    if (!confirmed) return

    try {
      const result = await buyMutation.mutateAsync(powerupType)
      // Show success with new balance
      alert(`${result.message}\n\nNew balance: ${result.new_balance} coins\nYou now have ${result.quantity} ${name}(s)`)
    } catch (error) {
      // Show error from server
      alert(error instanceof Error ? error.message : 'Failed to buy powerup')
    }
  }

  // Loading state
  if (profileLoading || powerupsLoading) {
    return <div className="loading">LOADING SHOP...</div>
  }

  return (
    <div className="powerups">
      {/* Header with coin balance */}
      <header className="header">
        <h1>POWERUPS</h1>
        <div className="coins">{profile?.coins ?? 0} COINS</div>
      </header>

      <main className="content">
        {/* Shop Section */}
        <section className="powerup-shop">
          <h2 className="section-title">SHOP</h2>
          <div className="powerup-grid">
            {powerups?.map((powerup) => {
              const canAfford = (profile?.coins ?? 0) >= powerup.cost
              const owned = getPowerupQuantity(inventory, powerup.type)

              return (
                <div key={powerup.id} className="powerup-card">
                  <div className="powerup-icon">{powerup.icon}</div>
                  <div className="powerup-name">{powerup.name}</div>
                  <div className="powerup-description">{powerup.description}</div>
                  <div className="powerup-cost">{powerup.cost} COINS</div>
                  {owned > 0 && (
                    <div className="powerup-owned">OWNED: {owned}</div>
                  )}
                  <button
                    className={`btn-buy ${!canAfford ? 'disabled' : ''}`}
                    onClick={() => handleBuy(powerup.type, powerup.cost, powerup.name)}
                    disabled={buyMutation.isPending || !canAfford}
                  >
                    {buyMutation.isPending ? 'BUYING...' : canAfford ? 'BUY' : 'NOT ENOUGH'}
                  </button>
                </div>
              )
            })}
          </div>
        </section>

        {/* Inventory Section */}
        <section className="powerup-inventory">
          <h2 className="section-title">YOUR INVENTORY</h2>
          {inventoryLoading ? (
            <div className="loading">LOADING...</div>
          ) : !inventory || inventory.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📦</div>
              <div className="empty-text">NO POWERUPS YET</div>
              <div className="empty-hint">Buy some from the shop above!</div>
            </div>
          ) : (
            <div className="inventory-grid">
              {inventory.map((item) => (
                <div key={item.id} className="inventory-item">
                  <div className="item-icon">{item.powerup_icon}</div>
                  <div className="item-name">{item.powerup_name}</div>
                  <div className="item-quantity">x{item.quantity}</div>
                </div>
              ))}
            </div>
          )}
          <p className="inventory-hint">
            Tap on an IN-USE machine to use your powerups!
          </p>
        </section>
      </main>
    </div>
  )
}

export default Powerups
