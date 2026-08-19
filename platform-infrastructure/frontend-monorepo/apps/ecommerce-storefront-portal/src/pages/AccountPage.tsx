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
