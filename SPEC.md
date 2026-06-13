# 跑步训练计划后端服务规格说明

## 1. 项目概述

### 项目名称
RunPlan API - 智能跑步训练计划后端服务

### 核心功能
为跑步 App、赛事报名平台和社群教练提供智能化的跑步训练计划生成和管理服务，支持 5 公里、半程马拉松和全程马拉松三种赛事类型。

### 目标用户
- 跑步爱好者（普通用户）
- 社群跑步教练
- 第三方跑步应用和平台

## 2. 技术架构

### 技术栈
- **后端框架**: Python 3.11 + FastAPI
- **数据库**: SQLite (开发环境) / PostgreSQL (生产环境)
- **ORM**: SQLAlchemy
- **API 文档**: Swagger/OpenAPI (自动生成)
- **验证**: Pydantic

### 项目结构
```
running_training_service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置文件
│   ├── database.py             # 数据库连接
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py             # 用户模型
│   │   ├── plan.py             # 训练计划模型
│   │   ├── workout.py          # 训练课次模型
│   │   └── coach.py            # 教练点评模型
│   ├── schemas/                # Pydantic 模式
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── plan.py
│   │   └── workout.py
│   ├── routers/                # API 路由
│   │   ├── __init__.py
│   │   ├── users.py            # 用户管理
│   │   ├── plans.py            # 计划管理
│   │   ├── workouts.py         # 训练记录
│   │   ├── coach.py            # 教练功能
│   │   └── reports.py          # 报告生成
│   ├── services/               # 业务逻辑
│   │   ├── __init__.py
│   │   ├── plan_generator.py   # 计划生成器
│   │   ├── pace_calculator.py   # 配速计算
│   │   ├── fatigue_tracker.py  # 疲劳追踪
│   │   └── prediction.py       # 完赛预测
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── training_types.py   # 训练类型定义
│       └── constants.py        # 常量定义
├── tests/                      # 测试文件
├── requirements.txt            # 依赖
└── README.md
```

## 3. 数据模型设计

### 3.1 用户模型 (User)
```python
{
    "id": UUID,
    "username": str,                    # 用户名
    "email": str,                       # 邮箱
    "height": float,                    # 身高(cm)
    "weight": float,                    # 体重(kg)
    "age": int,                         # 年龄
    "gender": str,                      # 性别
    "current_pace": float,              # 当前配速(秒/公里)
    "weekly_mileage": float,            # 当前周跑量(公里)
    "injury_history": List[str],         # 伤病史
    "available_days": List[int],        # 可训练日期(0-6, 周一到周日)
    "created_at": datetime,
    "updated_at": datetime
}
```

### 3.2 训练计划模型 (TrainingPlan)
```python
{
    "id": UUID,
    "user_id": UUID,                    # 关联用户
    "race_type": str,                    # 赛事类型: "5K", "HALF_MARATHON", "MARATHON"
    "race_date": date,                  # 比赛日期
    "target_time": str,                 # 目标时间(HH:MM:SS)
    "start_date": date,                 # 计划开始日期
    "status": str,                      # 状态: "active", "completed", "paused"
    "current_phase": str,               # 当前阶段: "base", "build", "peak", "taper"
    "created_at": datetime,
    "updated_at": datetime
}
```

### 3.3 训练课次模型 (Workout)
```python
{
    "id": UUID,
    "plan_id": UUID,                    # 关联计划
    "date": date,                       # 训练日期
    "week_number": int,                 # 第几周
    "day_number": int,                  # 第几天
    "workout_type": str,                # 训练类型
    "distance": float,                  # 距离(公里)
    "duration": int,                    # 时长(分钟)
    "target_pace": str,                 # 目标配速
    "pace_zones": List[dict],           # 配速区间
    "description": str,                 # 描述
    "notes": str,                       # 备注
    "gear_reminder": str,               # 装备提醒
    "nutrition_tip": str,               # 补给建议
    "status": str,                     # 状态: "scheduled", "completed", "missed"
    "actual_distance": float,           # 实际距离
    "actual_duration": int,             # 实际时长
    "actual_pace": float,               # 实际配速
    "fatigue_level": int,               # 疲劳等级(1-10)
    "completed_at": datetime,
    "check_in_id": UUID                 # 打卡记录ID
}
```

### 3.4 打卡记录模型 (CheckIn)
```python
{
    "id": UUID,
    "workout_id": UUID,                 # 关联训练课次
    "user_id": UUID,                    # 关联用户
    "distance": float,                  # 实际距离
    "duration": int,                    # 实际时长
    "pace": float,                      # 实际配速
    "heart_rate": int,                  # 心率(可选)
    "calories": int,                    # 消耗卡路里
    "feeling": int,                    # 主观感受(1-10)
    "notes": str,                       # 打卡备注
    "photo_url": str,                   # 照片URL(可选)
    "created_at": datetime
}
```

### 3.5 教练点评模型 (CoachComment)
```python
{
    "id": UUID,
    "plan_id": UUID,                    # 关联计划
    "workout_id": UUID,                 # 关联训练课次(可选)
    "coach_id": UUID,                   # 教练ID
    "content": str,                     # 点评内容
    "rating": int,                      # 评分(1-5)
    "created_at": datetime
}
```

### 3.6 阶段报告模型 (PhaseReport)
```python
{
    "id": UUID,
    "plan_id": UUID,                    # 关联计划
    "phase": str,                       # 阶段: "base", "build", "peak", "taper"
    "week_number": int,                 # 第几周
    "total_distance": float,            # 总距离
    "completed_distance": float,        # 完成距离
    "completion_rate": float,          # 完成率
    "average_pace": float,              # 平均配速
    "fatigue_trend": List[int],         # 疲劳趋势
    "improvement_notes": str,           # 改进建议
    "created_at": datetime
}
```

## 4. 训练类型定义

### 4.1 训练类型枚举
```python
WORKOUT_TYPES = {
    "EASY_RUN": "轻松跑",
    "INTERVAL": "间歇跑",
    "TEMPO_RUN": "节奏跑",
    "LONG_RUN": "长距离跑",
    "RECOVERY_RUN": "恢复跑",
    "STRENGTH": "力量训练",
    "STRETCH": "拉伸恢复",
    "TEST_RUN": "测试跑",
    "REST": "休息日",
    "CROSS_TRAIN": "交叉训练"
}
```

### 4.2 配速区间定义
```python
PACE_ZONES = {
    "Z1": {"name": "轻松区", "min_pct": 0.5, "max_pct": 0.6},   # 恢复/轻松跑
    "Z2": {"name": "有氧区", "min_pct": 0.6, "max_pct": 0.7},   # 长距离/轻松跑
    "Z3": {"name": "马拉松区", "min_pct": 0.7, "max_pct": 0.8}, # 节奏跑
    "Z4": {"name": "乳酸阈值区", "min_pct": 0.8, "max_pct": 0.88}, # 间歇
    "Z5": {"name": "无氧区", "min_pct": 0.88, "max_pct": 1.0}   # 高强度间歇
}
```

## 5. 训练计划生成算法

### 5.1 赛事周期划分
- **基础期 (Base Phase)**: 8-12 周
  - 目标: 建立有氧基础，提升跑量
  - 训练重点: 轻松跑为主，长距离跑逐步增加

- **强化期 (Build Phase)**: 4-6 周
  - 目标: 提升速度和耐力
  - 训练重点: 增加间歇跑和节奏跑比例

- **巅峰期 (Peak Phase)**: 2-4 周
  - 目标: 达到最佳竞技状态
  - 训练重点: 高强度训练，维持跑量

- **减量期 (Taper Phase)**: 2-3 周
  - 目标: 充分恢复，保证比赛状态
  - 训练重点: 减少训练量，保持竞技感觉

### 5.2 周训练结构
- **5K 计划 (12 周)**
  - 基础期: 1-4 周
  - 强化期: 5-8 周
  - 巅峰期: 9-10 周
  - 减量期: 11-12 周

- **半程马拉松计划 (16 周)**
  - 基础期: 1-6 周
  - 强化期: 7-11 周
  - 巅峰期: 12-14 周
  - 减量期: 15-16 周

- **全程马拉松计划 (20 周)**
  - 基础期: 1-8 周
  - 强化期: 9-14 周
  - 巅峰期: 15-17 周
  - 减量期: 18-20 周

### 5.3 计划生成输入参数
```python
{
    "race_type": str,           # 赛事类型
    "race_date": date,          # 比赛日期
    "current_pace": float,      # 当前配速(秒/公里)
    "weekly_mileage": float,    # 当前周跑量(公里)
    "target_time": str,         # 目标时间
    "injury_history": List[str], # 伤病史
    "available_days": List[int]  # 可训练日期
}
```

### 5.4 训练计划生成规则
1. 根据比赛日期倒推确定计划开始日期
2. 根据伤病史调整训练强度和内容
3. 根据可用训练日分配训练课次
4. 确保周跑量递增不超过 10%
5. 长距离跑安排在周末
6. 高强度训练后安排恢复日

## 6. API 端点设计

### 6.1 用户管理 API
```
POST   /api/v1/users                    # 创建用户
GET    /api/v1/users/{user_id}          # 获取用户信息
PUT    /api/v1/users/{user_id}          # 更新用户信息
DELETE /api/v1/users/{user_id}          # 删除用户
GET    /api/v1/users/{user_id}/profile  # 获取用户训练档案
```

### 6.2 训练计划 API
```
POST   /api/v1/plans                    # 创建训练计划
GET    /api/v1/plans/{plan_id}          # 获取计划详情
GET    /api/v1/plans/user/{user_id}     # 获取用户所有计划
PUT    /api/v1/plans/{plan_id}          # 更新计划
DELETE /api/v1/plans/{plan_id}          # 删除计划
POST   /api/v1/plans/{plan_id}/generate # 生成训练计划
GET    /api/v1/plans/{plan_id}/overview # 获取计划概览
PUT    /api/v1/plans/{plan_id}/reschedule # 重新排课
```

### 6.3 训练课次 API
```
GET    /api/v1/workouts/plan/{plan_id}  # 获取计划所有课次
GET    /api/v1/workouts/{workout_id}    # 获取课次详情
PUT    /api/v1/workouts/{workout_id}    # 更新课次
POST   /api/v1/workouts/{workout_id}/complete # 完成训练
GET    /api/v1/workouts/next-week       # 获取下周训练重点
```

### 6.4 打卡记录 API
```
POST   /api/v1/checkins                 # 创建打卡记录
GET    /api/v1/checkins/user/{user_id}  # 获取用户打卡记录
GET    /api/v1/checkins/workout/{workout_id} # 获取课次打卡记录
PUT    /api/v1/checkins/{checkin_id}    # 更新打卡记录
```

### 6.5 教练端 API
```
POST   /api/v1/coach/comments           # 追加点评
GET    /api/v1/coach/comments/plan/{plan_id} # 获取计划所有点评
GET    /api/v1/coach/athletes            # 获取教练管理的运动员
PUT    /api/v1/coach/comments/{comment_id} # 更新点评
DELETE /api/v1/coach/comments/{comment_id} # 删除点评
```

### 6.6 报告与分析 API
```
GET    /api/v1/reports/{plan_id}/phase  # 获取阶段报告
GET    /api/v1/reports/{plan_id}/progress # 获取进度报告
GET    /api/v1/reports/{user_id}/prediction # 完赛预测
GET    /api/v1/reports/{plan_id}/fatigue # 疲劳风险提示
```

### 6.7 工具 API
```
POST   /api/v1/utils/pace-calculate     # 计算配速区间
POST   /api/v1/utils/pace-convert       # 配速单位转换
GET    /api/v1/utils/training-types     # 获取训练类型列表
POST   /api/v1/utils/heart-rate-zones   # 计算心率区间
```

## 7. 核心业务功能

### 7.1 配速区间计算
根据用户的 5K 或 10K 最好成绩，使用 Jack Daniels 公式计算各配速区间：
- VDOT 计算
- 目标配速推算
- 区间配速生成

### 7.2 疲劳风险提示
- 根据连续高强度训练天数判断
- 根据周跑量增幅判断
- 根据用户反馈的疲劳等级判断
- 根据伤病史判断
- 提供风险等级和调整建议

### 7.3 缺课重排
- 自动检测错过的训练
- 提供重排建议
- 调整后续训练计划
- 保持周期完整性

### 7.4 减量周规划
- 赛前 2-3 周自动进入减量期
- 周跑量递减 40-60%
- 保持关键训练
- 调整恢复比例

### 7.5 完赛预测
根据当前训练数据和历史表现：
- 预测完赛时间
- 信心指数
- 风险评估
- 配速建议

### 7.6 阶段报告生成
每周期结束时生成：
- 完成率统计
- 配速变化趋势
- 训练负荷分析
- 下一阶段建议

## 8. 请求/响应示例

### 8.1 创建训练计划
**请求:**
```json
POST /api/v1/plans
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "race_type": "HALF_MARATHON",
    "race_date": "2026-10-15",
    "target_time": "01:45:00",
    "current_pace": 330,
    "weekly_mileage": 35.0,
    "injury_history": [],
    "available_days": [1, 2, 3, 4, 5, 6]
}
```

**响应:**
```json
{
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "race_type": "HALF_MARATHON",
    "race_date": "2026-10-15",
    "target_time": "01:45:00",
    "start_date": "2026-06-15",
    "status": "active",
    "current_phase": "base",
    "total_weeks": 16,
    "message": "训练计划已生成，共 16 周"
}
```

### 8.2 获取下周训练重点
**请求:**
```json
GET /api/v1/workouts/next-week?user_id=550e8400-e29b-41d4-a716-446655440000&plan_id=660e8400-e29b-41d4-a716-446655440001
```

**响应:**
```json
{
    "week_number": 5,
    "focus": "提升有氧耐力，增加间歇跑比例",
    "total_distance": 42.5,
    "workouts": [
        {
            "day": "周一",
            "type": "EASY_RUN",
            "distance": 6.0,
            "description": "轻松跑，保持在有氧区"
        },
        {
            "day": "周二",
            "type": "INTERVAL",
            "distance": 10.0,
            "description": "6x1000m间歇，休息400m"
        },
        {
            "day": "周三",
            "type": "RECOVERY_RUN",
            "distance": 5.0,
            "description": "恢复跑，配速偏慢"
        },
        {
            "day": "周四",
            "type": "TEMPO_RUN",
            "distance": 10.0,
            "description": "节奏跑，10公里目标配速"
        },
        {
            "day": "周五",
            "type": "REST",
            "distance": 0,
            "description": "休息或拉伸"
        },
        {
            "day": "周六",
            "type": "STRENGTH",
            "distance": 0,
            "description": "核心力量训练"
        },
        {
            "day": "周日",
            "type": "LONG_RUN",
            "distance": 16.0,
            "description": "长距离跑，保持稳定配速"
        }
    ],
    "gear_reminder": "本周长距离建议穿着缓震性能好的跑鞋",
    "nutrition_tip": "长距离训练前补充碳水化合物，训练中注意补水"
}
```

### 8.3 完赛预测
**请求:**
```json
GET /api/v1/reports/550e8400-e29b-41d4-a716-446655440000/prediction?plan_id=660e8400-e29b-41d4-a716-446655440001
```

**响应:**
```json
{
    "predicted_time": "01:42:30",
    "confidence": 0.85,
    "pace_strategy": {
        "first_half": "04:52/km",
        "second_half": "04:58/km",
        "note": "建议前半程略快，保持体力在后半程"
    },
    "risk_assessment": "中等风险，注意补给",
    "recommendations": [
        "赛前两周减少训练量",
        "比赛日早起补充碳水",
        "每5公里补充运动饮料"
    ]
}
```

## 9. 错误处理

### 错误代码定义
```python
ERROR_CODES = {
    "USER_NOT_FOUND": "用户不存在",
    "PLAN_NOT_FOUND": "训练计划不存在",
    "WORKOUT_NOT_FOUND": "训练课次不存在",
    "INVALID_DATE_RANGE": "日期范围无效",
    "INSUFFICIENT_DATA": "数据不足，无法生成计划",
    "PLAN_ALREADY_GENERATED": "计划已生成，无法重复生成",
    "INVALID_RACE_TYPE": "无效的赛事类型",
    "INVALID_PACE": "配速格式错误",
    "FATIUGUE_RISK": "检测到疲劳风险，建议调整训练"
}
```

## 10. 性能要求

- API 响应时间 < 200ms
- 计划生成时间 < 3s
- 数据库查询优化，建立必要索引
- 支持并发请求

## 11. 安全考虑

- 用户数据加密存储
- API 认证和授权（预留接口）
- 输入参数验证
- SQL 注入防护
- Rate Limiting

## 12. 扩展性设计

- 模块化架构，便于功能扩展
- 支持插件式训练模板
- 可配置的难度等级
- 多语言支持（预留）

## 13. 测试覆盖

### 单元测试
- 配速计算测试
- 训练计划生成测试
- 疲劳检测测试
- 完赛预测测试

### 集成测试
- API 端点测试
- 数据库操作测试
- 业务流程测试
