import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

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

try:
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        user = response.json()
        user_id = user["id"]
        print(f"✓ 用户创建成功: {user['username']} (ID: {user_id})")

        print("\n2. 创建训练计划...")
        from datetime import date, timedelta
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
        print(f"状态码: {response.status_code}")
        if response.status_code == 201:
            plan = response.json()
            plan_id = plan["id"]
            print(f"✓ 训练计划创建成功 (计划ID: {plan_id})")

            print("\n3. 生成训练计划...")
            response = requests.post(f"{BASE_URL}/plans/{plan_id}/generate")
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✓ 训练计划生成成功")
                print(f"  总训练课次: {result['total_workouts']}")
                print(f"  总距离: {result['total_distance']:.1f} km")

                print("\n4. 获取下周训练重点...")
                response = requests.get(
                    f"{BASE_URL}/workouts/next-week",
                    params={"user_id": user_id, "plan_id": plan_id}
                )
                if response.status_code == 200:
                    next_week = response.json()
                    print(f"✓ 下周训练 (第{next_week['week_number']}周):")
                    print(f"  训练重点: {next_week['focus']}")
                    print(f"  总距离: {next_week['total_distance']:.1f} km")

                print("\n5. 获取完赛预测...")
                response = requests.get(
                    f"{BASE_URL}/reports/{user_id}/prediction",
                    params={"plan_id": plan_id}
                )
                if response.status_code == 200:
                    prediction = response.json()
                    print(f"✓ 完赛预测:")
                    print(f"  预测时间: {prediction['predicted_time']}")
                    print(f"  预测配速: {prediction['predicted_pace']}/km")
                    print(f"  置信度: {prediction['confidence']:.0%}")

                print("\n" + "=" * 60)
                print("测试完成！")
                print("=" * 60)
            else:
                print(f"错误: {response.text}")
        else:
            print(f"错误: {response.text}")
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"错误: {e}")
    print("\n请确保服务已启动: python -m uvicorn app.main:app --reload")
