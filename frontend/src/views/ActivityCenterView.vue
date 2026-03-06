<template>
  <div class="activities">
    <section class="activity-form">
      <h3>发起活动</h3>
      <form @submit.prevent="handleSubmit">
        <label>
          活动标题
          <input v-model="form.title" type="text" required maxlength="80" placeholder="例如：戏曲进校园" />
        </label>
        <label>
          活动地点
          <input v-model="form.location" type="text" required placeholder="例如：福州师范大学礼堂" />
        </label>
        <div class="grid">
          <label>
            开始时间
            <input v-model="form.start_time" type="datetime-local" required />
          </label>
          <label>
            结束时间
            <input v-model="form.end_time" type="datetime-local" required />
          </label>
        </div>
        <label>
          人数上限
          <input v-model.number="form.quota" type="number" min="1" max="500" required />
        </label>
        <label>
          活动介绍
          <textarea v-model="form.description" rows="4" required minlength="20"></textarea>
        </label>
        <label class="checkbox">
          <input v-model="form.submit_for_review" type="checkbox" />
          <span>提交后立即审核（取消则保存草稿）</span>
        </label>
        <button type="submit" :disabled="loading">{{ loading ? "提交中" : "创建活动" }}</button>
        <p v-if="message" class="message">{{ message }}</p>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </section>

    <section class="activity-list">
      <header>
        <h3>活动列表</h3>
        <select v-model="status" @change="loadActivities">
          <option value="approved">已发布</option>
          <option value="pending">待审核</option>
          <option value="draft">草稿</option>
        </select>
      </header>
      <ul>
        <li v-for="item in activities" :key="item.id">
          <div>
            <h4>{{ item.title }}</h4>
            <p class="meta">
              {{ formatTime(item.start_time) }} - {{ formatTime(item.end_time) }} · {{ item.location }}
            </p>
            <p class="desc">{{ item.description }}</p>
          </div>
          <div class="actions">
            <button type="button" @click="enroll(item.id)">报名</button>
            <button type="button" @click="checkin(item.id)">签到</button>
          </div>
        </li>
        <li v-if="!activities.length" class="empty">暂无活动</li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import dayjs from "dayjs";
import { createActivity, fetchActivities, enrollActivity, checkinActivity, type ActivityItem } from "@/api/activity";

interface ActivityForm {
  title: string;
  location: string;
  start_time: string;
  end_time: string;
  quota: number;
  description: string;
  submit_for_review: boolean;
}

const form = reactive<ActivityForm>({
  title: "",
  location: "",
  start_time: "",
  end_time: "",
  quota: 50,
  description: "",
  submit_for_review: true
});

const activities = ref<ActivityItem[]>([]);
const status = ref("approved");
const loading = ref(false);
const message = ref("");
const error = ref("");

async function loadActivities() {
  const response = await fetchActivities(status.value);
  activities.value = response.items;
}

async function handleSubmit() {
  loading.value = true;
  message.value = "";
  error.value = "";
  try {
    await createActivity({ ...form });
    message.value = form.submit_for_review ? "活动已提交审核" : "草稿保存成功";
    Object.assign(form, {
      title: "",
      location: "",
      start_time: "",
      end_time: "",
      quota: 50,
      description: "",
      submit_for_review: true
    });
    await loadActivities();
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : String(err);
  } finally {
    loading.value = false;
  }
}

async function enroll(id: number) {
  try {
    await enrollActivity(id);
    message.value = "报名成功";
  } catch (err) {
    console.error(err);
  }
}

async function checkin(id: number) {
  try {
    await checkinActivity(id);
    message.value = "签到成功";
  } catch (err) {
    console.error(err);
  }
}

function formatTime(value: string) {
  return dayjs(value).format("MM-DD HH:mm");
}

onMounted(() => {
  loadActivities();
});
</script>

<style scoped>
.activities {
  display: grid;
  grid-template-columns: minmax(320px, 1fr) minmax(320px, 1.2fr);
  gap: 20px;
}

.activity-form,
.activity-list {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-form form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #475467;
  font-size: 14px;
}

input,
textarea,
select {
  padding: 10px;
  border: 1px solid #d0d5dd;
  border-radius: 10px;
}

textarea {
  resize: vertical;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
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
  background: #22d3ee;
  color: #0f172a;
  font-weight: 600;
}

.message {
  color: #047857;
}

.error {
  color: #b91c1c;
}

.activity-list header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-list ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-list li {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.activity-list h4 {
  margin: 0;
}

.activity-list .meta {
  margin: 6px 0;
  color: #94a3b8;
  font-size: 12px;
}

.activity-list .desc {
  margin: 0;
  font-size: 14px;
  color: #475467;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.actions button {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
}

.empty {
  text-align: center;
  color: #94a3b8;
}

@media (max-width: 960px) {
  .activities {
    grid-template-columns: 1fr;
  }
}
</style>
