import requests
import json
from datetime import date, timedelta
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_new_features():
    print("=" * 70)
    print("RunPlan API 新功能验证测试")
    print("=" * 70)

    print("\n【新功能1】测试按周查看计划接口...")
    timestamp = int(time.time())
    user_data = {
        "username": f"test_runner_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "current_pace": 330,
        "weekly_mileage": 40.0,
        "injury_history": [],
        "available_days": [1, 2, 3, 4, 5, 6]
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    if response.status_code != 201:
        print(f"✗ 用户创建失败: {response.text}")
        return
    user = response.json()
    user_id = user["id"]
    print(f"✓ 用户创建成功: {user_id}")

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
    if response.status_code != 201:
        print(f"✗ 计划创建失败: {response.text}")
        return
    plan = response.json()
    plan_id = plan["id"]
    print(f"✓ 计划创建成功: {plan_id}")

    response = requests.post(f"{BASE_URL}/plans/{plan_id}/generate")
    if response.status_code != 200:
        print(f"✗ 计划生成失败: {response.text}")
        return
    print(f"✓ 计划生成成功")

    ref_date = str(date.today())
    response = requests.get(
        f"{BASE_URL}/workouts/weekly",
        params={"plan_id": plan_id, "reference_date": ref_date}
    )
    if response.status_code == 200:
        weekly_plan = response.json()
        print(f"\n✓ 按周查看计划成功:")
        print(f"  - 当前周次: 第{weekly_plan['current_week']}周")
        print(f"  - 周范围: {weekly_plan['week_range']}")
        print(f"  - 总距离: {weekly_plan['total_distance']}km")
        print(f"  - 训练课次: {weekly_plan['workout_count']}次")
        print(f"  - 完成率: {weekly_plan['completion_rate']}%")
        print(f"  - 每日安排:")
        for day, workouts in weekly_plan['workouts_by_day'].items():
            if workouts:
                workout_info = f"{workouts[0]['workout_type']} ({workouts[0]['distance']}km)"
                print(f"    {day}: {workout_info}")
    else:
        print(f"✗ 按周查看失败: {response.text}")

    print("\n【新功能2】测试训练补录...")
    response = requests.get(f"{BASE_URL}/workouts/plan/{plan_id}")
    workouts = response.json()
    scheduled = [w for w in workouts if w["status"] == "scheduled"]

    if scheduled:
        makeup_workout = scheduled[0]
        makeup_data = {
            "actual_distance": makeup_workout["distance"],
            "actual_duration": makeup_workout["duration"],
            "fatigue_level": 5,
            "notes": "补录测试"
        }
        response = requests.post(
            f"{BASE_URL}/workouts/{makeup_workout['id']}/makeup",
            json=makeup_data
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 训练补录成功:")
            print(f"  - 训练类型: {result['workout_type']}")
            print(f"  - 实际距离: {result['actual_distance']}km")
            print(f"  - 计划统计: 完成{result['plan_stats']['completed_workouts']}/{result['plan_stats']['total_workouts']}次")
        else:
            print(f"✗ 训练补录失败: {response.text}")

    print("\n【新功能3】测试训练撤回...")
    response = requests.get(f"{BASE_URL}/workouts/plan/{plan_id}")
    workouts = response.json()
    completed = [w for w in workouts if w["status"] == "completed"]

    if completed:
        undo_workout = completed[0]
        response = requests.post(
            f"{BASE_URL}/workouts/{undo_workout['id']}/undo",
            json={"reason": "测试撤回"}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 训练撤回成功:")
            print(f"  - 训练类型: {result['workout_type']}")
            print(f"  - 计划统计: 完成{result['plan_stats']['completed_workouts']}/{result['plan_stats']['total_workouts']}次")
        else:
            print(f"✗ 训练撤回失败: {response.text}")

    print("\n【新功能4】测试疲劳分析深化（两周负荷走势）...")
    response = requests.get(f"{BASE_URL}/workouts/plan/{plan_id}")
    workouts = response.json()
    scheduled = [w for w in workouts if w["status"] == "scheduled"]

    for i, w in enumerate(scheduled[:5]):
        complete_data = {
            "actual_distance": w["distance"],
            "actual_duration": w["duration"],
            "fatigue_level": 5 + (i % 3)
        }
        requests.post(f"{BASE_URL}/workouts/{w['id']}/complete", json=complete_data)

    response = requests.get(f"{BASE_URL}/reports/{plan_id}/fatigue")
    if response.status_code == 200:
        fatigue = response.json()
        print(f"✓ 疲劳分析深化成功:")
        print(f"  - 当前风险等级: {fatigue['risk_level']}")
        print(f"  - 风险评分: {fatigue['risk_score']}")

        if 'two_week_trend' in fatigue:
            trend = fatigue['two_week_trend']
            print(f"\n  两周负荷走势:")
            print(f"  第1周: 距离{trend['week1']['total_distance']}km, 高强度{trend['week1']['high_intensity_count']}次, 平均疲劳{trend['week1']['avg_fatigue']}")
            print(f"  第2周: 距离{trend['week2']['total_distance']}km, 高强度{trend['week2']['high_intensity_count']}次, 平均疲劳{trend['week2']['avg_fatigue']}")
            print(f"  走势: {trend['trends']['description']}")
    else:
        print(f"✗ 疲劳分析失败: {response.text}")

    print("\n【新功能5】测试改期优化（自动顺开冲突）...")
    response = requests.get(f"{BASE_URL}/workouts/plan/{plan_id}")
    workouts = response.json()
    scheduled = [w for w in workouts if w["status"] == "scheduled"]

    if len(scheduled) >= 2:
        target_workout = scheduled[0]
        conflict_workout = scheduled[1]

        original_date = date.fromisoformat(target_workout["date"])
        conflict_date = date.fromisoformat(conflict_workout["date"])
        target_date = conflict_date

        print(f"  目标训练原日期: {original_date}")
        print(f"  目标日期已有训练: {conflict_workout['workout_type']}")

        reschedule_data = {
            "missed_workout_id": target_workout["id"],
            "target_date": str(target_date)
        }
        response = requests.put(
            f"{BASE_URL}/plans/{plan_id}/reschedule",
            json=reschedule_data
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 改期成功（自动顺开冲突）:")
            print(f"  - 训练类型: {result['rescheduled_workout']['workout_type']}")
            print(f"  - 新日期: {result['rescheduled_workout']['new_date']}")
            print(f"  - 新周次: 第{result['rescheduled_workout']['week_number']}周")
            print(f"  - 受影响训练数: {result['affected_workouts_count']}")

            if result.get('affected_workouts'):
                print(f"  受影响训练:")
                for aw in result['affected_workouts'][:3]:
                    print(f"    - {aw['workout_type']}: {aw['original_date']} → {aw['new_date']}")

            print(f"  - 总课次: {result['total_workouts']}")
            print(f"  - 无日期冲突: {result['date_order_valid']}")

            print(f"\n  验证课表完整性...")
            response = requests.get(f"{BASE_URL}/workouts/plan/{plan_id}")
            final_workouts = response.json()

            dates = [w["date"] for w in final_workouts]
            if len(dates) == len(set(dates)):
                print(f"  ✓ 无日期冲突")
            else:
                print(f"  ✗ 存在日期冲突")

            sorted_workouts = sorted(final_workouts, key=lambda x: x["date"])
            dates_sorted = [w["date"] for w in sorted_workouts]
            if dates_sorted == sorted(dates_sorted):
                print(f"  ✓ 日期顺序正确")
            else:
                print(f"  ✗ 日期顺序错误")

            if len(final_workouts) == len(workouts):
                print(f"  ✓ 课次总数保持不变: {len(final_workouts)}")
            else:
                print(f"  ✗ 课次总数变化: {len(workouts)} → {len(final_workouts)}")
        else:
            print(f"✗ 改期失败: {response.text}")
    else:
        print("✗ 无足够训练测试改期")

    print("\n" + "=" * 70)
    print("新功能测试完成！")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_new_features()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
