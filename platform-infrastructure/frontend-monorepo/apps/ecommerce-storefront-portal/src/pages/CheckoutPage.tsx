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
