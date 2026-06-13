PACE_ZONES = {
    "Z1": {
        "name": "轻松区",
        "name_en": "Recovery Zone",
        "min_pct": 0.5,
        "max_pct": 0.6,
        "description": "恢复/轻松跑"
    },
    "Z2": {
        "name": "有氧区",
        "name_en": "Aerobic Zone",
        "min_pct": 0.6,
        "max_pct": 0.7,
        "description": "长距离/轻松跑"
    },
    "Z3": {
        "name": "马拉松区",
        "name_en": "Marathon Zone",
        "min_pct": 0.7,
        "max_pct": 0.8,
        "description": "节奏跑"
    },
    "Z4": {
        "name": "乳酸阈值区",
        "name_en": "Threshold Zone",
        "min_pct": 0.8,
        "max_pct": 0.88,
        "description": "间歇跑"
    },
    "Z5": {
        "name": "无氧区",
        "name_en": "Anaerobic Zone",
        "min_pct": 0.88,
        "max_pct": 1.0,
        "description": "高强度间歇"
    }
}

GEAR_TIPS = {
    "EASY_RUN": "穿着缓震跑鞋，注意跑步姿势",
    "INTERVAL": "穿轻量竞速鞋，准备秒表或心率带",
    "TEMPO_RUN": "穿竞速跑鞋，携带水壶或了解补给点",
    "LONG_RUN": "穿缓震跑鞋，准备能量胶和盐丸",
    "RECOVERY_RUN": "穿舒适跑鞋，注意保暖",
    "TEST_RUN": "穿竞速跑鞋，携带计时设备",
    "default": "检查跑鞋磨损情况，确保状态良好"
}

NUTRITION_TIPS = {
    "EASY_RUN": "训练前适量补水，训练后补充蛋白质",
    "INTERVAL": "训练前补充碳水化合物，注意运动饮料",
    "TEMPO_RUN": "训练前1-2小时进食，携带补水",
    "LONG_RUN": "训练前补充碳水，训练中每30分钟补水",
    "RECOVERY_RUN": "轻度训练，注意补充电解质",
    "TEST_RUN": "赛前调整饮食，确保充足碳水化合物",
    "default": "保持均衡饮食，注意补充水分"
}

ERROR_CODES = {
    "USER_NOT_FOUND": {"code": "USER_NOT_FOUND", "message": "用户不存在"},
    "PLAN_NOT_FOUND": {"code": "PLAN_NOT_FOUND", "message": "训练计划不存在"},
    "WORKOUT_NOT_FOUND": {"code": "WORKOUT_NOT_FOUND", "message": "训练课次不存在"},
    "INVALID_DATE_RANGE": {"code": "INVALID_DATE_RANGE", "message": "日期范围无效"},
    "INSUFFICIENT_DATA": {"code": "INSUFFICIENT_DATA", "message": "数据不足，无法生成计划"},
    "PLAN_ALREADY_GENERATED": {"code": "PLAN_ALREADY_GENERATED", "message": "计划已生成，无法重复生成"},
    "INVALID_RACE_TYPE": {"code": "INVALID_RACE_TYPE", "message": "无效的赛事类型"},
    "INVALID_PACE": {"code": "INVALID_PACE", "message": "配速格式错误"},
    "FATIUGUE_RISK": {"code": "FATIUGUE_RISK", "message": "检测到疲劳风险，建议调整训练"}
}
