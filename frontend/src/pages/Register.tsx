import { useState } from 'react'
import { api } from '../api/client'
import { useQueryClient } from '@tanstack/react-query'

const BLOCKS = ['A', 'B', 'C', 'D', 'E']

export default function Register() {
    const [selectedBlock, setSelectedBlock] = useState<string>('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const queryClient = useQueryClient()

    const handleRegister = async () => {
        if (!selectedBlock) return
        setLoading(true)
        setError(null)

        try {
            await api.register(selectedBlock)
            // Force a refetch of the profile now that they are registered
            queryClient.invalidateQueries({ queryKey: ['profile'] })
        } catch (err: any) {
            setError(err.message || 'Failed to register')
            setLoading(false)
        }
    }

    return (
        <div className="home" style={{ padding: '24px', textAlign: 'center' }}>
            <h1>Welcome to Laundry Bot</h1>
            <p style={{ color: 'var(--hint-color)', marginTop: '8px' }}>
                Let's get you set up so you can track machines and get reminders.
            </p>

            <div style={{ marginTop: '32px', textAlign: 'left' }}>
                <p style={{ fontWeight: '600', marginBottom: '16px' }}>Which block do you live in?</p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
                    {BLOCKS.map(block => (
                        <button
                            key={block}
                            className={`btn-secondary ${selectedBlock === block ? 'btn-primary' : ''}`}
                            style={{ padding: '16px', background: selectedBlock === block ? 'var(--button-color)' : 'var(--secondary-bg)', color: selectedBlock === block ? 'var(--button-text-color)' : 'var(--text-color)' }}
                            onClick={() => setSelectedBlock(block)}
                        >
                            Block {block}
                        </button>
                    ))}
                </div>
            </div>

            {error && (
                <p style={{ color: '#f44336', marginTop: '16px' }}>{error}</p>
            )}

            <button
                className="btn-primary"
                style={{ width: '100%', marginTop: '32px', padding: '16px' }}
                disabled={!selectedBlock || loading}
                onClick={handleRegister}
            >
                {loading ? 'Setting up...' : 'Continue'}
            </button>
        </div>
    )
}
