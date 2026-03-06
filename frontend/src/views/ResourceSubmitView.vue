<template>
  <div class="submit-card">
    <h3>资源基础信息</h3>
    <form @submit.prevent="handleSubmit">
      <label>
        标题
        <input v-model="form.title" type="text" required maxlength="80" placeholder="请输入资源名称" />
      </label>
      <label>
        资源类型
        <select v-model="form.resource_type" required>
          <option value="text">文本资料</option>
          <option value="image">图片</option>
          <option value="video">视频</option>
          <option value="doc">文档</option>
        </select>
      </label>
      <label>
        简介
        <textarea
          v-model="form.synopsis"
          maxlength="300"
          rows="3"
          placeholder="请概述资源亮点"
        ></textarea>
      </label>
      <section class="ai-box">
        <header class="ai-head">
          <div>
            <p class="hint">粘贴剧本文本，AI 自动生成 100 字左右简介与标签</p>
          </div>
          <button type="button" class="ghost" :disabled="aiLoading" @click="runAI">
            {{ aiLoading ? "生成中..." : "AI 生成" }}
          </button>
        </header>
        <textarea v-model="aiSource" rows="4" placeholder="将剧本/策划案粘贴到这里，点击 AI 生成"></textarea>
      </section>
      <label>
        标签（使用逗号分隔）
        <input v-model="tagsInput" type="text" placeholder="戏曲,非遗,校园" />
      </label>
      <div class="grid">
        <label>
          所属剧种
          <input v-model="form.genre" type="text" placeholder="例如：莆仙戏" />
        </label>
        <label>
          所在地区编码
          <input v-model="form.region_code" type="text" placeholder="如：350300" />
        </label>
      </div>
      <div class="grid">
        <label>
          作者 / 传承人
          <input v-model="form.author" type="text" placeholder="选填" />
        </label>
        <label>
          版权状态
          <select v-model="form.copyright_status">
            <option value="unknown">未知</option>
            <option value="authorized">已授权</option>
            <option value="restricted">受限</option>
          </select>
        </label>
      </div>
      <label>
        上传文件路径
        <input v-model="form.file_path" type="text" placeholder="例如：/uploads/demo.pdf" />
      </label>
      <label>
        外部链接
        <input v-model="form.external_url" type="url" placeholder="如：https://example.com/resource" />
      </label>

      <section class="trail-section">
        <header>
          <h4>传播轨迹</h4>
          <button type="button" class="ghost" @click="addTrail">+ 添加轨迹点</button>
        </header>
        <p class="hint">按顺序填写重要节点，经纬度采用 WGS84 坐标。</p>
        <div v-if="!form.trails.length" class="empty-trail">暂未添加轨迹信息</div>
        <div v-for="(trail, index) in form.trails" :key="index" class="trail-row">
          <label>
            地点名称
            <input v-model="trail.place_name" type="text" required placeholder="例如：福州" />
          </label>
          <label>
            经度
            <input v-model.number="trail.longitude" type="number" step="0.0001" required />
          </label>
          <label>
            纬度
            <input v-model.number="trail.latitude" type="number" step="0.0001" required />
          </label>
          <label>
            序号
            <input v-model.number="trail.order_no" type="number" min="1" required />
          </label>
          <button type="button" class="delete" @click="removeTrail(index)">删除</button>
        </div>
      </section>

      <label class="checkbox">
        <input v-model="form.submit_for_review" type="checkbox" />
        <span>提交后立即进入审核（取消则保存为草稿）</span>
      </label>

      <button type="submit" :disabled="loading">{{ loading ? "提交中" : "提交资源" }}</button>
      <p v-if="message" class="message">{{ message }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { createResource, type ResourceTrail } from "@/api/resource";
import { generateSynopsis } from "@/api/ai";

interface ResourceForm {
  title: string;
  resource_type: string;
  synopsis: string;
  tags: string[];
  genre: string;
  region_code: string;
  author: string;
  copyright_status: string;
  file_path: string;
  external_url: string;
  submit_for_review: boolean;
  trails: ResourceTrail[];
}

const form = reactive<ResourceForm>({
  title: "",
  resource_type: "text",
  synopsis: "",
  tags: [],
  genre: "",
  region_code: "",
  author: "",
  copyright_status: "unknown",
  file_path: "",
  external_url: "",
  submit_for_review: true,
  trails: []
});

const tagsInput = ref("");
const loading = ref(false);
const message = ref("");
const error = ref("");
const aiSource = ref("");
const aiLoading = ref(false);

function syncTags() {
  form.tags = tagsInput.value
    .split(/[，,]/)
    .map((item) => item.trim())
    .filter((item, index, list) => item && list.indexOf(item) === index);
}

function addTrail() {
  form.trails.push({ place_name: "", longitude: 0, latitude: 0, order_no: form.trails.length + 1 });
}

function removeTrail(index: number) {
  form.trails.splice(index, 1);
}

async function handleSubmit() {
  loading.value = true;
  message.value = "";
  error.value = "";
  try {
    syncTags();
    if (!form.file_path && !form.external_url) {
      throw new Error("请至少提供文件路径或外部链接");
    }
    await createResource({ ...form });
    message.value = form.submit_for_review ? "资源已提交审核" : "草稿保存成功";
    Object.assign(form, {
      title: "",
      resource_type: "text",
      synopsis: "",
      tags: [],
      genre: "",
      region_code: "",
      author: "",
      copyright_status: "unknown",
      file_path: "",
      external_url: "",
      submit_for_review: true,
      trails: []
    });
    tagsInput.value = "";
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : String(err);
  } finally {
    loading.value = false;
  }
}

async function runAI() {
  if (!aiSource.value || aiSource.value.trim().length < 20) {
    error.value = "请先粘贴至少 20 字的文本";
    return;
  }
  error.value = "";
  message.value = "";
  aiLoading.value = true;
  try {
    const result = await generateSynopsis(aiSource.value, 120);
    form.synopsis = result.synopsis;
    const mergedTags = [...new Set([...form.tags, ...result.tags])];
    form.tags = mergedTags;
    tagsInput.value = mergedTags.join(",");
    message.value = "AI 生成完成，可修改后提交";
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : String(err);
  } finally {
    aiLoading.value = false;
  }
}
</script>

<style scoped>
.submit-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  max-width: 760px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

label {
  display: flex;
  flex-direction: column;
  font-size: 14px;
  color: #475467;
  gap: 8px;
}

input,
textarea,
select {
  padding: 12px;
  border: 1px solid #d0d5dd;
  border-radius: 10px;
}

textarea {
  resize: vertical;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.checkbox {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.checkbox input {
  width: auto;
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

.trail-section {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trail-section header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.trail-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  align-items: end;
}

.trail-row .delete {
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px;
  color: #ef4444;
}

.trail-row .delete:hover {
  background: #fee2e2;
}

.ghost {
  border: 1px solid #38bdf8;
  background: #e0f2fe;
  color: #0369a1;
  padding: 8px 12px;
  border-radius: 8px;
}

.hint {
  font-size: 12px;
  color: #64748b;
}

.empty-trail {
  padding: 12px;
  border: 1px dashed #cbd5f5;
  color: #64748b;
  border-radius: 10px;
}

.ai-box {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ai-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
