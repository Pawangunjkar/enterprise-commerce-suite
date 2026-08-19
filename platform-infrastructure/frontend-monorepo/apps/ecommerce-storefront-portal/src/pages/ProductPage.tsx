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
