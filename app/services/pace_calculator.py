from typing import Dict, List
from app.utils.constants import PACE_ZONES


class PaceCalculator:
    @staticmethod
    def seconds_to_pace(seconds: float) -> str:
        """将秒数转换为 MM:SS 格式的配速"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def pace_to_seconds(pace: str) -> float:
        """将 MM:SS 格式的配速转换为秒数"""
        try:
            parts = pace.split(":")
            minutes = int(parts[0])
            seconds = int(parts[1])
            return minutes * 60 + seconds
        except:
            return 0.0

    @staticmethod
    def calculate_vdot(pace_5k: float) -> float:
        """
        根据5K配速估算VDOT值
        使用 Jack Daniels 公式简化版
        pace_5k: 秒/公里
        """
        if pace_5k <= 0:
            return 0.0
        vdot = (132.77 - 0.075 * pace_5k) if pace_5k > 180 else 70.0
        return max(30.0, min(85.0, vdot))

    @staticmethod
    def calculate_pace_zones(current_pace: float) -> Dict[str, Dict]:
        """
        根据当前配速计算各区间配速
        current_pace: 秒/公里
        """
        zones = {}
        for zone_key, zone_info in PACE_ZONES.items():
            min_pace = current_pace / zone_info["max_pct"]
            max_pace = current_pace / zone_info["min_pct"]
            zones[zone_key] = {
                "name": zone_info["name"],
                "min_pace": PaceCalculator.seconds_to_pace(min_pace),
                "max_pace": PaceCalculator.seconds_to_pace(max_pace),
                "description": zone_info["description"]
            }
        return zones

    @staticmethod
    def calculate_target_pace(target_time: str, distance: float) -> float:
        """
        根据目标时间和距离计算目标配速
        target_time: HH:MM:SS 格式
        distance: 公里
        返回: 秒/公里
        """
        try:
            parts = target_time.split(":")
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            total_seconds = hours * 3600 + minutes * 60 + seconds
            return total_seconds / distance
        except:
            return 0.0

    @staticmethod
    def estimate_race_pace(vdot: float, distance_km: float) -> float:
        """
        根据VDOT值估算比赛配速
        返回: 秒/公里
        """
        if distance_km <= 0 or vdot <= 0:
            return 0.0
        race_factor = {
            5.0: 1.0,
            10.0: 1.03,
            21.0975: 1.06,
            42.195: 1.12
        }
        factor = race_factor.get(distance_km, 1.0 + (distance_km - 5) * 0.01)
        return (132.77 - 0.075 * (132.77 - vdot * 0.75)) * factor * 60
