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
