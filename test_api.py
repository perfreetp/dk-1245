import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    print("=" * 60)
    print("RunPlan API 测试")
    print("=" * 60)

    print("\n1. 创建测试用户...")
    user_data = {
        "username": "test_runner",
        "email": "test@example.com",
        "current_pace": 330,
        "weekly_mileage": 40.0,
        "injury_history": [],
        "available_days": [1, 2, 3, 4, 5, 6]
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    user = response.json()
    user_id = user["id"]
    print(f"✓ 用户创建成功: {user['username']} (ID: {user_id})")

    print("\n2. 创建训练计划...")
    race_date = date.today() + timedelta(weeks=16)
    plan_data = {
        "user_id": user_id,
        "race_type": "HALF_MARATHON",
        "race_date": str(race_date),
        "target_time": "01:45:00",
        "current_pace": 330,
        "weekly_mileage": 40.0,
        "injury_history": [],
        "available_days": [1, 2, 3, 4, 5, 6]
    }
    response = requests.post(f"{BASE_URL}/plans", json=plan_data)
    plan = response.json()
    plan_id = plan["id"]
    print(f"✓ 训练计划创建成功 (计划ID: {plan_id})")
    print(f"  赛事类型: {plan['race_type']}")
    print(f"  比赛日期: {plan['race_date']}")
    print(f"  计划周期: {plan['total_weeks']} 周")

    print("\n3. 生成训练计划...")
    response = requests.post(f"{BASE_URL}/plans/{plan_id}/generate")
    result = response.json()
    print(f"✓ 训练计划生成成功")
    print(f"  总训练课次: {result['total_workouts']}")
    print(f"  总距离: {result['total_distance']:.1f} km")

    print("\n4. 获取训练计划概览...")
    response = requests.get(f"{BASE_URL}/plans/{plan_id}/overview")
    overview = response.json()
    print(f"✓ 计划概览:")
    print(f"  当前阶段: {overview['current_phase']}")
    print(f"  总距离: {overview['total_distance']:.1f} km")
    print(f"  完成率: {overview['completion_rate']:.1%}")

    print("\n5. 获取下周训练重点...")
    response = requests.get(
        f"{BASE_URL}/workouts/next-week",
        params={"user_id": user_id, "plan_id": plan_id}
    )
    next_week = response.json()
    print(f"✓ 下周训练 (第{next_week['week_number']}周):")
    print(f"  训练重点: {next_week['focus']}")
    print(f"  总距离: {next_week['total_distance']:.1f} km")
    print(f"  训练课次: {len(next_week['workouts'])}")

    print("\n6. 获取完赛预测...")
    response = requests.get(
        f"{BASE_URL}/reports/{user_id}/prediction",
        params={"plan_id": plan_id}
    )
    prediction = response.json()
    print(f"✓ 完赛预测:")
    print(f"  预测时间: {prediction['predicted_time']}")
    print(f"  预测配速: {prediction['predicted_pace']}/km")
    print(f"  置信度: {prediction['confidence']:.0%}")
    print(f"  配速策略: {prediction['pace_strategy']['strategy']}")

    print("\n7. 获取疲劳风险评估...")
    response = requests.get(f"{BASE_URL}/reports/{plan_id}/fatigue")
    fatigue = response.json()
    print(f"✓ 疲劳风险:")
    print(f"  风险等级: {fatigue['risk_level']}")
    print(f"  风险评分: {fatigue['risk_score']}")
    print(f"  建议: {fatigue['recommendation']}")

    print("\n8. 获取用户训练档案...")
    response = requests.get(f"{BASE_URL}/users/{user_id}/profile")
    profile = response.json()
    print(f"✓ 用户档案:")
    print(f"  用户名: {profile['username']}")
    print(f"  当前配速: {profile['current_pace']}秒/km")
    print(f"  周跑量: {profile['weekly_mileage']:.1f} km")
    print(f"  总训练计划: {profile['total_plans']}")
    print(f"  总训练课次: {profile['total_workouts']}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n提示:")
    print("- 查看 API 文档: http://localhost:8000/docs")
    print("- 查看计划详情: GET /api/v1/plans/" + plan_id)
    print("- 查看所有训练: GET /api/v1/workouts/plan/" + plan_id)

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n请确保服务已启动: python -m uvicorn app.main:app --reload")
