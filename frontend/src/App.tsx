import { BrowserRouter, Route, Routes } from 'react-router'

import { Layout } from './components/Layout'
import { LoginPage } from './pages/LoginPage'
import { ModulesPage } from './pages/ModulesPage'
import { ShopPage } from './pages/ShopPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<ModulesPage />} />
          <Route path="shop" element={<ShopPage />} />
          <Route path="login" element={<LoginPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
