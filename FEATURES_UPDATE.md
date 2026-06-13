# RunPlan API - 跑步训练计划后端服务

## 功能更新日志

### 2026年6月14日 - 第二轮功能完善

#### 1. 按周查看计划接口 ✅
- **接口**: `GET /api/v1/workouts/weekly`
- **参数**:
  - `plan_id`: 计划ID
  - `reference_date`: 任意一天的日期（格式: YYYY-MM-DD）
- **返回**:
  - 当前周次和周范围
  - 每周每天的训练安排（包含训练类型、距离、目标配速、描述、状态等）
  - 总距离、训练课次数、完成率
  - 与训练列表保持完全一致

#### 2. 训练补录功能 ✅
- **接口**: `POST /api/v1/workouts/{workout_id}/makeup`
- **功能**: 漏打卡时手动补录真实完成记录
- **参数**:
  - `actual_distance`: 实际距离
  - `actual_duration`: 实际时长
  - `fatigue_level`: 疲劳等级（1-10）
  - `notes`: 备注
- **返回**: 补录成功信息和更新后的计划统计

#### 3. 训练撤回功能 ✅
- **接口**: `POST /api/v1/workouts/{workout_id}/undo`
- **功能**: 撤回已完成的打卡记录
- **参数**:
  - `reason`: 撤回原因
- **返回**: 撤回成功信息和更新后的计划统计
- **特性**: 补录或撤回后，疲劳风险、总跑量、计划完成度等统计会自动重算

#### 4. 疲劳分析深化 ✅
- **接口**: `GET /api/v1/reports/{plan_id}/fatigue`
- **新增功能**:
  - **两周负荷走势**:
    - 第1周和第2周的详细数据
    - 总距离、高强度训练次数、平均疲劳值、训练课次数
  - **负荷走势分析**:
    - 强度趋势（increasing/decreasing/stable）
    - 负荷趋势（increasing/decreasing/stable）
    - 智能描述（如："⚠️ 高强度+高负荷同时增加，风险上升"）
  - **高强度分布**: 统计间歇跑、节奏跑、测试跑等高强度训练的分布

#### 5. 改期优化（自动顺开冲突） ✅
- **接口**: `PUT /api/v1/plans/{plan_id}/reschedule`
- **优化功能**:
  - 移到已有训练的日子时，自动顺开前后课次
  - 不用反复试空白日期
  - 返回受影响训练列表
  - 验证无日期冲突
  - 保持课次总数不变
  - 更新所有课次的周次信息

### API 端点汇总

#### 用户管理
- `POST /api/v1/users` - 创建用户
- `GET /api/v1/users/{user_id}` - 获取用户信息
- `PUT /api/v1/users/{user_id}` - 更新用户信息
- `GET /api/v1/users/{user_id}/profile` - 获取用户训练档案

#### 训练计划
- `POST /api/v1/plans` - 创建训练计划
- `GET /api/v1/plans/{plan_id}` - 获取计划详情
- `POST /api/v1/plans/{plan_id}/generate` - 生成训练计划
- `GET /api/v1/plans/{plan_id}/overview` - 获取计划概览
- `PUT /api/v1/plans/{plan_id}/reschedule` - 缺课重排（自动顺开冲突）

#### 训练记录
- `GET /api/v1/workouts/plan/{plan_id}` - 获取计划所有课次
- `GET /api/v1/workouts/weekly` - 按周查看计划 ✅
- `GET /api/v1/workouts/{workout_id}` - 获取课次详情
- `POST /api/v1/workouts/{workout_id}/complete` - 完成训练
- `POST /api/v1/workouts/{workout_id}/makeup` - 训练补录 ✅
- `POST /api/v1/workouts/{workout_id}/undo` - 训练撤回 ✅

#### 打卡记录
- `POST /api/v1/checkins` - 创建打卡记录
- `GET /api/v1/checkins/user/{user_id}` - 获取用户打卡记录

#### 教练端
- `POST /api/v1/coach/comments` - 追加点评
- `GET /api/v1/coach/comments/plan/{plan_id}` - 获取计划所有点评
- `GET /api/v1/coach/athletes` - 获取教练管理的运动员

#### 报告与分析
- `GET /api/v1/reports/{plan_id}/phase` - 获取阶段报告
- `GET /api/v1/reports/{plan_id}/progress` - 获取进度报告
- `GET /api/v1/reports/{user_id}/prediction` - 完赛预测
- `GET /api/v1/reports/{plan_id}/fatigue` - 疲劳风险提示（含两周走势）✅

## 使用示例

### 按周查看训练计划
```bash
curl "http://localhost:8000/api/v1/workouts/weekly?plan_id=<plan_id>&reference_date=2026-06-15"
```

### 训练补录
```bash
curl -X POST "http://localhost:8000/api/v1/workouts/<workout_id>/makeup" \
  -H "Content-Type: application/json" \
  -d '{
    "actual_distance": 10.5,
    "actual_duration": 55,
    "fatigue_level": 6,
    "notes": "补录漏掉的训练"
  }'
```

### 训练撤回
```bash
curl -X POST "http://localhost:8000/api/v1/workouts/<workout_id>/undo" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "打错了，需要重新记录"
  }'
```

### 查看疲劳分析（含两周走势）
```bash
curl "http://localhost:8000/api/v1/reports/<plan_id>/fatigue"
```

### 缺课重排（自动顺开冲突）
```bash
curl -X PUT "http://localhost:8000/api/v1/plans/<plan_id>/reschedule" \
  -H "Content-Type: application/json" \
  -d '{
    "missed_workout_id": "<workout_id>",
    "target_date": "2026-06-20"
  }'
```

## 关键特性

1. **数据一致性**: 周视图和训练列表看到的信息完全一致
2. **实时统计**: 补录、撤回后统计立即重算
3. **智能冲突处理**: 自动顺开冲突训练，无需手动试日期
4. **深度分析**: 疲劳分析包含两周负荷走势和高强度分布
5. **完整性验证**: 重排后验证课次总数、日期顺序、周次归属

## 数据库
- SQLite 数据库文件: `running_training.db`
- 服务运行中自动创建和更新

## 启动服务
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API 文档
访问 http://localhost:8000/docs 查看完整的 Swagger UI 文档
