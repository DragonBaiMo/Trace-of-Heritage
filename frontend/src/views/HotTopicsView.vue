<template>
  <div class="card">
    <h3>热门话题</h3>
    <p class="sub">浏览、发布帖子并参与评论与点赞</p>

    <section class="panel form">
      <input v-model.trim="newTitle" placeholder="帖子标题" />
      <textarea v-model.trim="newContent" placeholder="内容（支持 Markdown）"></textarea>
      <input v-model.trim="newTopic" placeholder="话题（可选）" />
      <button @click="createPost">发布</button>
    </section>

    <section class="panel">
      <ul class="list">
        <li v-for="p in items" :key="p.id" class="row">
          <div class="main">
            <h4>{{ p.title }}</h4>
            <p class="meta">{{ p.created_at?.slice(0,19).replace('T',' ') }}</p>
            <p class="desc">{{ p.content_md?.slice(0,120) }}</p>
          </div>
          <div class="ops">
            <button @click="like(p.id)">点赞 {{ p.like_count }}</button>
            <button @click="favorite(p.id)">收藏 {{ p.favorite_count }}</button>
            <button @click="openComments(p.id)">评论</button>
          </div>
        </li>
        <li v-if="!items.length" class="empty">暂无帖子</li>
      </ul>
    </section>

    <div v-if="commentDrawer" class="drawer">
      <div class="drawer-body">
        <h4>评论</h4>
        <ul class="clist">
          <li v-for="c in comments" :key="c.id">
            <div class="c">{{ c.content }}</div>
            <div class="cmeta">#{{ c.author_id }} · {{ c.created_at?.slice(0,19).replace('T',' ') }}</div>
          </li>
          <li v-if="!comments.length" class="empty">暂无评论</li>
        </ul>
        <textarea v-model.trim="newComment" placeholder="写下你的评论"></textarea>
        <div class="ops"><button @click="sendComment">发表</button><button class="ghost" @click="commentDrawer=false">关闭</button></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { fetchHotPosts, type PostItem } from '@/api/topics_user';
import { createPost as createPostApi, createComment, fetchComments, sendReaction, type CommentItem } from '@/api/post';

const items = ref<PostItem[]>([]);
const newTitle = ref('');
const newContent = ref('');
const newTopic = ref('');

const commentDrawer = ref(false);
const currentPostId = ref<number | null>(null);
const comments = ref<CommentItem[]>([]);
const newComment = ref('');

async function load(){
  const res = await fetchHotPosts();
  items.value = res.data ?? [];
}

async function createPost(){
  if(!newTitle.value || !newContent.value){
    alert('标题与内容必填'); return;
  }
  if(newContent.value.length < 10){
    alert('正文内容至少需要 10 个字符');
    return;
  }
  await createPostApi({
    title: newTitle.value,
    content_md: newContent.value,
    topic: newTopic.value || undefined,
    submit_for_review: true
  });
  newTitle.value=''; newContent.value=''; newTopic.value='';
  await load();
}

async function like(id:number){
  await sendReaction({ target_type:'post', target_id:id, reaction_type:'like' });
  await load();
}

async function favorite(id:number){
  await sendReaction({ target_type:'post', target_id:id, reaction_type:'favorite' });
  await load();
}

async function openComments(id:number){
  currentPostId.value = id; commentDrawer.value = true; newComment.value='';
  const list = await fetchComments(id);
  comments.value = list;
}

async function sendComment(){
  if(!currentPostId.value) return;
  if(!newComment.value){ alert('请输入评论内容'); return; }
  await createComment(currentPostId.value, { content: newComment.value });
  newComment.value='';
  comments.value = await fetchComments(currentPostId.value);
}

onMounted(load);
</script>

<style scoped>
.card { display:flex; flex-direction:column; gap:16px; }
.sub { color:#64748b; margin:0; }
.panel { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.form { display:grid; gap:8px; }
.form textarea { min-height:80px; }
.list { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:12px; }
.row { display:flex; justify-content:space-between; align-items:flex-start; border:1px solid #e2e8f0; border-radius:12px; padding:12px; }
.meta { color:#94a3b8; font-size:12px; margin:6px 0 0; }
.desc { color:#475467; margin:6px 0 0; }
.ops button { padding:6px 10px; border-radius:8px; border:1px solid #e2e8f0; background:#fff; }
.empty { text-align:center; color:#94a3b8; padding:8px 0; }

.drawer { position:fixed; inset:0; background:rgba(15,23,42,.45); display:flex; justify-content:flex-end; }
.drawer-body { width:520px; height:100%; background:#fff; padding:16px 20px; overflow:auto; display:flex; flex-direction:column; gap:8px; }
.clist { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:8px; }
.cmeta { color:#94a3b8; font-size:12px; }
.ops { display:flex; gap:8px; }
.ops .ghost { background:transparent; }
</style>
