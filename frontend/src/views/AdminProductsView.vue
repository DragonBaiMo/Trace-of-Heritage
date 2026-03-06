<template>
  <div class="card">
    <h3>商品管理</h3>
    <div class="toolbar">
      <input v-model.trim="keyword" placeholder="搜索商品标题" @keyup.enter="load" />
      <select v-model="status">
        <option value="">全部状态</option>
        <option value="active">在售</option>
        <option value="inactive">下架</option>
      </select>
      <button class="btn" @click="load">查询</button>
      <button class="btn primary" @click="openCreate">新建商品</button>
    </div>

    <section class="panel">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>标题</th>
            <th>价格</th>
            <th>积分价</th>
            <th>库存</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in items" :key="p.id">
            <td>{{ p.id }}</td>
            <td>{{ p.title }}</td>
            <td>{{ p.price ?? '—' }}</td>
            <td>{{ p.points_price }}</td>
            <td>
              <input class="mini" type="number" min="0" v-model.number="p._stock" />
              <button class="btn sm" @click="saveStock(p)">保存</button>
            </td>
            <td>
              <span :class="p.status==='active' ? 'ok' : 'bad'">{{ p.status }}</span>
            </td>
            <td>
              <button class="btn sm" @click="openEdit(p)">编辑</button>
              <button class="btn sm" @click="toggleStatus(p)">{{ p.status==='active' ? '下架' : '上架' }}</button>
            </td>
          </tr>
          <tr v-if="!items.length"><td colspan="7" class="empty">暂无商品</td></tr>
        </tbody>
      </table>

      <div class="pager">
        <button :disabled="page<=1" @click="page--; load()">上一页</button>
        <span>第 {{ page }} / {{ totalPages }} 页（共 {{ meta.total }} 件）</span>
        <button :disabled="page>=totalPages" @click="page++; load()">下一页</button>
      </div>
    </section>

    <div v-if="dialog.visible" class="dialog-mask">
      <div class="dialog">
        <h4>{{ dialog.mode==='create' ? '新建商品' : '编辑商品' }}</h4>
        <div class="form">
          <label>标题</label>
          <input v-model.trim="dialog.form.title" />
          <label>封面</label>
          <input v-model.trim="dialog.form.cover" placeholder="图片URL（可选）" />
          <label>价格（元，可选）</label>
          <input v-model.number="dialog.form.price" type="number" step="0.01" min="0" />
          <label>积分价（分）</label>
          <input v-model.number="dialog.form.points_price" type="number" min="0" />
          <label>库存</label>
          <input v-model.number="dialog.form.stock" type="number" min="0" />
          <label>状态</label>
          <select v-model="dialog.form.status">
            <option value="active">在售</option>
            <option value="inactive">下架</option>
          </select>
        </div>
        <div class="ops">
          <button @click="submitDialog" class="btn primary">保存</button>
          <button @click="dialog.visible=false" class="btn ghost">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { adminListProducts, adminCreateProduct, adminUpdateProduct, type ProductItem, type PaginationMeta } from '@/api/admin_shop';

const items = ref<(ProductItem & { _stock?: number })[]>([]);
const meta = ref<PaginationMeta>({ page:1, page_size:10, total:0 });
const page = ref(1); const pageSize = ref(10);
const status = ref(''); const keyword = ref('');
const totalPages = computed(()=> Math.max(1, Math.ceil((meta.value.total||0)/pageSize.value)));

async function load(){
  const res = await adminListProducts({ page: page.value, pageSize: pageSize.value, status: status.value || undefined, keyword: keyword.value || undefined });
  items.value = res.data.map(p => ({ ...p, _stock: p.stock }));
  meta.value = res.meta;
}

function openCreate(){
  dialog.mode = 'create';
  dialog.form = { title:'', cover:'', price: undefined as any, points_price:0, stock:0, status:'active' } as any;
  dialog.visible = true;
}

function openEdit(p: ProductItem){
  dialog.mode = 'edit';
  dialog.id = p.id;
  dialog.form = { title:p.title, cover:p.cover||'', price:p.price||undefined, points_price:p.points_price, stock:p.stock, status:p.status } as any;
  dialog.visible = true;
}

async function submitDialog(){
  if(dialog.mode==='create'){
    await adminCreateProduct(dialog.form as any);
  } else if(dialog.mode==='edit' && dialog.id){
    await adminUpdateProduct(dialog.id, dialog.form as any);
  }
  dialog.visible=false; await load();
}

async function toggleStatus(p: ProductItem){
  const next = p.status === 'active' ? 'inactive' : 'active';
  await adminUpdateProduct(p.id, { status: next });
  await load();
}

async function saveStock(p: ProductItem & { _stock?: number }){
  if(p._stock == null) return;
  await adminUpdateProduct(p.id, { stock: p._stock });
  await load();
}

const dialog = reactive<{ visible: boolean; mode: 'create'|'edit'; id?: number; form: any }>({ visible:false, mode:'create', form:{} });

onMounted(load);
</script>

<style scoped>
.card { display:flex; flex-direction:column; gap:16px; }
.toolbar { display:flex; gap:8px; align-items:center; }
.primary { background:#6366f1; color:#fff; border:1px solid transparent; }
.panel { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.table { width:100%; border-collapse:collapse; }
.table th, .table td { border-bottom:1px solid #e2e8f0; padding:10px 8px; text-align:left; }
.table .empty { text-align:center; color:#94a3b8; }
.ok { color:#16a34a; }
.bad { color:#ef4444; }
.mini { padding:4px 8px; font-size:12px; }
.pager { display:flex; gap:12px; align-items:center; justify-content:center; padding-top:12px; }
.dialog-mask { position:fixed; inset:0; background:rgba(15,23,42,.45); display:flex; justify-content:center; align-items:center; }
.dialog { width:520px; background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.12); }
.dialog .form { display:grid; gap:8px; }
.ghost { background:transparent; }
input.mini { width:90px; }
</style>
