from typing import List, Dict, Optional
from datetime import date, timedelta


class FatigueTracker:
    @staticmethod
    def calculate_fatigue_risk(
        recent_workouts: List[Dict],
        weekly_mileage_increase: float = 0.0,
        injury_history: List[str] = None,
        current_week_distance: float = 0.0
    ) -> Dict:
        """
        计算疲劳风险等级
        recent_workouts: 最近训练记录列表（包含 intensity, distance, fatigue_level 等）
        返回: 风险等级和建议
        """
        if injury_history is None:
            injury_history = []

        risk_score = 0
        risk_factors = []

        recent_7_days = recent_workouts[-7:] if len(recent_workouts) >= 7 else recent_workouts

        hard_workouts = [w for w in recent_7_days if w.get("intensity", 0) >= 4]
        if len(hard_workouts) >= 3:
            risk_score += 3
            risk_factors.append(f"本周已完成{len(hard_workouts)}次高强度训练")

        total_distance = sum(w.get("distance", 0) for w in recent_7_days)
        if total_distance > 60:
            risk_score += 2
            risk_factors.append(f"近7天总跑量{total_distance:.1f}km较大")

        if weekly_mileage_increase > 20:
            risk_score += 2
            risk_factors.append(f"周跑量增长{weekly_mileage_increase:.1f}%")

        fatigue_levels = [w.get("fatigue_level", 0) for w in recent_7_days if w.get("fatigue_level")]
        if fatigue_levels:
            avg_fatigue = sum(fatigue_levels) / len(fatigue_levels)
            if avg_fatigue >= 7:
                risk_score += 3
                risk_factors.append(f"近期平均疲劳等级{avg_fatigue:.1f}，偏高")
            elif avg_fatigue >= 5:
                risk_score += 1
                risk_factors.append(f"近期平均疲劳等级{avg_fatigue:.1f}，中等")

        if any("膝盖" in injury for injury in injury_history):
            risk_score += 1
            risk_factors.append("有膝盖伤病史，需要特别关注")

        if any("跟腱" in injury for injury in injury_history):
            risk_score += 2
            risk_factors.append("有跟腱伤病史，需要特别注意")

        if current_week_distance > 0 and current_week_distance < 20:
            if risk_score > 0:
                risk_score = max(0, risk_score - 1)
                risk_factors.append("本周训练量较小，风险降低")

        risk_level = "low"
        recommendation = "训练状态良好，可以继续当前计划"

        if risk_score >= 5:
            risk_level = "high"
            recommendation = "疲劳风险较高，建议减少训练强度，增加恢复时间，充分休息"
        elif risk_score >= 3:
            risk_level = "medium"
            recommendation = "注意监测身体状态，适当降低训练强度，保持充足睡眠"
        elif risk_score > 0:
            risk_level = "low"
            recommendation = "存在轻微疲劳信号，注意休息和恢复"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors if risk_factors else ["训练负荷正常"],
            "recommendation": recommendation,
            "recent_stats": {
                "total_workouts": len(recent_7_days),
                "hard_workouts": len(hard_workouts),
                "total_distance": round(total_distance, 1),
                "avg_fatigue": round(avg_fatigue, 1) if fatigue_levels else None
            }
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
                "message": "建议减少30%跑量，增加恢复训练，充分休息"
            }
        elif fatigue_risk["risk_level"] == "medium":
            return {
                "adjust_distance": True,
                "distance_reduction": 0.15,
                "message": "建议减少15%跑量，注意休息"
            }
        else:
            return {
                "adjust_distance": False,
                "distance_reduction": 0,
                "message": "保持当前训练计划"
            }
