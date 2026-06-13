# RunPlan API - 智能跑步训练计划后端服务

## 项目简介

RunPlan API 是一个智能跑步训练计划后端服务，支持为跑步 App、赛事报名平台和社群教练提供个性化的训练计划生成和管理功能。

## 功能特性

- **多赛事支持**: 5公里、半程马拉松、全程马拉松
- **智能计划生成**: 根据目标赛事、比赛日期、当前配速、周跑量、伤病史和可训练日期自动生成训练计划
- **多样化训练类型**: 轻松跑、间歇跑、节奏跑、长距离跑、力量训练、拉伸恢复等
- **配速区间计算**: 基于VDOT的Jack Daniels配速计算
- **疲劳风险提示**: 智能监测训练负荷和疲劳风险
- **完赛预测**: 基于训练数据预测完赛时间
- **阶段报告**: 自动生成基础期、强化期、巅峰期、减量期报告
- **教练点评**: 教练可追加点评和评分
- **用户端功能**: 查看下周训练重点、完赛预测等

## 技术栈

- **后端框架**: Python 3.11 + FastAPI
- **数据库**: SQLite (开发环境) / PostgreSQL (生产环境)
- **ORM**: SQLAlchemy
- **API 文档**: Swagger/OpenAPI

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. 访问 API 文档

打开浏览器访问: http://localhost:8000/docs

## API 端点

### 用户管理
- `POST /api/v1/users` - 创建用户
- `GET /api/v1/users/{user_id}` - 获取用户信息
- `PUT /api/v1/users/{user_id}` - 更新用户信息
- `GET /api/v1/users/{user_id}/profile` - 获取用户训练档案

### 训练计划
- `POST /api/v1/plans` - 创建训练计划
- `GET /api/v1/plans/{plan_id}` - 获取计划详情
- `POST /api/v1/plans/{plan_id}/generate` - 生成训练计划
- `GET /api/v1/plans/{plan_id}/overview` - 获取计划概览

### 训练记录
- `GET /api/v1/workouts/plan/{plan_id}` - 获取计划所有课次
- `GET /api/v1/workouts/{workout_id}` - 获取课次详情
- `POST /api/v1/workouts/{workout_id}/complete` - 完成训练
- `GET /api/v1/workouts/next-week` - 获取下周训练重点

### 打卡记录
- `POST /api/v1/checkins` - 创建打卡记录
- `GET /api/v1/checkins/user/{user_id}` - 获取用户打卡记录

### 教练端
- `POST /api/v1/coach/comments` - 追加点评
- `GET /api/v1/coach/comments/plan/{plan_id}` - 获取计划所有点评
- `GET /api/v1/coach/athletes` - 获取教练管理的运动员

### 报告与分析
- `GET /api/v1/reports/{plan_id}/phase` - 获取阶段报告
- `GET /api/v1/reports/{plan_id}/progress` - 获取进度报告
- `GET /api/v1/reports/{user_id}/prediction` - 完赛预测
- `GET /api/v1/reports/{plan_id}/fatigue` - 疲劳风险提示

## 使用示例

### 1. 创建用户

```json
POST /api/v1/users
{
    "username": "runner1",
    "email": "runner@example.com",
    "current_pace": 330,
    "weekly_mileage": 40.0,
    "injury_history": [],
    "available_days": [1, 2, 3, 4, 5, 6]
}
```

### 2. 创建训练计划

```json
POST /api/v1/plans
{
    "user_id": "<user_id>",
    "race_type": "HALF_MARATHON",
    "race_date": "2026-10-15",
    "target_time": "01:45:00",
    "current_pace": 330,
    "weekly_mileage": 40.0,
    "injury_history": [],
    "available_days": [1, 2, 3, 4, 5, 6]
}
```

### 3. 生成训练计划

```bash
POST /api/v1/plans/<plan_id>/generate
```

### 4. 查看下周训练重点

```bash
GET /api/v1/workouts/next-week?user_id=<user_id>&plan_id=<plan_id>
```

### 5. 获取完赛预测

```bash
GET /api/v1/reports/<user_id>/prediction?plan_id=<plan_id>
```

## 数据库

SQLite 数据库文件: `running_training.db`

## 开发说明

- 所有数据模型位于 `app/models/`
- Pydantic schemas 位于 `app/schemas/`
- API 路由位于 `app/routers/`
- 业务逻辑位于 `app/services/`
- 工具函数位于 `app/utils/`

## 训练周期

- **5K**: 12周
  - 基础期: 1-4周
  - 强化期: 5-8周
  - 巅峰期: 9-10周
  - 减量期: 11-12周

- **半程马拉松**: 16周
  - 基础期: 1-6周
  - 强化期: 7-11周
  - 巅峰期: 12-14周
  - 减量期: 15-16周

- **全程马拉松**: 20周
  - 基础期: 1-8周
  - 强化期: 9-14周
  - 巅峰期: 15-17周
  - 减量期: 18-20周

## License

MIT
