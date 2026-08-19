import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8080",
  timeout: 15000
});

export async function searchProducts(params: Record<string, string | number | undefined>) {
  const { data } = await api.get("/api/v1/search/products", { params });
  return data;
}

export async function checkPincode(pincode: string) {
  const { data } = await api.get(`/api/v1/pincodes/${pincode}/serviceability`);
  return data;
}

export async function createBharatQr(payload: {
  orderId: string;
  amount: number;
  vpa: string;
  merchantName: string;
  mcc: string;
}) {
  const { data } = await api.post("/api/v1/payments/upi/bharat-qr", payload);
  return data;
}

export async function calculatePrice(payload: {
  sku: string;
  basePrice: number;
  offerDiscount: number;
  loyaltyDiscount: number;
}) {
  const { data } = await api.post("/api/v1/prices/calculate", payload);
  return data;
}
