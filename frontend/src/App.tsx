import { BrowserRouter, Route, Routes } from 'react-router'

import { Layout } from './components/Layout'
import { ModulesPage } from './pages/ModulesPage'
import { ShopPage } from './pages/ShopPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<ModulesPage />} />
          <Route path="shop" element={<ShopPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
