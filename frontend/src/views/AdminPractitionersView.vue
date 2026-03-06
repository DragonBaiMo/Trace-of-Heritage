<template>
  <div class="card">
    <h3>从业者管理</h3>
    <div class="toolbar">
      <select v-model="status">
        <option value="">全部</option>
        <option value="pending">待审</option>
        <option value="approved">已通过</option>
        <option value="rejected">已驳回</option>
      </select>
      <button @click="load()">刷新</button>
    </div>

    <section class="panel">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>申请人</th>
            <th>实名/头衔</th>
            <th>状态</th>
            <th>提交时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in items" :key="a.id">
            <td>{{ a.id }}</td>
            <td>#{{ a.applicant_id }}</td>
            <td>{{ a.realname }} / {{ a.title }}</td>
            <td>{{ a.status }}</td>
            <td>{{ a.created_at?.slice(0,19).replace('T',' ') }}</td>
            <td>
              <button @click="openReview(a)">审核</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!items.length" class="empty">暂无记录</div>
    </section>

    <div v-if="drawer" class="drawer">
      <div class="drawer-body">
        <h4>审核申请 #{{ current?.id }}</h4>
        <p class="hint">请核对实名、头衔与附件等资料，确认无误后给出审核结论；若驳回请详细填写审核意见。</p>
        <div class="field"><label>实名</label><div>{{ current?.realname }}</div></div>
        <div class="field"><label>头衔</label><div>{{ current?.title }}</div></div>
        <div class="field"><label>简介</label><div>{{ current?.bio || '—' }}</div></div>
        <div class="field"><label>附件</label><div>
          <template v-if="current?.attachment">
            <a :href="current.attachment" target="_blank">{{ current.attachment }}</a>
          </template>
          <template v-else>—</template>
        </div></div>
        <div class="field"><label>审核意见</label><textarea v-model="note" placeholder="驳回时需≥5字"></textarea></div>
        <div class="ops">
          <button :disabled="loading" @click="doReview('approve')">通过</button>
          <button :disabled="loading" class="danger" @click="doReview('reject')">驳回</button>
          <button class="ghost" @click="drawer=false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { fetchApplications, reviewApplication, type PractitionerApplicationItem } from '@/api/practitioner_admin';

const items = ref<PractitionerApplicationItem[]>([]);
const status = ref('pending');

const drawer = ref(false);
const current = ref<PractitionerApplicationItem | null>(null);
const note = ref('');
const loading = ref(false);

async function load(){
  try {
    items.value = await fetchApplications(status.value || undefined);
  } catch (e: any) {
    alert(e?.message || String(e) || '获取申请列表失败');
  }
}

function openReview(a: PractitionerApplicationItem){
  current.value = a; note.value=''; drawer.value=true;
}

async function doReview(decision: 'approve'|'reject'){
  if(!current.value) return;
  if(decision==='reject' && (!note.value || note.value.trim().length<5)){
    alert('驳回需填写不少于5个字符的审核意见');
    return;
  }
  try{
    loading.value = true;
    await reviewApplication(current.value.id, { decision, review_note: note.value || undefined });
    alert('操作成功');
    drawer.value=false;
    await load();
  }catch(e:any){
    alert(e?.message || String(e) || '审核失败');
  }finally{
    loading.value = false;
  }
}

onMounted(load);
watch(status, () => {
  load();
});
</script>

<style scoped>
.card { display:flex; flex-direction:column; gap:16px; }
.toolbar { display:flex; gap:8px; align-items:center; }
.panel { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.table { width:100%; border-collapse: collapse; }
.table th, .table td { border-bottom:1px solid #e2e8f0; padding:10px 8px; text-align:left; }
.empty { text-align:center; color:#94a3b8; padding:8px 0; }
.drawer { position:fixed; inset:0; background:rgba(15,23,42,.45); display:flex; justify-content:flex-end; }
.drawer-body { width:520px; height:100%; background:#fff; padding:16px 20px; overflow:auto; }
.field { display:flex; gap:12px; align-items:flex-start; margin:10px 0; }
.field label { width:88px; color:#64748b; }
.field textarea { width:100%; min-height:88px; padding:8px; border:1px solid #e2e8f0; border-radius:8px; }
.ops { display:flex; gap:8px; }
.ops .danger { color:#ef4444; border-color:#fecaca; }
.ops .ghost { background:transparent; }
</style>
