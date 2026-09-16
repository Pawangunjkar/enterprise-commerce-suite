import { useMemo, useState } from "react";

type FlowBox = { label: string; sub?: string; tone: "plat" | "mec" | "oms" | "bill" | "crm" };
type FlowStep = { title: string; text: string; boxes: FlowBox[] };

const FLOWS: Record<string, { title: string; steps: FlowStep[] }> = {
  overview: {
    title: "Platform layers",
    steps: [
      {
        title: "Experience → Gateway → Domains",
        text: "Storefront and admin consoles hit API Gateway :8080. JWT from Keycloak realm ecs.",
        boxes: [
          { label: "React portals", sub: ":5173–5178", tone: "plat" },
          { label: "API Gateway", sub: ":8080", tone: "plat" },
          { label: "MEC / OMS / Bill / CRM", tone: "mec" }
        ]
      },
      {
        title: "Data plane",
        text: "Postgres per domain, Redis carts/prices, Kafka events, Solr search index.",
        boxes: [
          { label: "PostgreSQL", tone: "plat" },
          { label: "Redis", tone: "plat" },
          { label: "Kafka", tone: "plat" },
          { label: "Solr", tone: "mec" }
        ]
      }
    ]
  },
  checkout: {
    title: "Checkout saga",
    steps: [
      {
        title: "Pre-checkout",
        text: "Pincode EDD → cart → dynamic price → IGST on HSN 8517.",
        boxes: [
          { label: "Pincode", tone: "oms" },
          { label: "Cart", tone: "oms" },
          { label: "GST", tone: "bill" }
        ]
      },
      {
        title: "Saga steps",
        text: "order-orchestrator: ATP lock → UPI authorize → WMS wave → capture + invoice. Compensate on failure.",
        boxes: [
          { label: "Order saga", tone: "oms" },
          { label: "ATP lock", tone: "oms" },
          { label: "BharatQR", tone: "bill" },
          { label: "WMS + Invoice", tone: "oms" }
        ]
      }
    ]
  },
  catalog: {
    title: "Catalog publish",
    steps: [
      {
        title: "SKU lifecycle",
        text: "Create → activate → IMEI ingest → offer event → Solr index → OMS consumer.",
        boxes: [
          { label: "product-service", tone: "mec" },
          { label: "IMEI", tone: "mec" },
          { label: "Kafka offer", tone: "plat" },
          { label: "Solr", tone: "mec" }
        ]
      }
    ]
  },
  crm: {
    title: "CRM 360",
    steps: [
      {
        title: "Assisted desk",
        text: "OTP → profile → DPDP consent → loyalty → pay-link / ticket.",
        boxes: [
          { label: "Customer 360", tone: "crm" },
          { label: "DPDP", tone: "crm" },
          { label: "Loyalty", tone: "crm" },
          { label: "Pay-link", tone: "crm" }
        ]
      }
    ]
  }
};

const toneBorder: Record<FlowBox["tone"], string> = {
  plat: "border-l-sky-500",
  mec: "border-l-violet-500",
  oms: "border-l-emerald-500",
  bill: "border-l-amber-500",
  crm: "border-l-pink-500"
};

export function ArchitectureDrawer() {
  const [open, setOpen] = useState(false);
  const [flowKey, setFlowKey] = useState("overview");
  const [stepIndex, setStepIndex] = useState(0);

  const flow = FLOWS[flowKey];
  const step = flow.steps[stepIndex];

  const flowKeys = useMemo(() => Object.keys(FLOWS), []);

  function selectFlow(key: string) {
    setFlowKey(key);
    setStepIndex(0);
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:border-slate-900"
      >
        Architecture blueprint
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/40" onClick={() => setOpen(false)}>
          <aside
            className="flex h-full w-full max-w-xl flex-col bg-white shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <header className="flex items-center justify-between border-b px-5 py-4">
              <div>
                <h2 className="text-lg font-bold">Architecture blueprint</h2>
                <p className="text-sm text-slate-500">{flow.title}</p>
              </div>
              <button type="button" className="text-slate-500 hover:text-slate-900" onClick={() => setOpen(false)}>
                Close
              </button>
            </header>

            <div className="flex flex-wrap gap-2 border-b px-5 py-3">
              {flowKeys.map((key) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => selectFlow(key)}
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    key === flowKey ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-700"
                  }`}
                >
                  {FLOWS[key].title}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-y-auto px-5 py-4">
              <p className="mb-3 text-xs uppercase tracking-wide text-slate-500">
                Step {stepIndex + 1} of {flow.steps.length}
              </p>
              <div className="flex flex-wrap items-center justify-center gap-2 rounded-2xl border bg-slate-50 p-4">
                {step.boxes.map((box, index) => (
                  <div key={box.label} className="flex items-center gap-2">
                    <div className={`min-w-[120px] rounded-xl border border-l-4 bg-white px-3 py-2 text-center ${toneBorder[box.tone]}`}>
                      <p className="text-sm font-semibold">{box.label}</p>
                      {box.sub && <p className="text-xs text-slate-500">{box.sub}</p>}
                    </div>
                    {index < step.boxes.length - 1 && <span className="text-slate-400">→</span>}
                  </div>
                ))}
              </div>
              <h3 className="mt-4 font-semibold">{step.title}</h3>
              <p className="mt-1 text-sm text-slate-600">{step.text}</p>
              <a
                href="/architecture-walkthrough.html"
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-block text-sm font-medium text-sky-700 hover:underline"
              >
                Open full interactive walkthrough →
              </a>
            </div>

            <footer className="flex gap-2 border-t px-5 py-4">
              <button
                type="button"
                disabled={stepIndex === 0}
                onClick={() => setStepIndex((i) => Math.max(0, i - 1))}
                className="rounded-lg border px-4 py-2 text-sm disabled:opacity-40"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={stepIndex >= flow.steps.length - 1}
                onClick={() => setStepIndex((i) => Math.min(flow.steps.length - 1, i + 1))}
                className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
              >
                Next
              </button>
            </footer>
          </aside>
        </div>
      )}
    </>
  );
}
