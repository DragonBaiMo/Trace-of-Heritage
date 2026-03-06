<template>
  <div class="card">
    <h3>从业者认证</h3>
    <p class="desc">提交您的资质材料，等待管理员审核。</p>

    <form @submit.prevent="onSubmit" class="form">
      <label>真实姓名</label>
      <input v-model.trim="form.realname" required />

      <label>职业/头衔</label>
      <input v-model.trim="form.title" required />

      <label>个人简介</label>
      <textarea v-model.trim="form.bio" rows="4" placeholder="简要介绍您的从业经历"></textarea>

      <label>资质附件链接（临时）</label>
      <input v-model.trim="form.attachment" placeholder="例如：网盘链接或公开作品链接" />

      <button type="submit" :disabled="submitting">{{ submitting ? '提交中...' : '提交认证' }}</button>
    </form>

    <p v-if="result" class="ok">已提交成功，申请编号 #{{ result.id }}，请等待审核结果。</p>
    <p v-if="error" class="err">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { applyPractitioner, type ApplicationRead } from '@/api/practitioner';

const form = reactive({ realname: '', title: '', bio: '', attachment: '' });
const submitting = ref(false);
const result = ref<ApplicationRead | null>(null);
const error = ref<string | null>(null);

async function onSubmit() {
  submitting.value = true;
  error.value = null;
  try {
    result.value = await applyPractitioner({
      realname: form.realname,
      title: form.title,
      bio: form.bio || undefined,
      attachment: form.attachment || undefined,
    });
  } catch (e: any) {
    error.value = e?.message || String(e) || '提交失败';
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.card { background:#fff; border-radius:12px; padding:16px 20px; box-shadow:0 10px 30px rgba(15,23,42,.08); }
.form { display:flex; flex-direction:column; gap:8px; max-width: 600px; }
label { font-size:12px; color:#64748b; }
input, textarea { padding:10px 12px; border:1px solid #d0d5dd; border-radius:8px; }
button { margin-top: 8px; width: 160px; padding: 10px; border-radius: 8px; border: none; background:#16a34a; color:#fff; }
.desc { color:#64748b; }
.ok { color:#16a34a; margin-top:12px; }
.err { color:#ef4444; margin-top:12px; }
</style>
