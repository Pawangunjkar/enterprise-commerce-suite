import { NavLink, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ProductPage from "./pages/ProductPage";
import CheckoutPage from "./pages/CheckoutPage";
import AccountPage from "./pages/AccountPage";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-20 border-b bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <span className="h-8 w-8 rounded-lg bg-saffron" />
            <strong>Enterprise Commerce</strong>
          </div>
          <nav className="flex gap-5 text-sm font-medium">
            <NavLink to="/">Store</NavLink>
            <NavLink to="/product/SKU-PHONE-8-128-BLACK">PDP</NavLink>
            <NavLink to="/checkout">Checkout</NavLink>
            <NavLink to="/account">My Orders</NavLink>
          </nav>
        </div>
      </header>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/product/:sku" element={<ProductPage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="/account" element={<AccountPage />} />
      </Routes>
    </div>
  );
}
