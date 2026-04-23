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
            queryClient.invalidateQueries({ queryKey: ['profile'] })
        } catch (err: unknown) {
            const message = err instanceof Error ? err.message : 'Failed to register'
            setError(message)
            setLoading(false)
        }
    }

    return (
        <div className="register-page">
            <h1>SH LAUNDRY</h1>
            <p className="subtitle">SELECT YOUR BLOCK</p>

            <div className="block-select">
                {BLOCKS.map(block => (
                    <button
                        key={block}
                        className={`block-btn ${selectedBlock === block ? 'selected' : ''}`}
                        onClick={() => setSelectedBlock(block)}
                    >
                        {block}
                    </button>
                ))}
            </div>

            {error && (
                <p style={{ color: 'var(--in-use)', marginBottom: '16px', fontFamily: 'var(--font-terminal)' }}>
                    {error}
                </p>
            )}

            <button
                className="btn-primary"
                disabled={!selectedBlock || loading}
                onClick={handleRegister}
            >
                {loading ? 'LOADING...' : 'START'}
            </button>
        </div>
    )
}
