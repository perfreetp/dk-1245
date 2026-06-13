WORKOUT_TYPES = {
    "EASY_RUN": {
        "name": "轻松跑",
        "name_en": "Easy Run",
        "intensity": 1,
        "description": "低强度有氧跑，恢复为主"
    },
    "INTERVAL": {
        "name": "间歇跑",
        "name_en": "Interval Training",
        "intensity": 5,
        "description": "高强度间歇训练，提升速度"
    },
    "TEMPO_RUN": {
        "name": "节奏跑",
        "name_en": "Tempo Run",
        "intensity": 4,
        "description": "中等强度，维持马拉松配速"
    },
    "LONG_RUN": {
        "name": "长距离跑",
        "name_en": "Long Run",
        "intensity": 3,
        "description": "长时间持续跑，提升耐力"
    },
    "RECOVERY_RUN": {
        "name": "恢复跑",
        "name_en": "Recovery Run",
        "intensity": 1,
        "description": "极慢配速，促进恢复"
    },
    "STRENGTH": {
        "name": "力量训练",
        "name_en": "Strength Training",
        "intensity": 2,
        "description": "核心力量和下肢力量"
    },
    "STRETCH": {
        "name": "拉伸恢复",
        "name_en": "Stretch & Recovery",
        "intensity": 0,
        "description": "拉伸和筋膜放松"
    },
    "TEST_RUN": {
        "name": "测试跑",
        "name_en": "Test Run",
        "intensity": 4,
        "description": "测试当前配速和能力"
    },
    "REST": {
        "name": "休息日",
        "name_en": "Rest Day",
        "intensity": 0,
        "description": "完全休息"
    },
    "CROSS_TRAIN": {
        "name": "交叉训练",
        "name_en": "Cross Training",
        "intensity": 2,
        "description": "游泳、骑行等低冲击运动"
    }
}

RACE_TYPES = {
    "5K": {
        "name": "5公里",
        "distance": 5.0,
        "base_weeks": 12
    },
    "HALF_MARATHON": {
        "name": "半程马拉松",
        "distance": 21.0975,
        "base_weeks": 16
    },
    "MARATHON": {
        "name": "全程马拉松",
        "distance": 42.195,
        "base_weeks": 20
    }
}

TRAINING_PHASES = {
    "base": {
        "name": "基础期",
        "name_en": "Base Phase",
        "focus": "建立有氧基础，提升跑量",
        "easy_pct": 0.8,
        "tempo_pct": 0.1,
        "interval_pct": 0.1
    },
    "build": {
        "name": "强化期",
        "name_en": "Build Phase",
        "focus": "提升速度和耐力",
        "easy_pct": 0.6,
        "tempo_pct": 0.2,
        "interval_pct": 0.2
    },
    "peak": {
        "name": "巅峰期",
        "name_en": "Peak Phase",
        "focus": "达到最佳竞技状态",
        "easy_pct": 0.5,
        "tempo_pct": 0.25,
        "interval_pct": 0.25
    },
    "taper": {
        "name": "减量期",
        "name_en": "Taper Phase",
        "focus": "充分恢复，保证比赛状态",
        "easy_pct": 0.7,
        "tempo_pct": 0.15,
        "interval_pct": 0.15
    }
}
