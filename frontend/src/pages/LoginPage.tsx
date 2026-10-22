import { useMutation } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'

import { api, ApiError, type LoginResult } from '../api/client'

export function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const login = useMutation<LoginResult, Error, void>({
    mutationFn: () => api.login({ username, password }),
  })

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    login.mutate()
  }

  const moduleOff = login.error instanceof ApiError && login.error.status === 404

  return (
    <section className="card">
      <h2>Logowanie</h2>
      <p className="muted">
        Użytkownicy z kolekcji MongoDB <code>users</code>. Przykład: <code>admin</code> /{' '}
        <code>Admin123!</code>.
      </p>

      <form className="login-form" onSubmit={handleSubmit}>
        <label>
          Login
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="np. admin"
            aria-label="Login"
          />
        </label>
        <label>
          Hasło
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            aria-label="Hasło"
          />
        </label>
        <button type="submit" disabled={login.isPending}>
          {login.isPending ? 'Logowanie…' : 'Zaloguj'}
        </button>
      </form>

      {login.data && (
        <p className="ok">
          Zalogowano jako <strong>{login.data.username}</strong> (rola: {login.data.role}).
        </p>
      )}
      {moduleOff && <p className="muted">Moduł NoSQLi jest wyłączony (BBQ_MODULE_NOSQLI=off).</p>}
      {login.isError && !moduleOff && <p className="error">{login.error.message}</p>}
    </section>
  )
}
