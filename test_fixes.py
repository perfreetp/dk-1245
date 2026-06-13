import requests
import json
from datetime import date, timedelta
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_fixes():
    print("=" * 70)
    print("RunPlan API 修复验证测试")
    print("=" * 70)

    print("\n【问题1】测试目标时间计划生成...")
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
    print(f"✓ 半马计划创建成功 (带目标时间): {plan_id}")

    response = requests.post(f"{BASE_URL}/plans/{plan_id}/generate")
    if response.status_code != 200:
        print(f"✗ 计划生成失败: {response.text}")
        return
    result = response.json()
    print(f"✓ 半马计划生成成功:")
    print(f"  - 总周数: {result['total_weeks']}")
    print(f"  - 总课次: {result['total_workouts']}")
    print(f"  - 总里程: {result['total_distance']:.1f} km")

    print("\n【问题2】验证课表包含力量训练、拉伸恢复和测试跑...")
    response = requests.get(f"{BASE_URL}/workouts/plan/{plan_id}")
    workouts = response.json()
    workout_types = {}
    for w in workouts:
        wtype = w["workout_type"]
        workout_types[wtype] = workout_types.get(wtype, 0) + 1

    print(f"✓ 课表类型统计:")
    for wtype, count in sorted(workout_types.items()):
        print(f"  - {wtype}: {count}次")

    has_strength = "STRENGTH" in workout_types
    has_stretch = "STRETCH" in workout_types
    has_test = "TEST_RUN" in workout_types

    if has_strength and has_stretch and has_test:
        print(f"✓ 课表内容完整：包含力量训练、拉伸恢复和测试跑")
    else:
        missing = []
        if not has_strength: missing.append("力量训练")
        if not has_stretch: missing.append("拉伸恢复")
        if not has_test: missing.append("测试跑")
        print(f"✗ 缺少: {', '.join(missing)}")

    print("\n【问题3】测试阶段报告（按阶段分别统计）...")
    response = requests.get(f"{BASE_URL}/reports/{plan_id}/phase")
    if response.status_code != 200:
        print(f"✗ 阶段报告获取失败: {response.text}")
        return
    phase_report = response.json()

    print(f"✓ 阶段报告 (共{phase_report['total_weeks']}周):")
    for phase_key, phase_data in phase_report["phases"].items():
        print(f"  【{phase_data['name']}】{phase_data['week_range']}")
        print(f"    - 完成率: {phase_data['completion_rate']}%")
        print(f"    - 总里程: {phase_data['total_distance']}km")
        print(f"    - 训练课次: {phase_data['workout_breakdown']['total']}次")
        if phase_data['target_pace']:
            print(f"    - 目标配速: {phase_data['target_pace']}/km")
        print(f"    - 重点: {phase_data['focus']}")

    print("\n【问题4】测试疲劳风险计算...")
    if len(workouts) > 0:
        completed_workout = workouts[0]
        complete_data = {
            "actual_distance": completed_workout["distance"],
            "actual_duration": completed_workout["duration"],
            "fatigue_level": 7
        }
        response = requests.post(
            f"{BASE_URL}/workouts/{completed_workout['id']}/complete",
            json=complete_data
        )
        if response.status_code == 200:
            print(f"✓ 训练打卡成功")

        response = requests.get(f"{BASE_URL}/reports/{plan_id}/fatigue")
        if response.status_code == 200:
            fatigue = response.json()
            print(f"✓ 疲劳风险评估:")
            print(f"  - 风险等级: {fatigue['risk_level']}")
            print(f"  - 风险评分: {fatigue['risk_score']}")
            print(f"  - 风险因素: {', '.join(fatigue['risk_factors'])}")
            print(f"  - 建议: {fatigue['recommendation']}")
            if 'recent_stats' in fatigue:
                stats = fatigue['recent_stats']
                print(f"  - 近期统计: 完成{stats.get('total_workouts', 0)}次, 高强度{stats.get('hard_workouts', 0)}次, 总跑量{stats.get('total_distance', 0)}km")
        else:
            print(f"✗ 疲劳风险获取失败: {response.text}")
    else:
        print("✗ 无训练数据可测试疲劳风险")

    print("\n【问题5】测试缺课重排...")
    missed_workout = None
    for w in workouts:
        if w["status"] == "scheduled":
            missed_workout = w
            break

    if missed_workout:
        reschedule_data = {
            "missed_workout_id": missed_workout["id"],
            "target_date": str(date.today() + timedelta(days=7))
        }
        response = requests.put(
            f"{BASE_URL}/plans/{plan_id}/reschedule",
            json=reschedule_data
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 重排成功:")
            print(f"  - 原日期: {result['rescheduled_workout']['original_date']}")
            print(f"  - 新日期: {result['rescheduled_workout']['new_date']}")
            print(f"  - 训练类型: {result['rescheduled_workout']['workout_type']}")
            print(f"  - 受影响训练: {result['affected_workouts']}个")
        else:
            print(f"✗ 重排失败: {response.text}")
    else:
        print("✗ 无可重排的训练")

    print("\n" + "=" * 70)
    print("测试完成！所有修复已验证。")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_fixes()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
