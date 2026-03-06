<template>
  <div class="card">
    <h3>订单管理</h3>
    <div class="toolbar">
      <select v-model="status">
        <option value="">全部状态</option>
        <option value="pending">待发货</option>
        <option value="shipped">已发货</option>
        <option value="completed">已完成</option>
        <option value="canceled">已取消</option>
      </select>
      <button class="btn" @click="load">筛选</button>
    </div>

    <section class="panel">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户</th>
            <th>商品</th>
            <th>数量</th>
            <th>积分</th>
            <th>状态</th>
            <th>备注/物流</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td>{{ order.id }}</td>
            <td>{{ order.user_id }}</td>
            <td>{{ order.product_id }}</td>
            <td>{{ order.quantity }}</td>
            <td>{{ order.points_cost }}</td>
            <td><span :class="['badge', order.status]">{{ statusText(order.status) }}</span></td>
            <td>{{ order.shipping_remark || '—' }}</td>
            <td>
              <button class="btn sm" :disabled="order.status!=='pending'" @click="openShip(order)">发货</button>
            </td>
          </tr>
          <tr v-if="!orders.length"><td colspan="8" class="empty">暂无订单</td></tr>
        </tbody>
      </table>
    </section>

    <div v-if="dialog.visible" class="dialog-mask">
      <div class="dialog">
        <h4>发货</h4>
        <label>备注/物流信息</label>
        <input v-model.trim="dialog.remark" placeholder="例如：顺丰单号 123456" />
        <div class="ops">
          <button class="btn primary" @click="ship">确认发货</button>
          <button class="btn ghost" @click="dialog.visible=false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { adminListOrders, adminShipOrder, type OrderItem, type PaginationMeta } from "@/api/admin_shop";

const orders = ref<OrderItem[]>([]);
const status = ref("");
const page = ref(1);
const pageSize = ref(10);
const meta = ref<PaginationMeta>({ page: 1, page_size: 10, total: 0 });

async function load() {
  const res = await adminListOrders({ page: page.value, pageSize: pageSize.value, status: status.value || undefined });
  orders.value = res.data;
  meta.value = res.meta;
}

function statusText(val: string) {
  const map: Record<string, string> = { pending: "待发货", shipped: "已发货", completed: "已完成", canceled: "已取消" };
  return map[val] || val;
}

const dialog = reactive<{ visible: boolean; id?: number; remark: string }>({ visible: false, remark: "" });

function openShip(order: OrderItem) {
  dialog.visible = true;
  dialog.id = order.id;
  dialog.remark = order.shipping_remark || "";
}

async function ship() {
  if (!dialog.id) return;
  await adminShipOrder(dialog.id, dialog.remark || undefined);
  dialog.visible = false;
  await load();
}

onMounted(load);
</script>

<style scoped>
.card { display:flex; flex-direction:column; gap:12px; }
.toolbar { display:flex; gap:8px; align-items:center; }
.panel { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.table { width:100%; border-collapse:collapse; }
.table th, .table td { border-bottom:1px solid #e2e8f0; padding:10px 8px; text-align:left; }
.badge { padding:4px 10px; border-radius:8px; background:#e2e8f0; font-size:12px; }
.badge.pending { background:#fef3c7; color:#b45309; }
.badge.shipped { background:#cffafe; color:#0e7490; }
.badge.completed { background:#dcfce7; color:#15803d; }
.empty { text-align:center; color:#94a3b8; }
.btn { padding:8px 12px; border:1px solid #e2e8f0; border-radius:8px; background:#fff; }
.btn.primary { background:#6366f1; color:#fff; border-color:#6366f1; }
.btn.ghost { background:#f8fafc; }
.btn.sm { padding:6px 10px; }
.dialog-mask { position:fixed; inset:0; background:rgba(15,23,42,.35); display:flex; justify-content:center; align-items:center; }
.dialog { background:#fff; padding:16px 18px; border-radius:12px; width:360px; display:flex; flex-direction:column; gap:10px; }
.ops { display:flex; gap:8px; justify-content:flex-end; }
</style>
