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
