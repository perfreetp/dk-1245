from typing import List, Dict, Optional
from datetime import date, timedelta
from app.utils.training_types import WORKOUT_TYPES, RACE_TYPES, TRAINING_PHASES
from app.utils.constants import GEAR_TIPS, NUTRITION_TIPS
from app.services.pace_calculator import PaceCalculator


class PlanGenerator:
    def __init__(self, race_type: str, race_date: date, current_pace: float,
                 weekly_mileage: float, available_days: List[int],
                 injury_history: List[str] = None):
        self.race_type = race_type
        self.race_date = race_date
        self.current_pace = current_pace
        self.weekly_mileage = weekly_mileage
        self.available_days = available_days if available_days else [1, 2, 3, 4, 5, 6]
        self.injury_history = injury_history or []
        self.race_config = RACE_TYPES.get(race_type, RACE_TYPES["HALF_MARATHON"])
        self.total_weeks = self.race_config["base_weeks"]

    def generate_plan(self) -> Dict:
        """生成完整的训练计划"""
        start_date = self.race_date - timedelta(weeks=self.total_weeks)
        if start_date < date.today():
            start_date = date.today()

        plan_structure = self._define_plan_structure()
        workouts = self._generate_workouts(start_date, plan_structure)

        return {
            "start_date": start_date,
            "total_weeks": self.total_weeks,
            "workouts": workouts,
            "race_type": self.race_type,
            "race_date": self.race_date,
            "total_distance": sum(w["distance"] for w in workouts),
            "message": f"训练计划已生成，共{self.total_weeks}周"
        }

    def _define_plan_structure(self) -> Dict:
        """定义计划结构"""
        phase_distribution = {
            "base": {"start": 1, "end": int(self.total_weeks * 0.4)},
            "build": {"start": int(self.total_weeks * 0.4) + 1, "end": int(self.total_weeks * 0.7)},
            "peak": {"start": int(self.total_weeks * 0.7) + 1, "end": int(self.total_weeks * 0.85)},
            "taper": {"start": int(self.total_weeks * 0.85) + 1, "end": self.total_weeks}
        }

        return phase_distribution

    def _generate_workouts(self, start_date: date, plan_structure: Dict) -> List[Dict]:
        """生成所有训练课次"""
        workouts = []
        current_date = start_date

        for week in range(1, self.total_weeks + 1):
            week_workouts = self._generate_week_workouts(week, current_date, plan_structure)
            workouts.extend(week_workouts)
            current_date += timedelta(days=7)

        return workouts

    def _generate_week_workouts(self, week_num: int, week_start: date, plan_structure: Dict) -> List[Dict]:
        """生成单周训练"""
        phase = self._get_current_phase(week_num, plan_structure)
        phase_config = TRAINING_PHASES[phase]

        weekly_distance = self._calculate_weekly_distance(week_num, phase)
        days_to_train = sorted(self.available_days)

        if phase == "taper":
            weekly_distance *= 0.6

        workouts = []
        distance_per_day = weekly_distance / len(days_to_train) if days_to_train else 0

        for day_idx, day_num in enumerate(days_to_train):
            workout_date = week_start + timedelta(days=day_num)
            if day_num == 6 and len(days_to_train) > 0:
                workout = self._create_long_run(workout_date, week_num, day_idx, weekly_distance * 0.4, phase)
                workouts.append(workout)

                if len(days_to_train) == 7 and phase in ["peak", "build", "taper"]:
                    stretch_date = week_start + timedelta(days=0)
                    stretch_workout = self._create_stretch_workout(stretch_date, week_num, 0)
                    workouts.append(stretch_workout)
                elif phase in ["base", "build"] and 0 not in days_to_train:
                    stretch_date = workout_date + timedelta(days=1)
                    stretch_workout = self._create_stretch_workout(stretch_date, week_num, day_idx + 1)
                    workouts.append(stretch_workout)

            elif day_num in [1, 3]:
                if phase == "build" and day_num == 1:
                    workout = self._create_interval_workout(workout_date, week_num, day_idx, distance_per_day * 0.8, phase)
                else:
                    workout = self._create_easy_run(workout_date, week_num, day_idx, distance_per_day * 0.7, phase)
                workouts.append(workout)

            elif day_num == 4:
                workout = self._create_tempo_workout(workout_date, week_num, day_idx, distance_per_day * 0.9, phase)
                workouts.append(workout)

            elif day_num == 2:
                workout = self._create_easy_run(workout_date, week_num, day_idx, distance_per_day * 0.6, phase)
                workouts.append(workout)

            elif day_num == 5:
                if phase == "peak" and week_num % 2 == 0:
                    test_distance = distance_per_day * 0.8
                    workout = self._create_test_run(workout_date, week_num, day_idx, test_distance, phase)
                else:
                    workout = self._create_easy_run(workout_date, week_num, day_idx, distance_per_day * 0.5, phase)
                workouts.append(workout)

            else:
                workout = self._create_easy_run(workout_date, week_num, day_idx, distance_per_day * 0.6, phase)
                workouts.append(workout)

        if phase in ["base", "build"]:
            if 5 in days_to_train:
                strength_date = week_start + timedelta(days=5)
                strength_workout = self._create_strength_workout(strength_date, week_num, 5)
                workouts.append(strength_workout)
            elif 6 in days_to_train:
                strength_date = week_start + timedelta(days=6)
                strength_workout = self._create_strength_workout(strength_date, week_num, 6)
                workouts.append(strength_workout)

        if 2 not in days_to_train and 5 not in days_to_train:
            rest_day = 2 if 2 not in days_to_train else 5
            rest_date = week_start + timedelta(days=rest_day)
            workouts.append(self._create_rest_day(rest_date, week_num, rest_day))

        return workouts

    def _get_current_phase(self, week_num: int, plan_structure: Dict) -> str:
        """确定当前处于哪个阶段"""
        for phase, config in plan_structure.items():
            if config["start"] <= week_num <= config["end"]:
                return phase
        return "taper"

    def _calculate_weekly_distance(self, week_num: int, phase: str) -> float:
        """计算周跑量"""
        if phase == "base":
            progress = (week_num - 1) / (self.total_weeks * 0.4)
            base_distance = self.weekly_mileage * (1 + progress * 0.3)
        elif phase == "build":
            progress = (week_num - int(self.total_weeks * 0.4)) / (self.total_weeks * 0.3)
            base_distance = self.weekly_mileage * 1.3 * (1 + progress * 0.2)
        elif phase == "peak":
            base_distance = self.weekly_mileage * 1.5
        else:
            base_distance = self.weekly_mileage * 1.2

        return min(base_distance, self.weekly_mileage * 1.8)

    def _create_easy_run(self, workout_date: date, week: int, day: int, distance: float, phase: str) -> Dict:
        """创建轻松跑"""
        target_pace = self.current_pace * 1.15
        return {
            "date": workout_date,
            "week_number": week,
            "day_number": day,
            "workout_type": "EASY_RUN",
            "distance": round(distance, 1),
            "duration": int(distance * (target_pace / 60)),
            "target_pace": PaceCalculator.seconds_to_pace(target_pace),
            "pace_zones": self._get_pace_zones(target_pace),
            "description": f"轻松跑，保持在有氧区间，配速 {PaceCalculator.seconds_to_pace(target_pace)}/km",
            "gear_reminder": GEAR_TIPS["EASY_RUN"],
            "nutrition_tip": NUTRITION_TIPS["EASY_RUN"]
        }

    def _create_interval_workout(self, workout_date: date, week: int, day: int, distance: float, phase: str) -> Dict:
        """创建间歇跑"""
        if phase in ["base", "taper"]:
            workout_type = "EASY_RUN"
            target_pace = self.current_pace * 1.1
            description = f"轻松跑代替间歇，注意节奏控制"
        else:
            workout_type = "INTERVAL"
            target_pace = self.current_pace * 0.95
            intervals = self._get_interval_config(week, phase)
            description = f"{intervals['reps']}x{intervals['distance']}m间歇，间歇{int(intervals['rest_distance'])}m走路"

        return {
            "date": workout_date,
            "week_number": week,
            "day_number": day,
            "workout_type": workout_type,
            "distance": round(distance, 1),
            "duration": int(distance * (target_pace / 60)),
            "target_pace": PaceCalculator.seconds_to_pace(target_pace),
            "pace_zones": self._get_pace_zones(target_pace),
            "description": description,
            "gear_reminder": GEAR_TIPS["INTERVAL"],
            "nutrition_tip": NUTRITION_TIPS["INTERVAL"]
        }

    def _create_tempo_workout(self, workout_date: date, week: int, day: int, distance: float, phase: str) -> Dict:
        """创建节奏跑"""
        if phase == "base":
            workout_type = "EASY_RUN"
            target_pace = self.current_pace * 1.05
            description = "渐进跑，从慢到快"
        else:
            workout_type = "TEMPO_RUN"
            target_pace = self.current_pace * 0.9
            description = f"节奏跑，目标配速 {PaceCalculator.seconds_to_pace(target_pace)}/km"

        return {
            "date": workout_date,
            "week_number": week,
            "day_number": day,
            "workout_type": workout_type,
            "distance": round(distance, 1),
            "duration": int(distance * (target_pace / 60)),
            "target_pace": PaceCalculator.seconds_to_pace(target_pace),
            "pace_zones": self._get_pace_zones(target_pace),
            "description": description,
            "gear_reminder": GEAR_TIPS["TEMPO_RUN"],
            "nutrition_tip": NUTRITION_TIPS["TEMPO_RUN"]
        }

    def _create_long_run(self, workout_date: date, week: int, day: int, distance: float, phase: str) -> Dict:
        """创建长距离跑"""
        if phase == "taper":
            distance = distance * 0.5
        elif phase == "peak" and week == int(self.total_weeks * 0.85):
            distance = self.race_config["distance"]

        target_pace = self.current_pace * 1.1
        return {
            "date": workout_date,
            "week_number": week,
            "day_number": day,
            "workout_type": "LONG_RUN",
            "distance": round(distance, 1),
            "duration": int(distance * (target_pace / 60)),
            "target_pace": PaceCalculator.seconds_to_pace(target_pace),
            "pace_zones": self._get_pace_zones(target_pace),
            "description": f"长距离跑 {distance:.1f}km，保持稳定配速",
            "gear_reminder": GEAR_TIPS["LONG_RUN"],
            "nutrition_tip": NUTRITION_TIPS["LONG_RUN"]
        }

    def _create_rest_day(self, workout_date: date, week: int, day: int) -> Dict:
        """创建休息日"""
        return {
            "date": workout_date,
            "week_number": week,
            "day_number": day,
            "workout_type": "REST",
            "distance": 0.0,
            "duration": 0,
            "target_pace": None,
            "pace_zones": [],
            "description": "休息日，充分恢复",
            "gear_reminder": None,
            "nutrition_tip": "注意补充蛋白质和碳水化合物"
        }

    def _create_strength_workout(self, workout_date: date, week: int, day: int) -> Dict:
        """创建力量训练"""
        return {
            "date": workout_date,
            "week_number": week,
            "day_number": day,
            "workout_type": "STRENGTH",
            "distance": 0.0,
            "duration": 30,
            "target_pace": None,
            "pace_zones": [],
            "description": "核心力量和下肢力量训练，包括深蹲、弓步、平板支撑等",
            "gear_reminder": "穿着舒适运动服，准备瑜伽垫和哑铃（如有）",
            "nutrition_tip": "训练后补充蛋白质促进肌肉恢复"
        }

    def _create_stretch_workout(self, workout_date: date, week: int, day: int) -> Dict:
        """创建拉伸恢复"""
        return {
            "date": workout_date,
            "week_number": week,
            "day_number": day,
            "workout_type": "STRETCH",
            "distance": 0.0,
            "duration": 20,
            "target_pace": None,
            "pace_zones": [],
            "description": "跑后拉伸，重点拉伸腿部肌肉、髋关节和足踝",
            "gear_reminder": "准备瑜伽垫，可以配合泡沫轴使用",
            "nutrition_tip": "拉伸后补充水分和电解质"
        }

    def _create_test_run(self, workout_date: date, week: int, day: int, distance: float, phase: str) -> Dict:
        """创建测试跑"""
        if phase == "peak":
            target_pace = self.current_pace * 0.95
            description = f"赛前测试跑 {distance:.1f}km，模拟比赛配速"
        else:
            target_pace = self.current_pace * 1.0
            description = f"能力测试 {distance:.1f}km，评估当前跑步能力"

        return {
            "date": workout_date,
            "week_number": week,
            "day_number": day,
            "workout_type": "TEST_RUN",
            "distance": round(distance, 1),
            "duration": int(distance * (target_pace / 60)),
            "target_pace": PaceCalculator.seconds_to_pace(target_pace),
            "pace_zones": self._get_pace_zones(target_pace),
            "description": description,
            "gear_reminder": GEAR_TIPS["TEST_RUN"],
            "nutrition_tip": NUTRITION_TIPS["TEST_RUN"]
        }

    def _get_interval_config(self, week: int, phase: str) -> Dict:
        """获取间歇跑配置"""
        if phase == "build":
            return {"reps": 6, "distance": 1000, "rest_distance": 400}
        else:
            return {"reps": 8, "distance": 800, "rest_distance": 400}

    def _get_pace_zones(self, target_pace: float) -> List[Dict]:
        """获取配速区间"""
        zones = PaceCalculator.calculate_pace_zones(target_pace)
        return [
            {"zone": key, "name": value["name"], "min_pace": value["min_pace"], "max_pace": value["max_pace"]}
            for key, value in zones.items()
        ]
