import { useMemo, useState } from "react";

type FlowBox = { label: string; sub?: string; tone: "plat" | "mec" | "oms" | "bill" | "crm" };
type FlowStep = { title: string; text: string; does?: string[]; how?: string[]; boxes: FlowBox[] };

const FLOWS: Record<string, { title: string; intro: string; steps: FlowStep[] }> = {
  overview: {
    title: "Platform layers",
    intro: "Six React portals → API Gateway → 50+ Java services → Postgres/Redis/Kafka/Solr. Domains never import each other directly.",
    steps: [
      {
        title: "Experience → Gateway",
        text: "Buyers use storefront :5173; operators use admin consoles :5174–5178. All HTTP goes to gateway :8080 — never to service ports directly from browsers.",
        does: ["Storefront: search, EDD, BharatQR checkout", "Admin: catalog, OMS, billing, CRM desks"],
        how: ["axios + TanStack Query → /api/v1/*", "JWT from Keycloak realm ecs on protected routes"],
        boxes: [
          { label: "React portals", sub: ":5173–5178", tone: "plat" },
          { label: "API Gateway", sub: ":8080", tone: "plat" }
        ]
      },
      {
        title: "Domains + data plane",
        text: "MEC owns SKUs, OMS owns orders/saga, Billing owns GST/UPI/invoices, CRM owns identity/consent. Postgres is source of truth; Redis holds carts.",
        does: ["MEC 8101–8111 · OMS 8201–8210 · Billing 8301–8311 · CRM 8401–8408", "Kafka → Solr indexer + OMS catalog consumer"],
        how: ["Flyway schema per service", "CloudEvents on offer/catalog changes"],
        boxes: [
          { label: "MEC", tone: "mec" },
          { label: "OMS", tone: "oms" },
          { label: "Billing", tone: "bill" },
          { label: "CRM", tone: "crm" },
          { label: "Postgres + Kafka", tone: "plat" }
        ]
      }
    ]
  },
  checkout: {
    title: "Checkout saga",
    intro: "Delhi shopper, inter-state IGST, UPI BharatQR. order-orchestrator runs compensating saga: ATP → pay → WMS → invoice.",
    steps: [
      {
        title: "Pre-checkout enrichment",
        text: "Pincode serviceability sets EDD and tax lane (HR→DL = IGST). Cart in Redis, price engine applies discounts, GST computes on HSN 8517.",
        does: ["GET /pincodes/serviceability", "POST /carts/items, /prices/calculate, /gst/compute"],
        how: ["Storefront orchestrates reads before place_order", "taxable amount = price after loyalty"],
        boxes: [
          { label: "Pincode", tone: "oms" },
          { label: "Cart + Price", tone: "oms" },
          { label: "GST IGST", tone: "bill" }
        ]
      },
      {
        title: "Saga execution",
        text: "POST /orders/place persists commerce_order + checkout_saga, then SagaOrchestrator calls ATP lock, payment authorize, WMS wave, capture + invoice.",
        does: ["lock_stock at NDC-HR", "BharatQR + simulate-success in lab", "Compensate unlock/void/cancel on failure"],
        how: ["In-process saga loop with reverse compensation", "FAILED status + error on checkout_saga row"],
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
    intro: "SKU create → activate → IMEI → Kafka offer → Solr index → OMS consumer. Search lags activate by seconds (eventual consistency).",
    steps: [
      {
        title: "SKU lifecycle",
        text: "product-service stores draft with HSN; activate flips LIVE; IMEI service validates Luhn for handsets.",
        does: ["POST /products, PUT /products/{id}/activate", "POST /imei/ingest"],
        how: ["Catalog Studio → gateway → MEC Postgres", "Draft invisible in Solr until indexed"],
        boxes: [
          { label: "product-service", tone: "mec" },
          { label: "IMEI", tone: "mec" }
        ]
      },
      {
        title: "Async propagation",
        text: "Offers publish Kafka CloudEvents; search-solr-indexer updates facets; catalog-consumer hydrates OMS cart validation.",
        does: ["POST /offers → Kafka", "GET /search/products for storefront"],
        how: ["Indexer consumer → Solr soft commit", "cart-service validates sku against consumer cache"],
        boxes: [
          { label: "Kafka offer", tone: "plat" },
          { label: "Solr", tone: "mec" },
          { label: "OMS consumer", tone: "oms" }
        ]
      }
    ]
  },
  crm: {
    title: "CRM 360",
    intro: "Assisted desk: OTP identity → KYC dossier → DPDP consent → loyalty → WhatsApp pay-link or ticket.",
    steps: [
      {
        title: "Identity + KYC",
        text: "Mobile is customerId. OTP verify (lab 123456), then upsert/get profile with PAN/GSTIN/name.",
        does: ["POST /customers/otp/start|verify", "PUT + GET /customers/{mobile}"],
        how: ["CRM portal :5178 → customer-360-service :8401", "Agents call get_profile for enrichment"],
        boxes: [
          { label: "Customer 360", tone: "crm" },
          { label: "Profile store", tone: "crm" }
        ]
      },
      {
        title: "Consent + assisted actions",
        text: "Record DPDP purpose, check loyalty tier, mint pay-link or open support ticket; mark cart abandoned if needed.",
        does: ["record_consent, get_loyalty, create_paylink, create_ticket"],
        how: ["Enrichment before pay-link (crm-assisted-sales playbook)", "Scenario crm-assisted-sales-paylink in agents repo"],
        boxes: [
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

            <p className="border-b bg-slate-50 px-5 py-3 text-sm text-slate-600">{flow.intro}</p>

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
              {step.does && step.does.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold uppercase tracking-wide text-sky-700">What it does</p>
                  <ul className="mt-1 list-disc pl-5 text-sm text-slate-600">
                    {step.does.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
              {step.how && step.how.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold uppercase tracking-wide text-sky-700">How it flows</p>
                  <ul className="mt-1 list-disc pl-5 text-sm text-slate-600">
                    {step.how.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
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
