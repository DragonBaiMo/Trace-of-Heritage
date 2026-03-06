<template>
  <div class="audit-page">
    <header class="audit-header">
      <div>
        <h3>审计日志留痕</h3>
        <p>聚合展示最近的关键操作，便于追踪责任主体与操作内容。</p>
      </div>
      <div class="actions">
        <label>
          展示条数
          <select v-model.number="limit" @change="loadAudits">
            <option v-for="option in limitOptions" :key="option" :value="option">{{ option }}</option>
          </select>
        </label>
      </div>
    </header>

    <table>
      <thead>
        <tr>
          <th>时间</th>
          <th>操作人</th>
          <th>动作</th>
          <th>目标</th>
          <th>来源 IP</th>
          <th>操作备注</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in audits" :key="item.id">
          <td>{{ formatTime(item.created_at) }}</td>
          <td>#{{ item.actor_id }}</td>
          <td>{{ translateAction(item.action) }}</td>
          <td>{{ item.target_type }} · {{ item.target_id }}</td>
          <td>{{ item.ip ?? "-" }}</td>
          <td>
            <pre v-if="item.note" class="detail">{{ item.note }}</pre>
            <span v-else class="placeholder">暂无</span>
          </td>
        </tr>
        <tr v-if="!audits.length">
          <td colspan="6" class="empty">暂无日志记录</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import dayjs from "dayjs";
import { fetchAuditLogs, type AuditLogItem } from "@/api/audit";

const audits = ref<AuditLogItem[]>([]);
const limit = ref(20);
const limitOptions = [10, 20, 50, 100];

async function loadAudits() {
  audits.value = await fetchAuditLogs(limit.value);
}

function formatTime(value: string) {
  return dayjs(value).format("YYYY-MM-DD HH:mm:ss");
}

function translateAction(action: string) {
  const mapping: Record<string, string> = {
    create_resource: "提交资源",
    update_resource: "更新资源",
    update_user: "调整用户",
    create_post: "发布帖子",
    create_comment: "发表评论",
    create_activity: "创建活动",
    enroll: "活动报名",
    checkin: "活动签到",
    review_resource_approve: "资源审核通过",
    review_resource_reject: "资源审核驳回",
    review_activity_approve: "活动审核通过",
    review_activity_reject: "活动审核驳回",
  };
  return mapping[action] ?? action;
}

onMounted(() => {
  loadAudits();
});
</script>

<style scoped>
.audit-page {
  background: #fff;
  border-radius: 16px;
  padding: 24px 28px 32px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.audit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.audit-header h3 {
  margin: 0;
}

.audit-header p {
  margin: 6px 0 0;
  color: #64748b;
}

.actions label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #475467;
}

select {
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid #d0d5dd;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8fafc;
}

th,
td {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
  vertical-align: top;
}

.detail {
  margin: 0;
  background: #f1f5f9;
  padding: 8px 12px;
  border-radius: 10px;
  white-space: pre-wrap;
}

.placeholder {
  color: #94a3b8;
}

.empty {
  text-align: center;
  color: #94a3b8;
  padding: 24px 0;
}
</style>
