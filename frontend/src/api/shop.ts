import { httpClient } from "./http";

export interface ProductItem {
  id: number;
  title: string;
  cover?: string | null;
  price?: number | null;
  points_price: number;
  stock: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PaginationMeta { page: number; page_size: number; total: number }
export interface OrderItem {
  id: number;
  user_id: number;
  product_id: number;
  quantity: number;
  points_cost: number;
  status: string;
  shipping_remark?: string | null;
  shipped_at?: string | null;
  confirmed_at?: string | null;
  created_at: string;
}

export async function fetchProducts(params: { page?: number; pageSize?: number } = {}) {
  const { page = 1, pageSize = 12 } = params;
  const { data } = await httpClient.get<{ data: ProductItem[]; meta: PaginationMeta }>("/shop/products", {
    params: { page, page_size: pageSize }
  });
  return data;
}

export async function fetchMyPoints() {
  const { data } = await httpClient.get<{ data: { balance: number } }>("/shop/points/me");
  return data.data.balance;
}

export async function createOrder(productId: number, quantity = 1) {
  const { data } = await httpClient.post<{ data: any }>("/shop/orders", { product_id: productId, quantity });
  return data.data;
}

export async function fetchMyOrders(params: { page?: number; pageSize?: number } = {}) {
  const { page = 1, pageSize = 10 } = params;
  const { data } = await httpClient.get<{ data: OrderItem[]; meta: PaginationMeta }>("/shop/orders", {
    params: { page, page_size: pageSize }
  });
  return data;
}

export async function confirmOrder(orderId: number) {
  const { data } = await httpClient.post<{ data: OrderItem }>(`/shop/orders/${orderId}/confirm`, {});
  return data.data;
}
