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
