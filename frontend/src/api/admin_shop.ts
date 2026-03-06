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

export async function adminListProducts(params: { page?: number; pageSize?: number; status?: string; keyword?: string } = {}) {
  const { page = 1, pageSize = 10, status, keyword } = params;
  const { data } = await httpClient.get<{ data: ProductItem[]; meta: PaginationMeta }>("/shop/admin/products", {
    params: { page, page_size: pageSize, status, keyword }
  });
  return data;
}

export async function adminCreateProduct(payload: { title: string; cover?: string | null; price?: number | null; points_price: number; stock: number; status?: string }) {
  const { data } = await httpClient.post<{ data: ProductItem }>("/shop/admin/products", payload);
  return data.data;
}

export async function adminUpdateProduct(id: number, payload: Partial<{ title: string; cover?: string | null; price?: number | null; points_price: number; stock: number; status: string }>) {
  const { data } = await httpClient.patch<{ data: ProductItem }>(`/shop/admin/products/${id}`, payload);
  return data.data;
}

export async function adminListOrders(params: { page?: number; pageSize?: number; status?: string } = {}) {
  const { page = 1, pageSize = 10, status } = params;
  const { data } = await httpClient.get<{ data: OrderItem[]; meta: PaginationMeta }>("/shop/admin/orders", {
    params: { page, page_size: pageSize, status }
  });
  return data;
}

export async function adminShipOrder(id: number, remark?: string) {
  const { data } = await httpClient.post<{ data: OrderItem }>(`/shop/admin/orders/${id}/ship`, { remark });
  return data.data;
}
