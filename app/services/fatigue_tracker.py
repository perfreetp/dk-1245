from typing import List, Dict, Optional
from datetime import date, timedelta


class FatigueTracker:
    @staticmethod
    def calculate_fatigue_risk(
        recent_workouts: List[Dict],
        weekly_mileage_increase: float = 0.0,
        injury_history: List[str] = None
    ) -> Dict:
        """
        计算疲劳风险等级
        recent_workouts: 最近训练记录列表
        返回: 风险等级和建议
        """
        if injury_history is None:
            injury_history = []

        risk_score = 0
        risk_factors = []

        consecutive_hard_days = 0
        max_consecutive_hard = 0
        for workout in recent_workouts[-7:]:
            if workout.get("intensity", 0) >= 4:
                consecutive_hard_days += 1
                max_consecutive_hard = max(max_consecutive_hard, consecutive_hard_days)
            else:
                consecutive_hard_days = 0

        if max_consecutive_hard >= 3:
            risk_score += 3
            risk_factors.append(f"连续{max_consecutive_hard}天高强度训练")

        if weekly_mileage_increase > 15:
            risk_score += 2
            risk_factors.append(f"周跑量增长{weekly_mileage_increase:.1f}%")

        avg_fatigue = sum(w.get("fatigue_level", 0) for w in recent_workouts[-7:]) / min(len(recent_workouts[-7:]), 1)
        if avg_fatigue >= 7:
            risk_score += 2
            risk_factors.append(f"近期平均疲劳等级{avg_fatigue:.1f}偏高")

        if any("膝盖" in injury for injury in injury_history):
            risk_score += 1
            risk_factors.append("有膝盖伤病史")

        if any("跟腱" in injury for injury in injury_history):
            risk_score += 2
            risk_factors.append("有跟腱伤病史")

        risk_level = "low"
        recommendation = "训练状态良好，可以继续当前计划"
        if risk_score >= 5:
            risk_level = "high"
            recommendation = "疲劳风险较高，建议减少训练强度，增加恢复时间"
        elif risk_score >= 3:
            risk_level = "medium"
            recommendation = "注意监测身体状态，适当降低训练强度"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendation": recommendation
        }

    @staticmethod
    def analyze_fatigue_trend(workouts: List[Dict]) -> List[int]:
        """
        分析疲劳趋势
        返回: 疲劳等级列表
        """
        return [w.get("fatigue_level", 0) for w in workouts if w.get("fatigue_level")]

    @staticmethod
    def suggest_adjustment(fatigue_risk: Dict, current_week_distance: float) -> Dict:
        """
        根据疲劳风险建议调整
        """
        if fatigue_risk["risk_level"] == "high":
            return {
                "adjust_distance": True,
                "distance_reduction": 0.3,
                "message": "建议减少30%跑量，增加恢复训练"
            }
        elif fatigue_risk["risk_level"] == "medium":
            return {
                "adjust_distance": True,
                "distance_reduction": 0.15,
                "message": "建议减少15%跑量"
            }
        else:
            return {
                "adjust_distance": False,
                "distance_reduction": 0,
                "message": "保持当前训练计划"
            }
