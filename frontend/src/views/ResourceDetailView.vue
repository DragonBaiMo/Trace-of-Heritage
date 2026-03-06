<template>
  <div class="detail">
    <section class="header">
      <div>
        <p class="eyebrow">资源详情</p>
        <h2>{{ resource?.title }}</h2>
        <p class="muted">类型：{{ resource?.resource_type }} ｜ 状态：{{ statusMap[resource?.status || ''] || resource?.status }}</p>
      </div>
      <RouterLink to="/resources" class="ghost">返回列表</RouterLink>
    </section>

    <section class="grid">
      <article class="card">
        <h3>基础信息</h3>
        <div class="info">
          <p><strong>简介：</strong>{{ resource?.synopsis || "暂无简介" }}</p>
          <p><strong>标签：</strong>
            <span v-for="tag in resource?.tags" :key="tag" class="tag">{{ tag }}</span>
            <span v-if="!resource?.tags?.length" class="tag muted">未设置</span>
          </p>
          <p><strong>作者：</strong>{{ resource?.author || "未填写" }}</p>
          <p><strong>流派：</strong>{{ resource?.genre || "未填写" }}</p>
          <p><strong>地区：</strong>{{ resource?.region_code || "未填写" }}</p>
        </div>
      </article>
      <article class="card map-card">
        <div class="map-head">
          <div>
            <p class="eyebrow">寻迹地图</p>
            <h3>传播路径</h3>
          </div>
          <span class="muted" v-if="resource?.trails?.length">共 {{ resource?.trails.length }} 个轨迹点</span>
        </div>
        <BaseChart :option="mapOption" />
        <div v-if="!resource?.trails?.length" class="empty">暂无轨迹数据</div>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, RouterLink } from "vue-router";
import * as echarts from "echarts/core";
import BaseChart from "@/components/charts/BaseChart.vue";
import { fetchResourceDetail, type ResourceItem } from "@/api/resource";

type TooltipFormatterParam = { name?: string };

const statusMap: Record<string, string> = {
  draft: "草稿",
  pending: "待审核",
  approved: "已通过",
  rejected: "已驳回"
};

const route = useRoute();
const resource = ref<ResourceItem | null>(null);

const mapOption = computed(() => {
  if (!resource.value || !resource.value.trails?.length) {
    return { tooltip: { show: true, formatter: "暂无轨迹数据" } };
  }
  const sorted = [...resource.value.trails].sort((a, b) => a.order_no - b.order_no);
  const scatter = sorted.map((item) => item.place_name);

  return {
    tooltip: {
      trigger: "axis",
      formatter: (params: TooltipFormatterParam[] | TooltipFormatterParam) => {
        const first = Array.isArray(params) ? params[0] : params;
        return first?.name || "轨迹点";
      }
    },
    xAxis: {
      type: "category",
      data: sorted.map((item) => item.place_name),
      axisLabel: { interval: 0, rotate: 35 }
    },
    yAxis: {
      type: "value",
      show: false
    },
    series: [
      {
        type: "line",
        smooth: true,
        data: sorted.map((_item, index) => index + 1),
        lineStyle: { color: "#2563eb", width: 2 },
        itemStyle: { color: "#22c55e" }
      },
      {
        type: "scatter",
        symbolSize: 10,
        itemStyle: { color: "#22c55e" },
        data: scatter.map((item, index) => ({
          name: item,
          value: [index, index + 1]
        }))
      }
    ]
  };
});

async function load() {
  const id = Number(route.params.id);
  resource.value = await fetchResourceDetail(id);
}

onMounted(load);
</script>

<style scoped>
.detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header {
  background: #fff;
  border-radius: 16px;
  padding: 18px 20px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
  display: flex;
  justify-content: space-between;
}

.eyebrow {
  margin: 0;
  color: #94a3b8;
  font-size: 12px;
}

.muted {
  color: #94a3b8;
}

.ghost {
  color: #2563eb;
  font-weight: 600;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.info p {
  margin: 8px 0;
  line-height: 1.5;
}

.tag {
  display: inline-block;
  padding: 4px 8px;
  background: #eef2ff;
  color: #4338ca;
  border-radius: 8px;
  margin-right: 6px;
}

.tag.muted {
  background: #e2e8f0;
  color: #475569;
}

.map-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.map-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty {
  text-align: center;
  color: #94a3b8;
}
</style>
