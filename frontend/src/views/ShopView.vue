<template>
  <div class="card">
    <h3>积分商城</h3>
    <p class="sub">我的积分：<b>{{ points }}</b></p>

    <section class="panel">
      <div class="grid">
        <div class="product" v-for="p in items" :key="p.id">
          <div class="cover"/>
          <div class="title">{{ p.title }}</div>
          <div class="meta">价格：{{ p.price ?? '—' }} / 积分价：{{ p.points_price }} / 库存：{{ p.stock }}</div>
          <button :disabled="p.stock<=0 || points < p.points_price" @click="redeem(p)">
            兑换（{{ p.points_price }}分）
          </button>
        </div>
        <div v-if="!items.length" class="empty">暂无商品</div>
      </div>
      <div class="pager">
        <button :disabled="page<=1" @click="page--; load()">上一页</button>
        <span>第 {{ page }} / {{ totalPages }} 页（共 {{ meta.total }} 件）</span>
        <button :disabled="page>=totalPages" @click="page++; load()">下一页</button>
      </div>
    </section>

    <section class="panel">
      <div class="order-head">
        <h4>我的订单</h4>
        <button class="ghost" @click="loadOrders">刷新</button>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>商品</th>
            <th>数量</th>
            <th>积分消耗</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td>{{ order.id }}</td>
            <td>{{ order.product_id }}</td>
            <td>{{ order.quantity }}</td>
            <td>{{ order.points_cost }}</td>
            <td><span :class="['badge', order.status]">{{ statusText(order.status) }}</span></td>
            <td>
              <button v-if="order.status==='shipped' || order.status==='pending'" class="ghost" @click="confirm(order)">确认收货</button>
              <span v-else class="muted">-</span>
            </td>
          </tr>
          <tr v-if="!orders.length"><td colspan="6" class="empty">暂无订单</td></tr>
        </tbody>
      </table>
    </section>
  </div>
  
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { fetchProducts, fetchMyPoints, createOrder, fetchMyOrders, confirmOrder, type ProductItem, type PaginationMeta, type OrderItem } from '@/api/shop';

const items = ref<ProductItem[]>([]);
const meta = ref<PaginationMeta>({ page:1, page_size:12, total:0 });
const page = ref(1); const pageSize = ref(12);
const totalPages = computed(()=> Math.max(1, Math.ceil((meta.value.total||0)/pageSize.value)));
const points = ref(0);
const orders = ref<OrderItem[]>([]);

async function load(){
  const res = await fetchProducts({ page: page.value, pageSize: pageSize.value });
  items.value = res.data; meta.value = res.meta;
  points.value = await fetchMyPoints();
  await loadOrders();
}

async function redeem(p: ProductItem){
  await createOrder(p.id, 1);
  // 刷新库存与积分
  await load();
  alert('兑换成功');
}

async function loadOrders(){
  const res = await fetchMyOrders();
  orders.value = res.data;
}

function statusText(status: string){
  const map: Record<string,string> = { pending:'待发货', shipped:'已发货', completed:'已完成', canceled:'已取消' };
  return map[status] || status;
}

async function confirm(order: OrderItem){
  await confirmOrder(order.id);
  await loadOrders();
  alert('收货成功');
}

onMounted(load);
</script>

<style scoped>
.card { display:flex; flex-direction:column; gap:16px; }
.sub { color:#64748b; margin:0; }
.panel { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; }
.product { border:1px solid #e2e8f0; border-radius:12px; padding:12px; display:flex; flex-direction:column; gap:8px; }
.cover { height:100px; background:#f1f5f9; border-radius:8px; }
.title { font-weight:600; }
.meta { color:#94a3b8; font-size:12px; }
button { align-self:flex-start; padding:8px 12px; border-radius:8px; border:1px solid #e2e8f0; background:#fff; }
.empty { color:#94a3b8; text-align:center; }
.pager { display:flex; gap:12px; align-items:center; justify-content:center; padding-top:12px; }
.table { width:100%; border-collapse:collapse; margin-top:12px; }
.table th, .table td { border-bottom:1px solid #e2e8f0; padding:8px 6px; text-align:left; }
.order-head { display:flex; justify-content:space-between; align-items:center; }
.ghost { border:1px solid #e2e8f0; background:#f8fafc; padding:8px 12px; border-radius:8px; }
.badge { padding:4px 8px; border-radius:8px; font-size:12px; background:#e2e8f0; }
.badge.pending { background:#fef3c7; color:#92400e; }
.badge.shipped { background:#cffafe; color:#0e7490; }
.badge.completed { background:#dcfce7; color:#15803d; }
.muted { color:#94a3b8; }
</style>
