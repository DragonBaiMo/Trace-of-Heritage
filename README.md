# 遗迹之光（Trace-of-Heritage）

基于 FastAPI + Vue3 的非遗/戏曲数字化平台，支持资源提交审核、轨迹可视化、水印保护、积分商城、每日问答、个性化推荐与 AI 简介生成。

## 功能概览
- 资源管理：提交/审核/轨迹维护，资源详情地图展示轨迹线和节点。
- 媒体水印：上传图片自动添加半透明文字水印（标题-作者），失败时返回中文提示但不阻断流程。
- 个性化推荐：基于点赞/收藏的流派与标签，返回“猜你喜欢”资源列表。
- 积分商城：商品维护、下单扣积分、订单发货/收货流转（pending → shipped → completed）。
- 每日一题：每日自动生成或预置题目，答对发积分，防重复作答。
- 数据导出：管理员一键导出用户/资源 Excel（过滤敏感字段）。
- AI 简介生成：调用大模型生成 100 字左右简介和标签，缺密钥时使用占位生成。

## 目录结构
```
backend/   # FastAPI 服务，SQLAlchemy ORM，业务路由与服务
frontend/  # Vue3 + Vite 前端，Pinia 状态管理，ECharts 可视化
```

## 环境要求
- Python 3.10+
- Node.js 18+
- SQLite 默认即可；可改为 MySQL/PostgreSQL（修改 env 中数据库 URL）

## 后端启动
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env    # 按需修改
uvicorn app.main:app --reload
```

### 核心配置（`.env`）
- `SQLITE_PATH`：数据库文件，默认 `data/app.db`
- `MEDIA_ROOT`：上传/水印输出目录，默认 `data/uploads`
- `AI_BASE_URL`：大模型接口地址，默认 SiliconFlow 示例
- `AI_MODEL`：模型名称，默认 `Qwen/Qwen3-Omni-30B-A3B-Instruct`
- `AI_API_KEY`：大模型密钥（不填则使用占位生成，不外呼接口）
- 默认账号：`admin/Admin123`、`opera_practitioner/Practitioner123`、`heritage_user/Heritage123`（仅用于开发，请修改）

### 关键后端接口
- 资源：`POST /api/resources` 创建（含水印）；`GET /api/resources/{id}/trails` 轨迹；`GET /api/recommendations` 推荐
- 商城：`POST /api/shop/orders` 下单；`POST /api/shop/orders/{id}/confirm` 收货；`POST /api/shop/admin/orders/{id}/ship` 发货
- 问答：`GET /api/quiz/today` 获取题目；`POST /api/quiz/answer` 作答
- 导出：`GET /api/admin/export?type=users|resources` 下载 Excel
- AI：`POST /api/ai/synopsis` 生成简介与标签（需密钥）

## 前端启动
```bash
cd frontend
npm install
npm run dev
```
- 主要入口：`src/views/DashboardView.vue`（含每日一题、猜你喜欢）、`ResourceDetailView.vue`（轨迹地图）、`ShopView.vue`（订单收货）、`AdminOrdersView.vue`（发货）、`ResourceSubmitView.vue`（AI 生成简介）。

## 验收建议
1) 提交图片资源，确认水印生成（文件名带 `_wm`）；无水印时看中文提示。
2) 打开资源详情，地图上出现轨迹点连线；无轨迹时提示“暂无轨迹数据”。
3) 首页“每日一题”作答一次即锁定，当天答对积分增加；“猜你喜欢”随点赞/收藏变化。
4) 商城下单后状态为待发货；管理员发货后用户可确认收货，状态按顺序流转。
5) 管理员可点击导出用户/资源为 Excel，文件可直接打开。
6) 资源提交页粘贴文本点击 AI 生成，如未配置密钥则走占位生成并提示成功。

## 迁移与扩展
- 数据库切换：在 `.env` 改写为数据库 URL（如 MySQL/PostgreSQL），SQLAlchemy 模型兼容。
- AI 供应商：调整 `AI_BASE_URL`、`AI_MODEL`、`AI_API_KEY` 即可，无需改业务代码。
- 静态文件：`MEDIA_ROOT` 可指向持久化挂载目录，便于水印文件存储。

## 常见问题
- AI 未返回内容：检查 `AI_API_KEY` 是否配置正确；未配置时属于预期，占位生成仍可用。
- 水印未生效：确认 `MEDIA_ROOT` 可写且文件路径正确，支持的格式为 png/jpg/jpeg/webp。
- 库存/积分不同步：发货与收货不影响积分，仅下单会扣减；库存不足会返回中文业务错误。
