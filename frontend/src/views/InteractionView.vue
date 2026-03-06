<template>
  <div class="interaction">
    <section class="post-form">
      <h3>发布新帖</h3>
      <form @submit.prevent="handleSubmit">
        <label>
          标题
          <input v-model="postForm.title" type="text" required maxlength="80" placeholder="请输入标题" />
        </label>
        <label>
          话题标签
          <input v-model="postForm.topic" type="text" placeholder="例如：曲牌赏析" />
        </label>
        <label>
          正文内容（支持 Markdown）
          <textarea v-model="postForm.content_md" rows="5" required minlength="20" placeholder="请填写内容"></textarea>
        </label>
        <label class="checkbox">
          <input v-model="postForm.submit_for_review" type="checkbox" />
          <span>提交后进入审核（取消则保存草稿）</span>
        </label>
        <button type="submit" :disabled="loading">{{ loading ? "提交中" : "发布帖子" }}</button>
        <p v-if="formMessage" class="message">{{ formMessage }}</p>
        <p v-if="formError" class="error">{{ formError }}</p>
      </form>
    </section>

    <section class="post-list">
      <header>
        <h3>互动话题</h3>
        <div class="filters">
          <select v-model="status" @change="loadPosts">
            <option value="approved">已发布</option>
            <option value="pending">待审核</option>
            <option value="draft">草稿</option>
          </select>
        </div>
      </header>
      <ul>
        <li v-for="post in posts" :key="post.id" @click="selectPost(post)" :class="{ active: post.id === activePost?.id }">
          <div>
            <h4>{{ post.title }}</h4>
            <p class="meta">{{ post.topic || "未分类" }} · {{ formatTime(post.updated_at) }}</p>
          </div>
          <div class="actions">
            <button type="button" @click.stop="sendLike(post.id)">👍 {{ post.like_count }}</button>
            <button type="button" @click.stop="sendFavorite(post.id)">⭐ {{ post.favorite_count }}</button>
          </div>
        </li>
        <li v-if="!posts.length" class="empty">暂无帖子</li>
      </ul>
    </section>

    <section class="comments" v-if="activePost">
      <header>
        <h3>评论 · {{ activePost.title }}</h3>
        <p class="meta">状态：{{ statusMap[activePost.status] ?? activePost.status }}</p>
      </header>
      <div class="comment-list">
        <article v-for="comment in comments" :key="comment.id">
          <p class="content">{{ comment.content }}</p>
          <p class="time">{{ formatTime(comment.created_at) }}</p>
        </article>
        <p v-if="!comments.length" class="empty">暂无评论</p>
      </div>
      <form class="comment-form" @submit.prevent="submitComment">
        <textarea v-model="commentContent" rows="3" minlength="2" placeholder="发表你的看法"></textarea>
        <button type="submit" :disabled="commentSubmitting || !commentContent.trim()">{{ commentSubmitting ? "提交中" : "发表评论" }}</button>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import dayjs from "dayjs";
import {
  fetchPosts,
  createPost,
  sendReaction,
  type PostItem,
  type PostCreatePayload,
  fetchComments,
  createComment,
  type CommentItem
} from "@/api/post";

const posts = ref<PostItem[]>([]);
const comments = ref<CommentItem[]>([]);
const activePost = ref<PostItem | null>(null);
const status = ref("approved");
const loading = ref(false);
const formMessage = ref("");
const formError = ref("");
const commentContent = ref("");
const commentSubmitting = ref(false);

const statusMap: Record<string, string> = {
  draft: "草稿",
  pending: "待审核",
  approved: "已发布",
  rejected: "已驳回"
};

const postForm = reactive<PostCreatePayload>({
  title: "",
  topic: "",
  content_md: "",
  submit_for_review: true
});

async function loadPosts() {
  const response = await fetchPosts({ status: status.value });
  posts.value = response.items;
  if (posts.value.length) {
    selectPost(posts.value[0]);
  } else {
    activePost.value = null;
    comments.value = [];
  }
}

async function selectPost(post: PostItem) {
  activePost.value = post;
  comments.value = await fetchComments(post.id);
}

async function handleSubmit() {
  loading.value = true;
  formMessage.value = "";
  formError.value = "";
  try {
    await createPost({ ...postForm });
    formMessage.value = postForm.submit_for_review ? "帖子已提交审核" : "草稿保存成功";
    Object.assign(postForm, { title: "", topic: "", content_md: "", submit_for_review: true });
    await loadPosts();
  } catch (err: unknown) {
    formError.value = err instanceof Error ? err.message : String(err);
  } finally {
    loading.value = false;
  }
}

async function sendLike(postId: number) {
  try {
    await sendReaction({ reaction_type: "like", target_type: "post", target_id: postId });
    await loadPosts();
  } catch (error) {
    console.error(error);
  }
}

async function sendFavorite(postId: number) {
  try {
    await sendReaction({ reaction_type: "favorite", target_type: "post", target_id: postId });
    await loadPosts();
  } catch (error) {
    console.error(error);
  }
}

async function submitComment() {
  if (!activePost.value || !commentContent.value.trim()) {
    return;
  }
  commentSubmitting.value = true;
  try {
    await createComment(activePost.value.id, { content: commentContent.value });
    commentContent.value = "";
    comments.value = await fetchComments(activePost.value.id);
  } catch (error) {
    console.error(error);
  } finally {
    commentSubmitting.value = false;
  }
}

function formatTime(value: string) {
  return dayjs(value).format("YYYY-MM-DD HH:mm");
}

onMounted(() => {
  loadPosts();
});
</script>

<style scoped>
.interaction {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) minmax(260px, 320px) minmax(320px, 1fr);
  gap: 20px;
  align-items: start;
}

.post-form,
.post-list,
.comments {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-form form,
.comment-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-form label,
.checkbox {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  color: #475467;
}

input,
textarea,
select {
  padding: 10px;
  border: 1px solid #d0d5dd;
  border-radius: 10px;
}

.checkbox {
  flex-direction: row;
  align-items: center;
}

.checkbox input {
  width: auto;
  margin-right: 8px;
}

button[type="submit"] {
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: #6366f1;
  color: #fff;
  font-weight: 600;
}

.message {
  color: #047857;
}

.error {
  color: #b91c1c;
}

.post-list ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-list li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.post-list li:hover,
.post-list li.active {
  border-color: #6366f1;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.12);
}

.post-list h4 {
  margin: 0;
  font-size: 16px;
}

.post-list .meta {
  margin: 4px 0 0;
  font-size: 12px;
  color: #94a3b8;
}

.post-list .actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.post-list .actions button {
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  padding: 6px 12px;
  background: #f8fafc;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-list article {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px;
}

.comment-list .content {
  margin: 0 0 6px;
}

.comment-list .time {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

.empty {
  text-align: center;
  color: #94a3b8;
}

@media (max-width: 1100px) {
  .interaction {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
}
</style>
