"""
公司模擬器 - 遊戲化核心模組
包含：Token追蹤、抽卡系統、任務關卡、資源系統、升級系統
"""

import streamlit as st
import json
import os
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 數據目錄
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_FILE = os.path.join(DATA_DIR, "game_data.json")
TOKEN_FILE = os.path.join(DATA_DIR, "token_usage.json")

# ==================== Token 用量追蹤 ====================

def load_token_usage() -> Dict:
    """載入 Token 用量數據"""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"total_tokens": 0, "daily_tokens": {}, "last_update": None}
    return {"total_tokens": 0, "daily_tokens": {}, "last_update": None}

def save_token_usage(data: Dict):
    """儲存 Token 用量"""
    data["last_update"] = datetime.now().isoformat()
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_token_usage(prompt_tokens: int = 0, completion_tokens: int = 0):
    """記錄 Token 用量"""
    data = load_token_usage()
    today = datetime.now().strftime("%Y-%m-%d")
    
    data["total_tokens"] += prompt_tokens + completion_tokens
    if today not in data["daily_tokens"]:
        data["daily_tokens"][today] = {"prompt": 0, "completion": 0, "total": 0}
    
    data["daily_tokens"][today]["prompt"] += prompt_tokens
    data["daily_tokens"][today]["completion"] += completion_tokens
    data["daily_tokens"][today]["total"] += prompt_tokens + completion_tokens
    
    save_token_usage(data)
    return data["total_tokens"]

def get_today_tokens() -> int:
    """獲取今日 Token 用量"""
    data = load_token_usage()
    today = datetime.now().strftime("%Y-%m-%d")
    return data.get("daily_tokens", {}).get(today, {}).get("total", 0)

def tokens_to_coins(tokens: int) -> int:
    """Token 轉換為金幣 - 每 1000 tokens = 100 金幣"""
    return int(tokens / 10)

def get_coin_from_tokens() -> int:
    """根據歷史 Token 用量獲取金幣"""
    data = load_token_usage()
    return tokens_to_coins(data.get("total_tokens", 0))

# ==================== 抽卡招募系統 ====================

# 員工稀有度
RARITY = {
    "普通": {"weight": 60, "min_efficiency": 0.8, "max_efficiency": 1.0, "color": "🟢"},
    "稀有": {"weight": 30, "min_efficiency": 1.0, "max_efficiency": 1.3, "color": "🔵"},
    "傳說": {"weight": 10, "min_efficiency": 1.3, "max_efficiency": 1.8, "color": "🟡"},
}

# 員工名字庫
FIRST_NAMES = ["小", "阿", "大", "老", "新", "美", "帥", "聰", "慧", "強", "偉", "芳", "婷", "麗", "軍"]
LAST_NAMES = ["明", "華", "強", "偉", "軍", "麗", "芳", "婷", "美", "帥", "傑", "超", "鵬", "飛", "宇"]

# 角色類型
ROLES = {
    "工程師": {"base_salary": 150, "skill": "程式開發"},
    "設計師": {"base_salary": 130, "skill": "視覺設計"},
    "行銷": {"base_salary": 120, "skill": "市場營銷"},
    "業務": {"base_salary": 140, "skill": "銷售談判"},
    "客服": {"base_salary": 100, "skill": "客戶服務"},
    "財務": {"base_salary": 130, "skill": "財務管理"},
    "人資": {"base_salary": 110, "skill": "人才管理"},
    "運營": {"base_salary": 125, "skill": "運營優化"},
}

# 特殊傳說員工
LEGENDARY_EMPLOYEES = [
    {"name": "🦞 OpenClaw", "role": "AI 工程師", "efficiency": 2.0, "skill_level": 10, "description": "強大的 AI 助手"},
    {"name": "🤖 GPT", "role": "AI 顧問", "efficiency": 1.9, "skill_level": 10, "description": "AI 領域傳奇"},
    {"name": "🧠 MiniMax", "role": "AI 策略師", "efficiency": 1.8, "skill_level": 9, "description": "智能策略大師"},
    {"name": "💡 Claude", "role": "AI 設計師", "efficiency": 1.8, "skill_level": 9, "description": "創意設計天才"},
    {"name": "🌟 Gemini", "role": "AI 全才", "efficiency": 1.7, "skill_level": 8, "description": "全能型 AI"},
]

def generate_random_name() -> str:
    """生成隨機名字"""
    return random.choice(FIRST_NAMES) + random.choice(LAST_NAMES)

def roll_gacha(cost: int = 100) -> Dict:
    """抽卡系統"""
    game = load_game_data()
    
    if game.get("coins", 0) < cost:
        return {"success": False, "error": "金幣不足"}
    
    # 扣除金幣
    game["coins"] -= cost
    game["total_rolls"] = game.get("total_rolls", 0) + 1
    
    # 計算稀有度
    roll = random.randint(1, 100)
    if roll <= RARITY["傳說"]["weight"]:
        rarity = "傳說"
    elif roll <= RARITY["傳說"]["weight"] + RARITY["稀有"]["weight"]:
        rarity = "稀有"
    else:
        rarity = "普通"
    
    # 生成員工
    if rarity == "傳說" and random.random() < 0.3:
        # 30% 機會抽到特殊傳說員工
        emp = random.choice(LEGENDARY_EMPLOYEES).copy()
    else:
        role_name = random.choice(list(ROLES.keys()))
        role_data = ROLES[role_name]
        
        emp = {
            "name": generate_random_name(),
            "role": role_name,
            "skill": role_data["skill"],
            "efficiency": round(random.uniform(RARITY[rarity]["min_efficiency"], RARITY[rarity]["max_efficiency"]), 2),
            "salary": int(role_data["base_salary"] * random.uniform(0.9, 1.1)),
            "rarity": rarity,
            "skill_level": 1,
            "experience": 0,
        }
    
    emp["id"] = len(game.get("employees", [])) + 1
    emp["hired_at"] = datetime.now().strftime("%Y-%m-%d")
    emp["level"] = 1
    
    # 添加員工
    if "employees" not in game:
        game["employees"] = []
    game["employees"].append(emp)
    
    # 記錄抽卡
    if "gacha_history" not in game:
        game["gacha_history"] = []
    game["gacha_history"].append({
        "rarity": rarity,
        "employee": emp["name"],
        "role": emp["role"],
        "timestamp": datetime.now().isoformat()
    })
    
    save_game_data(game)
    
    return {
        "success": True,
        "employee": emp,
        "rarity": rarity,
        "remaining_coins": game["coins"]
    }

def get_gacha_cost(roll_type: str = "single") -> int:
    """獲取抽卡費用"""
    if roll_type == "multi":
        return 900  # 10連抽 = 900
    return 100  # 單抽 = 100

# ==================== 任務關卡系統 ====================

# 任務難度
DIFFICULTY = {
    "簡單": {"multiplier": 1.0, "energy_cost": 10, "time_limit": 60},
    "普通": {"multiplier": 1.5, "energy_cost": 20, "time_limit": 120},
    "困難": {"multiplier": 2.5, "energy_cost": 35, "time_limit": 180},
    "地獄": {"multiplier": 4.0, "energy_cost": 50, "time_limit": 300},
}

# 任務類型
TASK_CATEGORIES = {
    "開發": {"base_reward": 100, "token_cost": 50},
    "設計": {"base_reward": 80, "token_cost": 40},
    "行銷": {"base_reward": 90, "token_cost": 45},
    "銷售": {"base_reward": 120, "token_cost": 60},
    "客服": {"base_reward": 60, "token_cost": 30},
}

# 任務模板
TASK_TEMPLATES = {
    "開發": [
        "開發新功能模組",
        "修復系統 Bug",
        "優化資料庫查詢",
        "實作用戶反饋",
        "重構舊代碼",
    ],
    "設計": [
        "設計新產品 Logo",
        "製作宣傳海報",
        "設計網站介面",
        "創作品牌視覺",
        "設計包裝方案",
    ],
    "行銷": [
        "規劃營銷活動",
        "執行社群推廣",
        "撰寫新聞稿",
        "分析市場趨勢",
        "制定推廣策略",
    ],
    "銷售": [
        "拜訪潛在客戶",
        "談判合作方案",
        "處理客戶訂單",
        "開發新市場",
        "維護客戶關係",
    ],
    "客服": [
        "回覆客戶詢問",
        "處理投訴問題",
        "提供技術支援",
        "解答產品問題",
        "收集用戶反饋",
    ],
}

def generate_task(difficulty: str = "普通", category: str = None) -> Dict:
    """生成任務"""
    game = load_game_data()
    
    if category is None:
        category = random.choice(list(TASK_CATEGORIES.keys()))
    
    task_data = TASK_CATEGORIES[category]
    diff_data = DIFFICULTY[difficulty]
    
    base_reward = task_data["base_reward"]
    reward = int(base_reward * diff_data["multiplier"])
    token_cost = task_data["token_cost"]
    
    task = {
        "id": len(game.get("tasks", [])) + 1,
        "title": random.choice(TASK_TEMPLATES[category]),
        "category": category,
        "difficulty": difficulty,
        "reward_coins": reward,
        "reward_exp": int(reward * 0.5),
        "energy_cost": diff_data["energy_cost"],
        "token_cost": token_cost,
        "status": "pending",
        "assigned_to": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "is_daily": False,
        "is_weekly": False,
        "is_emergency": False,
    }
    
    if "tasks" not in game:
        game["tasks"] = []
    game["tasks"].append(task)
    save_game_data(game)
    
    return task

def generate_daily_tasks():
    """生成每日任務"""
    game = load_game_data()
    tasks = []
    
    # 3 個每日任務
    for i in range(3):
        task = generate_task(difficulty="簡單")
        task["is_daily"] = True
        task["title"] = f"📅 每日: {task['title']}"
        tasks.append(task)
    
    # 2 個普通任務
    for i in range(2):
        task = generate_task(difficulty="普通")
        tasks.append(task)
    
    save_game_data(game)
    return tasks

def generate_weekly_tasks():
    """生成每週任務"""
    game = load_game_data()
    tasks = []
    
    # 1 個週挑戰
    task = generate_task(difficulty="困難")
    task["is_weekly"] = True
    task["title"] = f"🏆 週挑戰: {task['title']}"
    task["reward_coins"] = int(task["reward_coins"] * 1.5)
    task["reward_exp"] = int(task["reward_exp"] * 1.5)
    tasks.append(task)
    
    save_game_data(game)
    return tasks

def generate_emergency_task() -> Dict:
    """生成緊急任務"""
    task = generate_task(difficulty="地獄")
    task["is_emergency"] = True
    task["title"] = f"⚡ 緊急: {task['title']}"
    task["reward_coins"] = int(task["reward_coins"] * 2)
    task["reward_exp"] = int(task["reward_exp"] * 2)
    return task

def complete_task(task_id: int, employee_id: int = None) -> Dict:
    """完成任務"""
    game = load_game_data()
    
    for task in game.get("tasks", []):
        if task["id"] == task_id and task["status"] == "in_progress":
            # 檢查能量
            if game.get("energy", 0) < task["energy_cost"]:
                return {"success": False, "error": "能量不足"}
            
            # 扣除能量
            game["energy"] -= task["energy_cost"]
            
            # 發放獎勵
            game["coins"] = game.get("coins", 0) + task["reward_coins"]
            game["reputation"] = game.get("reputation", 0) + task.get("reward_reputation", 5)
            game["total_tasks_completed"] = game.get("total_tasks_completed", 0) + 1
            
            # 經驗值
            exp_gained = task.get("reward_exp", 0)
            
            # 員工經驗
            if employee_id:
                for emp in game.get("employees", []):
                    if emp["id"] == employee_id:
                        emp["experience"] = emp.get("experience", 0) + exp_gained
                        # 檢查升級
                        if emp["experience"] >= emp.get("level", 1) * 100:
                            emp["level"] = emp.get("level", 1) + 1
                            emp["efficiency"] = round(emp.get("efficiency", 1.0) * 1.1, 2)
            
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            
            # 記錄成就
            check_achievements(game)
            
            # Token 消耗記錄
            add_token_usage(task.get("token_cost", 0), task.get("token_cost", 0) // 2)
            
            save_game_data(game)
            
            return {
                "success": True,
                "coins": task["reward_coins"],
                "exp": exp_gained,
                "reputation": task.get("reward_reputation", 5),
                "new_level": emp.get("level", 1) if employee_id else None
            }
    
    return {"success": False, "error": "任務不存在或已完成"}

# ==================== 資源系統 ====================

def init_game_data() -> Dict:
    """初始化遊戲數據"""
    return {
        "coins": 0,  # 金幣
        "energy": 100,  # 能量
        "max_energy": 100,  # 最大能量
        "reputation": 0,  # 聲望
        "level": 1,  # 公司等級
        "experience": 0,  # 公司經驗
        "total_tasks_completed": 0,
        "total_rolls": 0,
        "employees": [],
        "tasks": [],
        "achievements": [],
        "skills": {
            "coding": 1,
            "design": 1,
            "marketing": 1,
            "sales": 1,
            "service": 1,
        },
        "gacha_history": [],
        "created_at": datetime.now().isoformat(),
    }

def load_game_data() -> Dict:
    """載入遊戲數據"""
    if os.path.exists(GAME_FILE):
        try:
            with open(GAME_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return init_game_data()
    return init_game_data()

def save_game_data(data: Dict):
    """儲存遊戲數據"""
    with open(GAME_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_coins(amount: int):
    """添加金幣"""
    game = load_game_data()
    game["coins"] = game.get("coins", 0) + amount
    save_game_data(game)

def spend_coins(amount: int) -> bool:
    """花費金幣"""
    game = load_game_data()
    if game.get("coins", 0) >= amount:
        game["coins"] -= amount
        save_game_data(game)
        return True
    return False

def add_energy(amount: int):
    """添加能量"""
    game = load_game_data()
    game["energy"] = min(game.get("energy", 0) + amount, game.get("max_energy", 100))
    save_game_data(game)

def regenerate_energy():
    """能量恢復（每小時恢復 10%）"""
    game = load_game_data()
    regen = int(game.get("max_energy", 100) * 0.1)
    game["energy"] = min(game.get("energy", 0) + regen, game.get("max_energy", 100))
    save_game_data(game)

# ==================== 升級系統 ====================

def upgrade_company() -> Dict:
    """升級公司"""
    game = load_game_data()
    
    current_level = game.get("level", 1)
    exp_required = current_level * 1000
    current_exp = game.get("experience", 0)
    
    if current_exp >= exp_required:
        game["level"] = current_level + 1
        game["experience"] = current_exp - exp_required
        game["max_energy"] = 100 + (game["level"] - 1) * 20
        
        # 解鎖新內容
        unlocks = []
        if game["level"] >= 2:
            unlocks.append("解鎖更多員工技能")
        if game["level"] >= 3:
            unlocks.append("解鎖困難任務")
        if game["level"] >= 5:
            unlocks.append("解鎖傳說員工")
        
        save_game_data(game)
        
        return {
            "success": True,
            "new_level": game["level"],
            "unlocks": unlocks
        }
    
    return {
        "success": False,
        "error": f"經驗不足，需要 {exp_required} 經驗，目前 {current_exp}"
    }

def upgrade_skill(skill_name: str) -> Dict:
    """升級技能"""
    game = load_game_data()
    cost = game.get("skills", {}).get(skill_name, 1) * 500
    
    if game.get("coins", 0) >= cost:
        game["coins"] -= cost
        game["skills"][skill_name] = game.get("skills", {}).get(skill_name, 1) + 1
        save_game_data(game)
        
        return {
            "success": True,
            "new_level": game["skills"][skill_name],
            "cost": cost
        }
    
    return {"success": False, "error": "金幣不足"}

# ==================== 成就系統 ====================

ACHIEVEMENTS = {
    "first_task": {"name": "初試身手", "desc": "完成第一個任務", "reward": 100},
    "first_roll": {"name": "幸運抽卡", "desc": "進行第一次抽卡", "reward": 50},
    "ten_tasks": {"name": "任務達人", "desc": "完成 10 個任務", "reward": 500},
    "hundred_tasks": {"name": "任務大師", "desc": "完成 100 個任務", "reward": 5000},
    "legendary": {"name": "傳說降臨", "desc": "招募傳說員工", "reward": 1000},
    "level_5": {"name": "小有名氣", "desc": "公司達到 5 級", "reward": 2000},
    "level_10": {"name": "業界翹楚", "desc": "公司達到 10 級", "reward": 10000},
    "all_skills": {"name": "全能公司", "desc": "所有技能達到 5 級", "reward": 3000},
}

def check_achievements(game: Dict):
    """檢查並解鎖成就"""
    unlocked = game.get("achievements", [])
    new_unlocks = []
    
    # 首次任務
    if "first_task" not in unlocked and game.get("total_tasks_completed", 0) >= 1:
        unlocked.append("first_task")
        new_unlocks.append("初試身手")
        game["coins"] = game.get("coins", 0) + ACHIEVEMENTS["first_task"]["reward"]
    
    # 10 個任務
    if "ten_tasks" not in unlocked and game.get("total_tasks_completed", 0) >= 10:
        unlocked.append("ten_tasks")
        new_unlocks.append("任務達人")
        game["coins"] = game.get("coins", 0) + ACHIEVEMENTS["ten_tasks"]["reward"]
    
    # 100 個任務
    if "hundred_tasks" not in unlocked and game.get("total_tasks_completed", 0) >= 100:
        unlocked.append("hundred_tasks")
        new_unlocks.append("任務大師")
        game["coins"] = game.get("coins", 0) + ACHIEVEMENTS["hundred_tasks"]["reward"]
    
    # 等級成就
    if "level_5" not in unlocked and game.get("level", 1) >= 5:
        unlocked.append("level_5")
        new_unlocks.append("小有名氣")
        game["coins"] = game.get("coins", 0) + ACHIEVEMENTS["level_5"]["reward"]
    
    if "level_10" not in unlocked and game.get("level", 1) >= 10:
        unlocked.append("level_10")
        new_unlocks.append("業界翹楚")
        game["coins"] = game.get("coins", 0) + ACHIEVEMENTS["level_10"]["reward"]
    
    # 檢查傳說員工
    has_legendary = any(e.get("rarity") == "傳說" for e in game.get("employees", []))
    if "legendary" not in unlocked and has_legendary:
        unlocked.append("legendary")
        new_unlocks.append("傳說降臨")
        game["coins"] = game.get("coins", 0) + ACHIEVEMENTS["legendary"]["reward"]
    
    # 檢查全技能
    all_skills_maxed = all(level >= 5 for level in game.get("skills", {}).values())
    if "all_skills" not in unlocked and all_skills_maxed:
        unlocked.append("all_skills")
        new_unlocks.append("全能公司")
        game["coins"] = game.get("coins", 0) + ACHIEVEMENTS["all_skills"]["reward"]
    
    game["achievements"] = unlocked
    save_game_data(game)
    
    return new_unlocks

# ==================== 工具函數 ====================

def get_employee_by_id(employee_id: int) -> Optional[Dict]:
    """根據 ID 獲取員工"""
    game = load_game_data()
    for emp in game.get("employees", []):
        if emp["id"] == employee_id:
            return emp
    return None

def get_task_by_id(task_id: int) -> Optional[Dict]:
    """根據 ID 獲取任務"""
    game = load_game_data()
    for task in game.get("tasks", []):
        if task["id"] == task_id:
            return task
    return None

def assign_task_to_employee(task_id: int, employee_id: int) -> bool:
    """分配任務給員工"""
    game = load_game_data()
    
    for task in game.get("tasks", []):
        if task["id"] == task_id:
            task["assigned_to"] = employee_id
            task["status"] = "in_progress"
            save_game_data(game)
            return True
    
    return False

def format_time_diff(timestamp: str) -> str:
    """格式化時間差"""
    dt = datetime.fromisoformat(timestamp)
    diff = datetime.now() - dt
    
    if diff.days > 0:
        return f"{diff.days} 天前"
    elif diff.seconds >= 3600:
        return f"{diff.seconds // 3600} 小時前"
    elif diff.seconds >= 60:
        return f"{diff.seconds // 60} 分鐘前"
    else:
        return "剛剛"
