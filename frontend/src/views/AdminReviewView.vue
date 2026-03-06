<template>
  <div class="review-center">
    <header class="header">
      <h3>审核中心</h3>
      <p>处理资源、活动与帖子等待审核的内容。</p>
    </header>

    <div class="tabs">
      <button :class="{active: tab==='resources'}" @click="switchTab('resources')">资源待审</button>
      <button :class="{active: tab==='activities'}" @click="switchTab('activities')">活动待审</button>
      <button :class="{active: tab==='posts'}" @click="switchTab('posts')">帖子待审</button>
      <button :class="{active: tab==='practitioners'}" @click="switchTab('practitioners')">热门话题审核</button>
    </div>

    <section v-if="tab==='resources'" class="panel">
      <ul>
        <li v-for="item in pendingResources" :key="`r-${item.id}`">
          <div>
            <h4>{{ item.title }}</h4>
            <p class="meta">类型：{{ item.resource_type }} · 提交人：#{{ item.submitter_id }}</p>
          </div>
          <div class="actions">
            <input v-model="resourceNotes[item.id]" type="text" class="note" placeholder="审核意见（可选）" />
            <button @click="handleResource(item.id, 'approve')">通过</button>
            <button class="reject" @click="handleResource(item.id, 'reject')">驳回</button>
          </div>
        </li>
        <li v-if="!pendingResources.length" class="empty">暂无待审资源</li>
      </ul>
    </section>

    <section v-else-if="tab==='activities'" class="panel">
      <ul>
        <li v-for="item in pendingActivities" :key="`a-${item.id}`">
          <div>
            <h4>{{ item.title }}</h4>
            <p class="meta">{{ fmt(item.start_time) }} - {{ fmt(item.end_time) }} · {{ item.location }}</p>
          </div>
          <div class="actions">
            <input v-model="activityNotes[item.id]" type="text" class="note" placeholder="审核意见（可选）" />
            <button @click="handleActivity(item.id, 'approve')">通过</button>
            <button class="reject" @click="handleActivity(item.id, 'reject')">驳回</button>
          </div>
        </li>
        <li v-if="!pendingActivities.length" class="empty">暂无待审活动</li>
      </ul>
    </section>

    <section v-else-if="tab==='posts'" class="panel">
      <ul>
        <li v-for="item in pendingPosts" :key="`p-${item.id}`">
          <div>
            <h4>{{ item.title }}</h4>
            <p class="meta">话题：{{ item.topic || '未分类' }} · 作者：#{{ item.author_id }}</p>
          </div>
          <div class="actions">
            <input v-model="postNotes[item.id]" type="text" class="note" placeholder="审核意见（可选）" />
            <button @click="handlePost(item.id, 'approve')">通过</button>
            <button class="reject" @click="handlePost(item.id, 'reject')">驳回</button>
          </div>
        </li>
        <li v-if="!pendingPosts.length" class="empty">暂无待审帖子</li>
      </ul>
    </section>
    <section v-else class="panel">
      <ul>
        <li v-for="item in pendingPosts" :key="`hp-${item.id}`">
          <div>
            <h4>{{ item.title }}</h4>
            <p class="meta">话题：{{ item.topic || '未分类' }} · 作者：#{{ item.author_id }}</p>
          </div>
          <div class="actions">
            <input v-model="hotTopicNotes[item.id]" type="text" class="note" placeholder="审核意见（可选）" />
            <button @click="handleHotTopic(item.id, 'approve')">通过</button>
            <button class="reject" @click="handleHotTopic(item.id, 'reject')">驳回</button>
          </div>
        </li>
        <li v-if="!pendingPosts.length" class="empty">暂无热门话题审核任务</li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { listPendingResources, reviewResource, listPendingActivities, reviewActivity, listPendingPosts, reviewPost } from "@/api/admin";

type NoteStore = { [key: number]: string };

const tab = ref<'resources'|'activities'|'posts'|'practitioners'>('resources');
const resourceNotes = reactive<NoteStore>({});
const activityNotes = reactive<NoteStore>({});
const postNotes = reactive<NoteStore>({});
const hotTopicNotes = reactive<NoteStore>({});

const pendingResources = ref<any[]>([]);
const pendingActivities = ref<any[]>([]);
const pendingPosts = ref<any[]>([]);

function fmt(v: string) {
  const d = new Date(v);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function switchTab(t: 'resources'|'activities'|'posts'|'practitioners') {
  tab.value = t;
}

async function loadAll() {
  [pendingResources.value, pendingActivities.value, pendingPosts.value] = await Promise.all([
    listPendingResources(),
    listPendingActivities(),
    listPendingPosts()
  ]);
  pruneNotes(pendingResources.value, resourceNotes);
  pruneNotes(pendingActivities.value, activityNotes);
  pruneNotes(pendingPosts.value, postNotes);
  pruneNotes(pendingPosts.value, hotTopicNotes);
}

async function handleResource(id: number, decision: 'approve'|'reject') {
  await reviewResource(id, { decision, review_note: resourceNotes[id] || undefined });
  delete resourceNotes[id];
  await loadAll();
}

async function handleActivity(id: number, decision: 'approve'|'reject') {
  await reviewActivity(id, { decision, review_note: activityNotes[id] || undefined });
  delete activityNotes[id];
  await loadAll();
}

async function handlePost(id: number, decision: 'approve'|'reject') {
  await reviewPost(id, { decision, review_note: postNotes[id] || undefined });
  delete postNotes[id];
  await loadAll();
}

async function handleHotTopic(id: number, decision: 'approve'|'reject') {
  await reviewPost(id, { decision, review_note: hotTopicNotes[id] || undefined });
  delete hotTopicNotes[id];
  await loadAll();
}

function pruneNotes(list: Array<{ id: number }>, store: NoteStore) {
  const keep = new Set(list.map(item => item.id));
  Object.keys(store).forEach(key => {
    const id = Number(key);
    if (!keep.has(id)) delete store[id];
  });
}

onMounted(loadAll);
</script>

<style scoped>
.review-center { display: flex; flex-direction: column; gap: 16px; }
.header { background: #fff; border-radius: 12px; padding: 16px 20px; box-shadow: 0 10px 30px rgba(15,23,42,.08); }
.tabs { display: inline-flex; gap: 8px; }
.tabs button { padding: 8px 14px; border-radius: 999px; border: 1px solid #e2e8f0; background: #fff; }
.tabs .active { background: #6366f1; color: #fff; border-color: transparent; }
.panel { background: #fff; border-radius: 12px; padding: 16px 20px; box-shadow: 0 10px 30px rgba(15,23,42,.08); }
.panel ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.panel li { display: flex; justify-content: space-between; align-items: center; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px; }
.meta { margin: 6px 0 0; font-size: 12px; color: #94a3b8; }
.actions { display: flex; gap: 8px; align-items: center; }
.actions .note { padding: 8px; border: 1px solid #d0d5dd; border-radius: 8px; min-width: 220px; }
.actions .reject { background: #fee2e2; border: 1px solid #fecaca; }
.empty { text-align: center; color: #94a3b8; padding: 16px 0; }
</style>
