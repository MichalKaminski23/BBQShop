import { NavLink, Outlet } from 'react-router'

export function Layout() {
  return (
    <div className="layout">
      <header className="header">
        <span className="logo">🔥 BBQShop</span>
        <nav className="nav">
          <NavLink to="/" end>
            Moduły
          </NavLink>
          <NavLink to="/shop">Sklep</NavLink>
        </nav>
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="footer">
        Projekt edukacyjny TBO – aplikacja celowo zawiera podatności.
      </footer>
    </div>
  )
}
