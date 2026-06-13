from typing import Dict, Optional
from app.services.pace_calculator import PaceCalculator


class PredictionService:
    @staticmethod
    def predict_finish_time(
        race_type: str,
        current_pace: float,
        target_time: Optional[str] = None,
        training_completion_rate: float = 1.0
    ) -> Dict:
        """
        预测完赛时间
        current_pace: 秒/公里
        training_completion_rate: 训练完成率 (0-1)
        """
        race_distances = {
            "5K": 5.0,
            "HALF_MARATHON": 21.0975,
            "MARATHON": 42.195
        }

        distance = race_distances.get(race_type, 0)
        if distance == 0:
            return {"error": "Invalid race type"}

        if target_time:
            base_pace = PaceCalculator.calculate_target_pace(target_time, distance)
        else:
            vdot = PaceCalculator.calculate_vdot(current_pace * 5)
            base_pace = PaceCalculator.estimate_race_pace(vdot, distance)

        adjustment_factor = 1.0 - (1.0 - training_completion_rate) * 0.1
        adjusted_pace = base_pace * adjustment_factor

        total_seconds = adjusted_pace * distance
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        predicted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        confidence = min(0.95, 0.6 + training_completion_rate * 0.3)

        return {
            "predicted_time": predicted_time,
            "predicted_pace": PaceCalculator.seconds_to_pace(adjusted_pace),
            "confidence": round(confidence, 2)
        }

    @staticmethod
    def generate_pace_strategy(race_type: str, predicted_time: str, distance: float) -> Dict:
        """
        生成配速策略
        """
        total_seconds = sum(int(x) * 60 ** (2 - i) for i, x in enumerate(predicted_time.split(":")))
        avg_pace = total_seconds / distance

        half_distance = distance / 2
        first_half_pace = avg_pace * 0.98
        second_half_pace = avg_pace * 1.02

        return {
            "average_pace": PaceCalculator.seconds_to_pace(avg_pace),
            "first_half_pace": PaceCalculator.seconds_to_pace(first_half_pace),
            "second_half_pace": PaceCalculator.seconds_to_pace(second_half_pace),
            "strategy": "建议前半程略快于目标配速，为后半程留有余地" if race_type != "5K" else "5K建议全程保持稳定配速"
        }

    @staticmethod
    def assess_risk(predicted_time: str, target_time: Optional[str] = None) -> Dict:
        """
        评估完赛风险
        """
        if not target_time:
            return {
                "risk": "medium",
                "message": "建议设定明确目标以便更好地评估风险"
            }

        predicted_seconds = sum(int(x) * 60 ** (2 - i) for i, x in enumerate(predicted_time.split(":")))
        target_seconds = sum(int(x) * 60 ** (2 - i) for i, x in enumerate(target_time.split(":")))

        difference = (predicted_seconds - target_seconds) / target_seconds

        if difference <= -0.05:
            return {
                "risk": "low",
                "message": "目标可达成，注意比赛策略和补给"
            }
        elif difference <= 0.05:
            return {
                "risk": "medium",
                "message": "目标有一定挑战性，需要良好执行"
            }
        else:
            return {
                "risk": "high",
                "message": "目标较激进，建议调整预期或加强训练"
            }
