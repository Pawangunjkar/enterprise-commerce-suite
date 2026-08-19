#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FE = ROOT / "platform-infrastructure" / "frontend-monorepo"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


w(FE / "package.json", '''
{
  "name": "ecs-frontend-monorepo",
  "private": true,
  "version": "1.0.0",
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "lint": "turbo run lint"
  },
  "devDependencies": {
    "turbo": "^2.3.0",
    "typescript": "^5.6.3"
  },
  "packageManager": "npm@10.8.2"
}
''')
w(FE / "turbo.json", '''
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] },
    "dev": { "cache": false, "persistent": true },
    "lint": {}
  }
}
''')
w(FE / "tsconfig.base.json", '''
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "resolveJsonModule": true
  }
}
''')

w(FE / "packages/tailwind-config/package.json", '''
{ "name": "@ecs/tailwind-config", "version": "1.0.0", "private": true, "main": "tailwind.config.js" }
''')
w(FE / "packages/tailwind-config/tailwind.config.js", '''
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../../apps/**/*.{ts,tsx}", "../../packages/ui-components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        saffron: "#FF9933",
        indiaGreen: "#138808",
        navy: "#0B1F3A"
      }
    }
  },
  plugins: []
};
''')

w(FE / "packages/ui-components/package.json", '''
{
  "name": "@ecs/ui",
  "version": "1.0.0",
  "private": true,
  "main": "src/index.ts",
  "types": "src/index.ts",
  "peerDependencies": { "react": "^19.0.0", "react-dom": "^19.0.0" }
}
''')
w(FE / "packages/ui-components/src/index.ts", '''
export { Button } from "./Button";
export { Card } from "./Card";
export { Shell } from "./Shell";
''')
w(FE / "packages/ui-components/src/Button.tsx", '''
import { ButtonHTMLAttributes } from "react";

export function Button({ className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-xl bg-navy px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50 ${className}`}
      {...props}
    />
  );
}
''')
w(FE / "packages/ui-components/src/Card.tsx", '''
import { PropsWithChildren } from "react";
export function Card({ children }: PropsWithChildren) {
  return <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">{children}</div>;
}
''')
w(FE / "packages/ui-components/src/Shell.tsx", '''
import { PropsWithChildren } from "react";
export function Shell({ title, children }: PropsWithChildren<{ title: string }>) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <h1 className="text-xl font-bold tracking-tight">{title}</h1>
      </header>
      <main className="mx-auto max-w-7xl p-6">{children}</main>
    </div>
  );
}
''')

w(FE / "packages/data-access/package.json", '''
{
  "name": "@ecs/data-access",
  "version": "1.0.0",
  "private": true,
  "main": "src/index.ts"
}
''')
w(FE / "packages/data-access/src/index.ts", '''
import axios from "axios";

export const api = axios.create({
  baseURL: import.metaEnv?.VITE_API_BASE ?? "http://localhost:8080",
  timeout: 15000
});

export async function searchProducts(params: Record<string, string | number | undefined>) {
  const { data } = await api.get("/api/v1/search/products", { params });
  return data;
}

export async function checkPincode(pincode: string) {
  const { data } = await api.get(`/api/v1/pincodes/${pincode}/serviceability`);
  return data;
}

export async function createBharatQr(payload: { orderId: string; amount: number; vpa: string; merchantName: string; mcc: string }) {
  const { data } = await api.post("/api/v1/payments/upi/bharat-qr", payload);
  return data;
}

export async function calculatePrice(payload: { sku: string; basePrice: number; offerDiscount: number; loyaltyDiscount: number }) {
  const { data } = await api.post("/api/v1/prices/calculate", payload);
  return data;
}
''')

# Vite app helper
def vite_app(app_name, port, title):
    base = FE / "apps" / app_name
    w(base / "package.json", f'''
{{
  "name": "{app_name}",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite --port {port}",
    "build": "tsc -b && vite build",
    "preview": "vite preview --port {port}"
  }},
  "dependencies": {{
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.0.1",
    "@tanstack/react-query": "^5.62.0",
    "axios": "^1.7.9",
    "@ecs/ui": "1.0.0",
    "@ecs/data-access": "1.0.0"
  }},
  "devDependencies": {{
    "@types/react": "^19.0.1",
    "@types/react-dom": "^19.0.1",
    "@vitejs/plugin-react": "^4.3.4",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.16",
    "typescript": "^5.6.3",
    "vite": "^6.0.3"
  }}
}}
''')
    w(base / "vite.config.ts", '''
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({ plugins: [react()] });
''')
    w(base / "tsconfig.json", '''
{ "extends": "../../tsconfig.base.json", "include": ["src"], "compilerOptions": { "types": ["vite/client"] } }
''')
    w(base / "postcss.config.js", "export default { plugins: { tailwindcss: {}, autoprefixer: {} } };")
    w(base / "tailwind.config.js", '''
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}", "../../packages/ui-components/src/**/*.{ts,tsx}"],
  theme: { extend: { colors: { saffron: "#FF9933", indiaGreen: "#138808", navy: "#0B1F3A" } } },
  plugins: []
};
''')
    w(base / "index.html", f'''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''')
    w(base / "src/main.tsx", '''
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

const client = new QueryClient();
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={client}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
''')
    w(base / "src/index.css", "@tailwind base;\\n@tailwind components;\\n@tailwind utilities;")
    return base

store = vite_app("ecommerce-storefront-portal", 5173, "ECS Storefront")
w(store / "src/App.tsx", r'''
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
''')

w(store / "src/pages/HomePage.tsx", r'''
import { useQuery } from "@tanstack/react-query";
import { searchProducts } from "@ecs/data-access";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

const FALLBACK = {
  data: {
    numFound: 3,
    docs: [
      { id: "1", sku_s: "SKU-PHONE-8-128-BLACK", name_txt_en: "Nova X 5G (8GB / 128GB, Black)", list_price_f: 24999, brand_s: "Nova" },
      { id: "2", sku_s: "SKU-PHONE-12-256-GOLD", name_txt_en: "Nova X 5G (12GB / 256GB, Gold)", list_price_f: 32999, brand_s: "Nova" },
      { id: "3", sku_s: "SKU-BUDS-PRO", name_txt_en: "Nova Buds Pro", list_price_f: 4999, brand_s: "Nova" }
    ]
  }
};

export default function HomePage() {
  const [q, setQ] = useState("nova");
  const [ram, setRam] = useState<number | undefined>(undefined);
  const query = useQuery({
    queryKey: ["search", q, ram],
    queryFn: async () => {
      try {
        return await searchProducts({ q, ram });
      } catch {
        return FALLBACK;
      }
    }
  });
  const docs = query.data?.data?.docs ?? FALLBACK.data.docs;
  const ends = useMemo(() => Date.now() + 1000 * 60 * 60 * 36, []);
  const remaining = Math.max(0, ends - Date.now());
  const hours = Math.floor(remaining / 3_600_000);

  return (
    <div className="mx-auto max-w-7xl p-6">
      <section className="mb-6 rounded-3xl bg-gradient-to-r from-saffron to-amber-400 p-8 text-navy">
        <p className="text-sm font-semibold uppercase tracking-widest">Great Indian Festival</p>
        <h2 className="mt-2 text-4xl font-black">Diwali Sale is live</h2>
        <p className="mt-2">Offer window closes in ~{hours} hours. GST invoices on every order.</p>
      </section>
      <div className="mb-6 flex flex-wrap gap-3">
        <input className="w-80 rounded-xl border px-4 py-2" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search Hinglish: phone, 8gb, sasta" />
        {[8, 12].map((v) => (
          <button key={v} onClick={() => setRam(v)} className="rounded-full border px-4 py-2 text-sm">{v} GB RAM</button>
        ))}
      </div>
      <div className="grid gap-5 md:grid-cols-3">
        {docs.map((doc: any) => (
          <Link key={doc.id} to={`/product/${doc.sku_s}`} className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="mb-3 h-40 rounded-xl bg-slate-100" />
            <h3 className="font-semibold">{doc.name_txt_en}</h3>
            <p className="mt-2 text-lg font-bold">₹{Number(doc.list_price_f).toLocaleString("en-IN")}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
''')

w(store / "src/pages/ProductPage.tsx", r'''
import { useState } from "react";
import { checkPincode } from "@ecs/data-access";
import { Button } from "@ecs/ui";

export default function ProductPage() {
  const [ram, setRam] = useState("8");
  const [storage, setStorage] = useState("128");
  const [color, setColor] = useState("Black");
  const [pin, setPin] = useState("110001");
  const [edd, setEdd] = useState<string>("");
  const price = ram === "12" ? 32999 : 24999;

  async function lookup() {
    try {
      const res = await checkPincode(pin);
      setEdd(res.data.edd + (res.data.oda ? " (ODA +2 days)" : ""));
    } catch {
      setEdd("2026-08-23");
    }
  }

  return (
    <div className="mx-auto grid max-w-7xl gap-8 p-6 md:grid-cols-2">
      <div className="h-[420px] rounded-3xl bg-slate-200" />
      <div>
        <h1 className="text-3xl font-black">Nova X 5G</h1>
        <p className="mt-2 text-slate-600">HSN 8517 · GST 18%</p>
        <p className="mt-4 text-3xl font-bold">₹{price.toLocaleString("en-IN")}</p>
        <div className="mt-6 space-y-3">
          <Row label="RAM" values={["8", "12"]} value={ram} onChange={setRam} />
          <Row label="Storage" values={["128", "256"]} value={storage} onChange={setStorage} />
          <Row label="Color" values={["Black", "Gold"]} value={color} onChange={setColor} />
        </div>
        <div className="mt-6 flex gap-2">
          <input className="rounded-xl border px-3 py-2" value={pin} onChange={(e) => setPin(e.target.value)} />
          <Button onClick={lookup}>Check EDD</Button>
        </div>
        {edd && <p className="mt-2 text-sm text-indiaGreen">Estimated delivery {edd}</p>}
        <Button className="mt-6 w-full">Add to cart · {ram}/{storage} {color}</Button>
      </div>
    </div>
  );
}

function Row({ label, values, value, onChange }: { label: string; values: string[]; value: string; onChange: (v: string) => void }) {
  return (
    <div>
      <p className="mb-1 text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <div className="flex gap-2">
        {values.map((v) => (
          <button key={v} onClick={() => onChange(v)} className={`rounded-lg border px-3 py-1 ${v === value ? "border-navy bg-navy text-white" : ""}`}>{v}</button>
        ))}
      </div>
    </div>
  );
}
''')

w(store / "src/pages/CheckoutPage.tsx", r'''
import { useState } from "react";
import { createBharatQr } from "@ecs/data-access";
import { Button, Card } from "@ecs/ui";

export default function CheckoutPage() {
  const [step, setStep] = useState(1);
  const [qr, setQr] = useState<string>("");
  const [codOtp, setCodOtp] = useState("");

  async function payUpi() {
    try {
      const res = await createBharatQr({ orderId: "ECS-1001", amount: 24999, vpa: "ecs@upi", merchantName: "ECS Store", mcc: "5732" });
      setQr(res.data.qr.pngBase64);
    } catch {
      setQr("demo");
    }
    setStep(3);
  }

  return (
    <div className="mx-auto max-w-3xl space-y-4 p-6">
      <h1 className="text-2xl font-bold">Checkout</h1>
      <Card>
        <h2 className="font-semibold">1. Address & GSTIN</h2>
        {step >= 1 && (
          <div className="mt-3 grid gap-3">
            <input className="rounded-xl border px-3 py-2" defaultValue="A-12, Connaught Place, New Delhi 110001" />
            <input className="rounded-xl border px-3 py-2" placeholder="GSTIN (optional B2B invoice)" />
            <Button onClick={() => setStep(2)}>Continue</Button>
          </div>
        )}
      </Card>
      <Card>
        <h2 className="font-semibold">2. Payment</h2>
        {step >= 2 && (
          <div className="mt-3 flex flex-wrap gap-3">
            <Button onClick={payUpi}>UPI BharatQR</Button>
            <Button onClick={() => setStep(4)}>COD + OTP</Button>
            <Button>Cards / NetBanking</Button>
          </div>
        )}
      </Card>
      {step === 3 && (
        <Card>
          <p className="mb-3 font-semibold">Scan Dynamic BharatQR</p>
          {qr && qr !== "demo" ? <img alt="UPI QR" src={`data:image/png;base64,${qr}`} className="h-48 w-48" /> : <div className="h-48 w-48 bg-slate-200" />}
          <p className="mt-2 text-sm text-slate-500">Waiting for UPI collect confirmation over websocket...</p>
        </Card>
      )}
      {step === 4 && (
        <Card>
          <p>Enter COD verification OTP sent to your mobile</p>
          <input className="mt-2 rounded-xl border px-3 py-2" value={codOtp} onChange={(e) => setCodOtp(e.target.value)} />
          <Button className="mt-3">Place COD order</Button>
        </Card>
      )}
    </div>
  );
}
''')

w(store / "src/pages/AccountPage.tsx", r'''
import { Card } from "@ecs/ui";
export default function AccountPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-4 p-6">
      <h1 className="text-2xl font-bold">Order radar</h1>
      <Card>
        <p className="font-semibold">ECS-1001 · Nova X 5G</p>
        <ol className="mt-3 space-y-2 text-sm">
          <li>Packed at Gurgaon FC</li>
          <li>In transit · Delhivery DLV123456</li>
          <li>Out for delivery · EDD today</li>
        </ol>
        <a className="mt-4 inline-block text-sm text-indiaGreen" href="http://localhost:8080/api/v1/invoices/INV-1/pdf">Download GST invoice PDF</a>
      </Card>
    </div>
  );
}
''')

admin = vite_app("master-admin-portal", 5174, "ECS Master Admin")
w(admin / "src/App.tsx", r'''
import { Card, Shell } from "@ecs/ui";

const consoles = [
  { name: "Catalog Studio", href: "http://localhost:5175", desc: "SKU tree, IMEI, time-travel offers" },
  { name: "OMS Fulfillment", href: "http://localhost:5176", desc: "Kanban, WMS waves, NDR radar" },
  { name: "Billing Hub", href: "http://localhost:5177", desc: "GST, TCS 194O, BYOK vault" },
  { name: "CRM 360", href: "http://localhost:5178", desc: "Customer 360, paylinks, tickets" }
];

export default function App() {
  return (
    <Shell title="Unified Master Super-Admin">
      <div className="grid gap-4 md:grid-cols-4">
        {[
          ["GMV", "₹18.4 Cr"],
          ["AOV", "₹4,812"],
          ["Orders", "38,204"],
          ["Open DLQ", "7"]
        ].map(([k, v]) => (
          <Card key={k}>
            <p className="text-xs uppercase text-slate-500">{k}</p>
            <p className="mt-2 text-2xl font-bold">{v}</p>
          </Card>
        ))}
      </div>
      <h2 className="mt-8 mb-3 text-lg font-semibold">Domain consoles</h2>
      <div className="grid gap-4 md:grid-cols-2">
        {consoles.map((c) => (
          <a key={c.name} href={c.href} className="rounded-2xl border bg-white p-5 hover:border-navy">
            <h3 className="font-semibold">{c.name}</h3>
            <p className="text-sm text-slate-600">{c.desc}</p>
          </a>
        ))}
      </div>
    </Shell>
  );
}
''')

def portal(name, port, title, body):
    app = vite_app(name, port, title)
    w(app / "src/App.tsx", body)

# Domain portals live both in monorepo apps (for turbo) — architecture also lists them under domains.
portal("catalog-admin-studio", 5175, "Catalog Studio", r'''
import { Shell, Card } from "@ecs/ui";
export default function App() {
  return (
    <Shell title="MEC Catalog Studio">
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <h2 className="font-semibold">Time-travel simulator</h2>
          <input type="datetime-local" className="mt-3 w-full rounded-xl border px-3 py-2" />
          <p className="mt-2 text-sm text-slate-500">Solr fq: effective_from_dt:[* TO asOf] AND effective_to_dt:[asOf TO *]</p>
        </Card>
        <Card>
          <h2 className="font-semibold">IMEI ingest</h2>
          <input className="mt-3 w-full rounded-xl border px-3 py-2" placeholder="15-digit IMEI 1" />
          <input className="mt-2 w-full rounded-xl border px-3 py-2" placeholder="IMEI 2 / Serial" />
        </Card>
      </div>
    </Shell>
  );
}
''')
portal("order-admin-portal", 5176, "OMS Console", r'''
import { Shell, Card } from "@ecs/ui";
const cols = ["NEW", "PICKING", "PACKED", "IN_TRANSIT", "NDR"];
export default function App() {
  return (
    <Shell title="OMS Fulfillment Console">
      <div className="grid grid-cols-5 gap-3">
        {cols.map((c) => (
          <Card key={c}>
            <h3 className="font-semibold">{c}</h3>
            <div className="mt-3 rounded-xl bg-slate-100 p-3 text-sm">ECS-1001</div>
          </Card>
        ))}
      </div>
    </Shell>
  );
}
''')
portal("billing-admin-portal", 5177, "Billing Hub", r'''
import { Shell, Card } from "@ecs/ui";
export default function App() {
  return (
    <Shell title="Billing & Finance Hub">
      <div className="grid gap-4 md:grid-cols-3">
        <Card><h2 className="font-semibold">GSTR-1 draft</h2><p className="mt-2 text-2xl">₹2.1 Cr taxable</p></Card>
        <Card><h2 className="font-semibold">TCS 194O</h2><p className="mt-2 text-2xl">₹18.4 L</p></Card>
        <Card><h2 className="font-semibold">BYOK vault</h2><p className="mt-2 text-sm">Razorpay · PhonePe · Cashfree keys encrypted</p></Card>
      </div>
    </Shell>
  );
}
''')
portal("crm-admin-portal", 5178, "CRM 360", r'''
import { Shell, Card } from "@ecs/ui";
export default function App() {
  return (
    <Shell title="CRM 360 Helpdesk">
      <Card>
        <h2 className="font-semibold">Customer 360</h2>
        <p className="mt-2">+91 98765 43210 · GOLD · LTV ₹1.2L · PAN masked · GSTIN on file</p>
      </Card>
    </Shell>
  );
}
''')

print("frontend generated")
