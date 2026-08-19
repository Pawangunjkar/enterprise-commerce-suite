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
