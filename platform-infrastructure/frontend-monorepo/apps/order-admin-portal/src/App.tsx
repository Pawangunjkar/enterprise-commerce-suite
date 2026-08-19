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
