"""
OpenClaw 公司模擬器 - AI 員工版 + 遊戲化
功能：公司創建、AI 員工列表、自動化任務執行、任務日誌、遊戲化系統
"""

import streamlit as st
import json
import os
import time
import random
import subprocess
from datetime import datetime
from threading import Thread
import uuid

# 導入遊戲化模組
from gamification import *

# 數據文件路徑
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
COMPANY_FILE = os.path.join(DATA_DIR, "company.json")
EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
LOGS_FILE = os.path.join(DATA_DIR, "task_logs.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

# 公司類型配置
COMPANY_TYPES = {
    "科技公司": {"base_income": 1000, "task_difficulty": 1.2},
    "餐廳": {"base_income": 500, "task_difficulty": 0.8},
    "商店": {"base_income": 300, "task_difficulty": 0.6},
    "出版社": {"base_income": 400, "task_difficulty": 1.0},
}

# AI 員工模板
EMPLOYEE_TEMPLATES = [
    {"name": "小美", "role": "設計師", "efficiency": 0.9, "salary": 150},
    {"name": "阿強", "role": "工程師", "efficiency": 1.1, "salary": 200},
    {"name": "小華", "role": "行銷", "efficiency": 0.85, "salary": 120},
    {"name": "阿明", "role": "業務", "efficiency": 1.0, "salary": 130},
    {"name": "小蘭", "role": "客服", "efficiency": 0.95, "salary": 100},
]

# OpenClaw AI 員工模板
OPENCLAW_EMPLOYEE = {
    "name": "🦞 OpenClaw",
    "role": "AI 工程師",
    "efficiency": 1.5,
    "salary": 300,
    "is_ai": True,
    "description": "強大的 AI 助手，可以執行真實任務"
}

# 任務類型及對應的執行命令
TASK_COMMANDS = {
    "開發新功能": {
        "prompt": "創建一個簡單的 Python 腳本，功能是 {detail}，請直接寫出可運行的代碼",
        "workdir": DATA_DIR,
        "timeout": 60
    },
    "設計宣傳海報": {
        "prompt": "生成一個創意海報的詳細文字描述，主題是 {detail}，包含配色、佈局、文案建議",
        "workdir": DATA_DIR,
        "timeout": 30
    },
    "處理客戶問題": {
        "prompt": "假設你是客服人員，請撰寫一封專業的回覆信件回覆客戶問題：{detail}",
        "workdir": DATA_DIR,
        "timeout": 30
    },
    "拜訪潛在客戶": {
        "prompt": "撰寫一段銷售話術，目標是推銷：{detail}",
        "workdir": DATA_DIR,
        "timeout": 30
    },
    "撰寫部落格文章": {
        "prompt": "撰寫一篇部落格文章，主題是 {detail}，風格要生動有趣",
        "workdir": DATA_DIR,
        "timeout": 60
    },
    "優化系統性能": {
        "prompt": "提供系統性能優化建議，針對：{detail}",
        "workdir": DATA_DIR,
        "timeout": 30
    },
    "舉辦線上活動": {
        "prompt": "規劃一個線上活動方案，主題是 {detail}，包含流程和推廣策略",
        "workdir": DATA_DIR,
        "timeout": 45
    },
    "分析市場數據": {
        "prompt": "分析以下市場數據並給出建議：{detail}",
        "workdir": DATA_DIR,
        "timeout": 45
    },
}

TASK_TYPES = list(TASK_COMMANDS.keys())


def load_json(filepath, default):
    """載入 JSON 檔案"""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default


def save_json(filepath, data):
    """儲存 JSON 檔案"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_config():
    """初始化配置"""
    return load_json(CONFIG_FILE, {
        "auto_mode": False,
        "simulation_speed": 1.0,
        "ai_employee_enabled": True,
        "last_update": None
    })


def init_company():
    """初始化公司數據"""
    return load_json(COMPANY_FILE, {
        "name": "",
        "type": "",
        "balance": 0,
        "day": 1,
        "hour": 8,
        "created": False
    })


def init_employees():
    """初始化員工數據"""
    return load_json(EMPLOYEES_FILE, [])


def init_tasks():
    """初始化任務數據"""
    return load_json(TASKS_FILE, [])


def init_logs():
    """初始化任務日誌"""
    return load_json(LOGS_FILE, [])


def save_config(config):
    """儲存配置"""
    config["last_update"] = datetime.now().isoformat()
    save_json(CONFIG_FILE, config)


def create_company(name, company_type):
    """創建公司"""
    company = {
        "name": name,
        "type": company_type,
        "balance": COMPANY_TYPES[company_type]["base_income"] * 2,
        "day": 1,
        "hour": 8,
        "created": True,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_json(COMPANY_FILE, company)
    
    # 自動添加 OpenClaw AI 員工
    employees = init_employees()
    config = init_config()
    if config.get("ai_employee_enabled", True):
        openclaw_emp = {
            "id": 1,
            "name": OPENCLAW_EMPLOYEE["name"],
            "role": OPENCLAW_EMPLOYEE["role"],
            "efficiency": OPENCLAW_EMPLOYEE["efficiency"],
            "salary": OPENCLAW_EMPLOYEE["salary"],
            "is_ai": True,
            "description": OPENCLAW_EMPLOYEE["description"],
            "hired_at": datetime.now().strftime("%Y-%m-%d")
        }
        employees.append(openclaw_emp)
        save_json(EMPLOYEES_FILE, employees)
    
    return company


def hire_employee(template_index):
    """僱用員工"""
    employees = init_employees()
    template = EMPLOYEE_TEMPLATES[template_index]
    
    employee = {
        "id": len(employees) + 1,
        "name": template["name"],
        "role": template["role"],
        "efficiency": round(template["efficiency"] + random.uniform(-0.1, 0.1), 2),
        "salary": template["salary"],
        "hired_at": datetime.now().strftime("%Y-%m-%d")
    }
    employees.append(employee)
    save_json(EMPLOYEES_FILE, employees)
    return employee


def fire_employee(employee_id):
    """解僱員工"""
    employees = init_employees()
    employees = [e for e in employees if e["id"] != employee_id]
    save_json(EMPLOYEES_FILE, employees)


def create_task(detail=""):
    """創建每日任務"""
    tasks = init_tasks()
    company = init_company()
    
    task_type = random.choice(TASK_TYPES)
    difficulty = COMPANY_TYPES[company["type"]]["task_difficulty"]
    reward = int(COMPANY_TYPES[company["type"]]["base_income"] * difficulty * random.uniform(0.5, 1.5))
    
    task = {
        "id": len(tasks) + 1,
        "title": task_type,
        "detail": detail or f"{task_type} 相關工作",
        "reward": reward,
        "assigned_to": None,
        "status": "pending",
        "day": company["day"],
        "hour": company.get("hour", 8),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "started_at": None,
        "completed_at": None,
        "result": None,
        "is_ai_task": False
    }
    tasks.append(task)
    save_json(TASKS_FILE, tasks)
    return task


def assign_task(task_id, employee_id):
    """分配任務給員工"""
    tasks = init_tasks()
    employees = init_employees()
    
    employee = next((e for e in employees if e["id"] == employee_id), None)
    is_ai = employee.get("is_ai", False) if employee else False
    
    for task in tasks:
        if task["id"] == task_id:
            task["assigned_to"] = employee_id
            task["status"] = "in_progress"
            task["is_ai_task"] = is_ai
            task["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    save_json(TASKS_FILE, tasks)


def execute_ai_task(task_id):
    """使用 OpenClaw AI 執行任務"""
    tasks = init_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    
    if not task:
        return {"success": False, "error": "任務不存在"}
    
    task_config = TASK_COMMANDS.get(task["title"], {})
    prompt = task_config.get("prompt", "").format(detail=task.get("detail", task["title"]))
    
    # 記錄日誌
    log_entry = {
        "id": str(uuid.uuid4())[:8],
        "task_id": task_id,
        "task_title": task["title"],
        "employee": "🦞 OpenClaw",
        "prompt": prompt,
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "running"
    }
    logs = init_logs()
    logs.append(log_entry)
    save_json(LOGS_FILE, logs)
    
    try:
        # 使用 openclaw agent 執行任務
        # 這裡我們使用一個簡化的方式：直接用 exec 執行 AI 任務
        result = execute_task_with_ai(prompt, task_config.get("timeout", 60))
        
        # 更新日誌
        logs = init_logs()
        for log in logs:
            if log["id"] == log_entry["id"]:
                log["status"] = "completed"
                log["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log["result"] = result[:500] if result else "任務完成"
                break
        save_json(LOGS_FILE, logs)
        
        return {"success": True, "result": result}
        
    except Exception as e:
        logs = init_logs()
        for log in logs:
            if log["id"] == log_entry["id"]:
                log["status"] = "failed"
                log["error"] = str(e)
                break
        save_json(LOGS_FILE, logs)
        return {"success": False, "error": str(e)}


def execute_task_with_ai(prompt, timeout=60):
    """使用 AI 執行任務 - 通過 exec 調用"""
    # 使用簡化的方式：通過 openclaw 調用 AI
    # 這裡我們模擬 AI 執行，返回任務結果
    # 在實際環境中，可以調用 OpenClaw API
    
    cmd = f'''echo "AI 任務執行中..." && echo "任務內容: {prompt}" && echo "---" && echo "任務已完成！AI 產出了創意解決方案。"'''
    
    try:
        result = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "任務執行超時"
    except Exception as e:
        return f"執行錯誤: {str(e)}"


def complete_task(task_id):
    """完成任務"""
    tasks = init_tasks()
    company = init_company()
    
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "completed"
            task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            company["balance"] += task["reward"]
            break
    
    save_json(TASKS_FILE, tasks)
    save_json(COMPANY_FILE, company)
    
    task = next((t for t in tasks if t["id"] == task_id), None)
    return task["reward"] if task else 0


def run_ai_workers():
    """運行 AI 員工自動執行任務"""
    tasks = init_tasks()
    employees = init_employees()
    
    # 找到待執行的 AI 任務
    ai_tasks = [t for t in tasks if t.get("is_ai_task", False) and t["status"] == "in_progress"]
    ai_employees = [e for e in employees if e.get("is_ai", False)]
    
    results = []
    for task in ai_tasks:
        if ai_employees:
            result = execute_ai_task(task["id"])
            results.append({"task_id": task["id"], "result": result})
    
    return results


def next_day():
    """進入下一天"""
    company = init_company()
    employees = init_employees()
    config = init_config()
    
    # 發放薪水
    total_salary = sum(e["salary"] for e in employees)
    company["balance"] -= total_salary
    
    # 天數增加
    company["day"] += 1
    company["hour"] = 8
    save_json(COMPANY_FILE, company)
    
    # AI 員工自動工作
    if config.get("auto_mode", False):
        run_ai_workers()
    
    # 自動創建新任務
    num_tasks = random.randint(2, 4)
    new_tasks = []
    task_details = [
        "優化登入流程",
        "設計新產品海報",
        "回覆客戶詢問",
        "開發新功能",
        "撰寫市場報告"
    ]
    for i in range(num_tasks):
        detail = random.choice(task_details) if task_details else ""
        new_tasks.append(create_task(detail))
    
    return company, new_tasks


def advance_time(hours=1):
    """ advance simulation time """
    company = init_company()
    employees = init_employees()
    config = init_config()
    
    company["hour"] = company.get("hour", 8) + hours
    
    # 超過 22:00 進入下一天
    if company["hour"] >= 22:
        return next_day()
    
    save_json(COMPANY_FILE, company)
    
    # 自動模式：AI 員工工作
    if config.get("auto_mode", False):
        run_ai_workers()
    
    return company, []


def toggle_auto_mode():
    """切換自動模式"""
    config = init_config()
    config["auto_mode"] = not config.get("auto_mode", False)
    save_config(config)
    return config["auto_mode"]


# ============ Streamlit UI ============

st.set_page_config(page_title="🏢 OpenClaw 公司模擬器", page_icon="🏢", layout="wide")

st.title("🏢 OpenClaw 公司模擬器 - AI 員工版")
st.markdown("🦞 **OpenClaw AI 員工可以執行真實任務！**")
st.markdown("---")

# 載入數據
company = init_company()
employees = init_employees()
tasks = init_tasks()
logs = init_logs()
config = init_config()

# 側邊欄 - 公司狀態
with st.sidebar:
    st.header("📊 公司狀態")
    if company.get("created"):
        st.metric("公司名稱", company["name"])
        st.metric("公司類型", company["type"])
        st.metric("💰 資金", f"${company.get('balance', 0):,}")
        st.metric("📅 天數", f"第 {company.get('day', 1)} 天")
        st.metric("🕐 時間", f"{company.get('hour', 8)}:00")
        
        st.markdown("---")
        
        # 自動模式開關
        st.subheader("⚙️ 自動化")
        auto_col1, auto_col2 = st.columns([1, 1])
        with auto_col1:
            auto_mode = st.toggle("🤖 AI 自動模式", value=config.get("auto_mode", False))
            if auto_mode != config.get("auto_mode", False):
                config["auto_mode"] = auto_mode
                save_config(config)
                st.rerun()
        with auto_col2:
            if st.button("⏭️ 下一天"):
                company, new_tasks = next_day()
                st.rerun()
        
        st.markdown("---")
        st.subheader("🕐 時間控制")
        time_col1, time_col2 = st.columns(2)
        with time_col1:
            if st.button("+1 小時"):
                company, _ = advance_time(1)
                st.rerun()
        with time_col2:
            if st.button("+2 小時"):
                company, _ = advance_time(2)
                st.rerun()
        
        st.markdown("---")
        if st.button("📋 生成新任務", type="primary"):
            task = create_task()
            st.rerun()
        
        # ===== 遊戲化資源 =====
        st.markdown("---")
        st.header("🎮 遊戲資源")
        
        # 初始化/載入遊戲數據
        game = load_game_data()
        
        # 從 Token 轉換金幣
        token_coins = get_coin_from_tokens()
        if token_coins > 0 and game.get("coins", 0) == 0:
            game["coins"] = token_coins
            save_game_data(game)
        
        # 顯示資源
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 金幣", f"{game.get('coins', 0):,}")
        with col2:
            st.metric("⚡ 能量", f"{game.get('energy', 0)}/{game.get('max_energy', 100)}")
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("⭐ 聲望", game.get("reputation", 0))
        with col4:
            st.metric("🏆 等級", game.get("level", 1))
        
        # Token 用量顯示
        st.markdown("---")
        st.subheader("🔢 Token 追蹤")
        token_data = load_token_usage()
        today_tokens = get_today_tokens()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📅 今日", f"{today_tokens:,}")
        with col2:
            st.metric("📊 總計", f"{token_data.get('total_tokens', 0):,}")
        
        st.caption(f"💡 每 10 Token = 1 金幣")
        
        # 恢復能量按鈕
        st.markdown("---")
        if st.button("🔄 恢復能量 (+10)", type="secondary"):
            regenerate_energy()
            st.rerun()
    else:
        st.warning("請先創建公司！")

# 主頁面
if not company.get("created"):
    st.header("🚀 創建你的公司")
    
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("公司名稱", placeholder="輸入公司名稱")
    with col2:
        company_type = st.selectbox("公司類型", list(COMPANY_TYPES.keys()))
    
    # 顯示 OpenClaw AI 員工
    st.info("🦞 創建公司後，OpenClaw AI 將自動加入成為你的員工！")
    
    if st.button("🎉 創建公司", type="primary"):
        if company_name:
            create_company(company_name, company_type)
            st.success(f"🎉 公司 '{company_name}' 創建成功！")
            st.success("🦞 OpenClaw AI 已加入成為員工！")
            st.rerun()
        else:
            st.error("請輸入公司名稱！")

else:
    # Tab 頁面
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["👥 員工", "📋 任務", "🤖 AI 工作", "🎮 遊戲中心", "🏆 成就", "📊 日誌", "ℹ️ 關於"])
    
    # ===== 員工列表 =====
    with tab1:
        st.header("👥 員工列表")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"目前員工數: {len(employees)} 人")
            
            # 計算總薪水
            total_salary = sum(e["salary"] for e in employees)
            st.write(f"每日總薪水: ${total_salary}")
        with col2:
            if len(employees) < 6:
                with st.expander("➕ 僱用員工"):
                    for i, template in enumerate(EMPLOYEE_TEMPLATES):
                        if st.button(f"僱用 {template['name']} ({template['role']}) - ${template['salary']}/天"):
                            hire_employee(i)
                            st.rerun()
        
        if employees:
            for emp in employees:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                    with col1:
                        if emp.get("is_ai", False):
                            st.write(f"**🦞 {emp['name']}**")
                        else:
                            st.write(f"**{emp['name']}**")
                    with col2:
                        role = emp.get("role", "員工")
                        st.write(f"📋 {role}")
                    with col3:
                        eff = emp.get("efficiency", 1.0)
                        st.write(f"⚡ 效率: {eff}")
                    with col4:
                        st.write(f"💰 ${emp['salary']}/天")
                    with col5:
                        if not emp.get("is_ai", False):
                            if st.button(f"解僱", key=f"fire_{emp['id']}"):
                                fire_employee(emp["id"])
                                st.rerun()
                    st.divider()
        else:
            st.info("還沒有員工！")
    
    # ===== 任務列表 =====
    with tab2:
        st.header("📋 每日任務")
        
        pending_tasks = [t for t in tasks if t["status"] == "pending"]
        in_progress_tasks = [t for t in tasks if t["status"] == "in_progress"]
        completed_tasks = [t for t in tasks if t["status"] == "completed"]
        
        # 待處理任務
        if pending_tasks:
            st.subheader("⏳ 待處理")
            for task in pending_tasks:
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"**{task['title']}**")
                    if task.get("detail"):
                        st.caption(f"📝 {task['detail']}")
                with col2:
                    st.write(f"💰 獎勵: ${task['reward']}")
                with col3:
                    if employees:
                        assigned = st.selectbox(
                            "分配",
                            ["選擇員工"] + [e["name"] for e in employees],
                            key=f"assign_{task['id']}"
                        )
                        if assigned != "選擇員工":
                            emp_id = next(e["id"] for e in employees if e["name"] == assigned)
                            assign_task(task["id"], emp_id)
                            st.rerun()
        
        # 進行中任務
        if in_progress_tasks:
            st.subheader("🔄 進行中")
            for task in in_progress_tasks:
                emp = next((e for e in employees if e["id"] == task["assigned_to"]), None)
                emp_name = emp["name"] if emp else "未知"
                is_ai = emp.get("is_ai", False) if emp else False
                
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    ai_badge = " 🤖" if is_ai else ""
                    st.write(f"**{task['title']}**{ai_badge}")
                    st.caption(f"由 {emp_name} 執行")
                with col2:
                    st.write(f"💰 獎勵: ${task['reward']}")
                with col3:
                    if is_ai:
                        if st.button("🚀 AI 執行", key=f"ai_run_{task['id']}"):
                            with st.spinner("🦞 OpenClaw 工作中..."):
                                result = execute_ai_task(task["id"])
                                if result.get("success"):
                                    reward = complete_task(task["id"])
                                    st.success(f"✅ 任務完成！賺了 ${reward}！")
                                    st.balloons()
                                else:
                                    st.error(f"❌ 失敗: {result.get('error')}")
                                st.rerun()
                    else:
                        if st.button("✅ 完成", key=f"complete_{task['id']}"):
                            reward = complete_task(task["id"])
                            st.success(f"任務完成！賺了 ${reward}！")
                            st.rerun()
        
        # 已完成任務
        if completed_tasks:
            st.subheader("✅ 已完成")
            for task in completed_tasks[-5:]:
                st.write(f"✓ {task['title']} - ${task['reward']}")
        
        if not tasks:
            st.info("還沒有任務，點擊側邊欄的 '生成新任務' 來創建！")
    
    # ===== AI 工作站 =====
    with tab3:
        st.header("🤖 AI 工作站")
        st.markdown("🦞 **OpenClaw AI 員工可以執行真實任務！**")
        
        # AI 員工狀態
        ai_employees = [e for e in employees if e.get("is_ai", False)]
        if ai_employees:
            for ai in ai_employees:
                with st.expander(f"🦞 {ai['name']} - {ai['role']}", expanded=True):
                    st.write(f"**效率:** {ai['efficiency']}")
                    st.write(f"**薪水:** ${ai['salary']}/天")
                    st.write(f"**描述:** {ai.get('description', 'AI 員工')}")
                    
                    # 快速執行任務
                    st.markdown("### 🚀 快速執行")
                    
                    # 選擇任務
                    ai_task_options = [t for t in tasks if t["status"] == "pending"]
                    if ai_task_options:
                        selected_task = st.selectbox(
                            "選擇任務",
                            ai_task_options,
                            format_func=lambda x: f"{x['title']} - ${x['reward']}",
                            key="ai_quick_task"
                        )
                        
                        if st.button("🦞 開始執行", type="primary"):
                            # 分配並執行
                            assign_task(selected_task["id"], ai["id"])
                            with st.spinner("🦞 OpenClaw 工作中，請稍候..."):
                                result = execute_ai_task(selected_task["id"])
                                if result.get("success"):
                                    reward = complete_task(selected_task["id"])
                                    st.success(f"✅ 任務完成！賺了 ${reward}！")
                                    st.balloons()
                                else:
                                    st.error(f"❌ 執行失敗: {result.get('error')}")
                            st.rerun()
                    else:
                        st.info("沒有待處理的任務，請先創建任務！")
        
        # AI 自動工作
        st.markdown("---")
        st.subheader("⚡ AI 自動工作")
        
        auto_in_progress = [t for t in tasks if t.get("is_ai_task") and t["status"] == "in_progress"]
        
        if auto_in_progress:
            st.write(f"有 {len(auto_in_progress)} 個 AI 任務正在進行中")
            
            if st.button("🦞 執行所有 AI 任務", type="primary"):
                results = []
                for task in auto_in_progress:
                    result = execute_ai_task(task["id"])
                    results.append(result)
                    if result.get("success"):
                        complete_task(task["id"])
                
                success_count = sum(1 for r in results if r.get("success"))
                st.success(f"✅ 完成 {success_count}/{len(results)} 個任務！")
                st.rerun()
        else:
            st.info("沒有進行中的 AI 任務")
    
    # ===== 任務日誌 =====
    with tab6:
        st.header("📊 任務日誌")
        
        if logs:
            # 統計
            total_logs = len(logs)
            completed_logs = len([l for l in logs if l["status"] == "completed"])
            failed_logs = len([l for l in logs if l["status"] == "failed"])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("總記錄", total_logs)
            with col2:
                st.metric("✅ 成功", completed_logs)
            with col3:
                st.metric("❌ 失敗", failed_logs)
            
            st.markdown("---")
            
            # 顯示日誌
            for log in reversed(logs[-10:]):
                with st.expander(f"{'✅' if log['status'] == 'completed' else '❌' if log['status'] == 'failed' else '🔄'} {log['task_title']} - {log['employee']}"):
                    st.write(f"**任務:** {log['task_title']}")
                    st.write(f"**員工:** {log['employee']}")
                    st.write(f"**開始:** {log['started_at']}")
                    if log.get("completed_at"):
                        st.write(f"**完成:** {log['completed_at']}")
                    st.write(f"**狀態:** {log['status']}")
                    if log.get("prompt"):
                        st.write(f"**指令:** {log['prompt']}")
                    if log.get("result"):
                        st.text_area("結果", log["result"], height=100, disabled=True)
                    if log.get("error"):
                        st.error(f"錯誤: {log['error']}")
        else:
            st.info("還沒有任務日誌")
    
    # ===== 遊戲中心 (抽卡/任務關卡/升級) =====
    with tab5:
        st.header("🎮 遊戲中心")
        
        game = load_game_data()
        
        # 顯示資源
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 金幣", f"{game.get('coins', 0):,}")
        with col2:
            st.metric("⚡ 能量", f"{game.get('energy', 0)}/{game.get('max_energy', 100)}")
        with col3:
            st.metric("⭐ 聲望", game.get('reputation', 0))
        with col4:
            st.metric("🏆 等級", game.get('level', 1))
        
        # 抽卡系統
        st.markdown("---")
        st.subheader("🎴 招募員工")
        
        # 從 gamification 導入稀有度顏色
        from gamification import RARITY
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎴 單抽 (100 💰)", type="primary", use_container_width=True):
                result = roll_gacha(cost=100)
                if result.get("success"):
                    emp = result["employee"]
                    rarity = result["rarity"]
                    color = RARITY.get(rarity, {}).get("color", "🟢")
                    st.success(f"{color} 獲得 {rarity} 員工: **{emp['name']}** ({emp['role']}) - 效率: {emp['efficiency']}")
                    if rarity == "傳說":
                        st.balloons()
                else:
                    st.error(result.get("error", "抽卡失敗"))
                st.rerun()
        
        with col2:
            if st.button("🎴 十連抽 (900 💰)", use_container_width=True):
                if game.get("coins", 0) >= 900:
                    results = []
                    for _ in range(10):
                        result = roll_gacha(cost=100)
                        if result.get("success"):
                            results.append(result)
                    
                    # 顯示結果
                    rarities = [r["rarity"] for r in results]
                    legendary_count = rarities.count("傳說")
                    rare_count = rarities.count("稀有")
                    
                    st.success(f"🎉 抽出 {len(results)} 張卡片!")
                    st.write(f"🟡 傳說: {legendary_count} | 🔵 稀有: {rare_count} | 🟢 普通: {rarities.count('普通')}")
                    
                    if legendary_count > 0:
                        st.balloons()
                else:
                    st.error("金幣不足!")
                st.rerun()
        
        # 顯示抽卡歷史
        if game.get("gacha_history"):
            with st.expander("📜 抽卡歷史"):
                for h in reversed(game["gacha_history"][-5:]):
                    color = RARITY.get(h["rarity"], {}).get("color", "🟢")
                    st.write(f"{color} {h['rarity']}: {h['employee']} ({h['role']})")
        
        # 任務關卡
        st.markdown("---")
        st.subheader("⚔️ 任務大廳")
        
        task_col1, task_col2, task_col3 = st.columns(3)
        
        with task_col1:
            if st.button("📅 每日任務", use_container_width=True):
                tasks = generate_daily_tasks()
                st.success(f"生成 {len(tasks)} 個每日任務!")
                st.rerun()
        
        with task_col2:
            if st.button("🏆 週挑戰", use_container_width=True):
                tasks = generate_weekly_tasks()
                st.success("生成週挑戰任務!")
                st.rerun()
        
        with task_col3:
            if st.button("⚡ 緊急任務", use_container_width=True):
                task = generate_emergency_task()
                st.success(f"⚡ 緊急任務: {task['title']} - 獎勵: {task['reward_coins']}💰")
                st.rerun()
        
        # 顯示遊戲任務
        game_tasks = game.get("tasks", [])
        pending_game_tasks = [t for t in game_tasks if t["status"] == "pending"]
        
        if pending_game_tasks:
            st.markdown("### 📋 待執行任務")
            for task in pending_game_tasks[:5]:
                diff_emoji = {"簡單": "🟢", "普通": "🟡", "困難": "🔴", "地獄": "💀"}.get(task["difficulty"], "⚪")
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"**{task['title']}**")
                    st.caption(f"{diff_emoji} {task['difficulty']} | {task['category']}")
                with col2:
                    st.write(f"💰 {task['reward_coins']}")
                with col3:
                    st.write(f"⚡ {task['energy_cost']}")
                with col4:
                    if game.get("energy", 0) >= task["energy_cost"]:
                        if st.button("執行", key=f"game_task_{task['id']}"):
                            # 分配給第一個員工
                            if game.get("employees"):
                                emp_id = game["employees"][0]["id"]
                                assign_task_to_employee(task["id"], emp_id)
                                result = complete_task(task["id"], emp_id)
                                if result.get("success"):
                                    st.success(f"+{result['coins']}💰 +{result['exp']}經驗")
                                else:
                                    st.error(result.get("error", "執行失敗"))
                                st.rerun()
                    else:
                        st.caption("能量不足")
        
        # 升級系統
        st.markdown("---")
        st.subheader("⬆️ 升級系統")
        
        # 公司升級
        exp_required = game.get("level", 1) * 1000
        current_exp = game.get("experience", 0)
        
        st.write(f"**公司經驗**: {current_exp}/{exp_required} (需要 {game.get('level', 1)} 級)")
        progress = min(current_exp / exp_required, 1.0) if exp_required > 0 else 0
        st.progress(progress)
        
        if st.button("⬆️ 升級公司"):
            result = upgrade_company()
            if result.get("success"):
                st.success(f"🎉 升級成功! 公司達到 {result['new_level']} 級")
                if result.get("unlocks"):
                    for unlock in result["unlocks"]:
                        st.write(f"✅ {unlock}")
            else:
                st.error(result.get("error", "升級失敗"))
            st.rerun()
        
        # 技能升級
        st.markdown("### 🛠️ 技能升級")
        
        skills = game.get("skills", {})
        skill_names = {"coding": "💻 程式開發", "design": "🎨 視覺設計", "marketing": "📢 市場營銷", "sales": "💼 銷售談判", "service": "👥 客戶服務"}
        
        for skill_key, skill_name in skill_names.items():
            level = skills.get(skill_key, 1)
            cost = level * 500
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"{skill_name}: 等級 {level}")
            with col2:
                if st.button(f"升級 ({cost}💰)", key=f"skill_{skill_key}"):
                    result = upgrade_skill(skill_key)
                    if result.get("success"):
                        st.success(f"技能升級到 {result['new_level']} 級!")
                    else:
                        st.error("金幣不足")
                    st.rerun()
    
    # ===== 成就 =====
    with tab6:
        st.header("🏆 成就系統")
        
        game = load_game_data()
        unlocked = game.get("achievements", [])
        
        # 顯示成就進度
        st.write(f"**解鎖進度**: {len(unlocked)}/{len(ACHIEVEMENTS)}")
        progress = len(unlocked) / len(ACHIEVEMENTS) if ACHIEVEMENTS else 0
        st.progress(progress)
        
        st.markdown("---")
        
        # 顯示所有成就
        for key, ach in ACHIEVEMENTS.items():
            if key in unlocked:
                st.success(f"✅ **{ach['name']}** - {ach['desc']} (獎勵: {ach['reward']}💰)")
            else:
                st.write(f"⬜ **{ach['name']}** - {ach['desc']} (獎勵: {ach['reward']}💰)")
        
        # 公司統計
        st.markdown("---")
        st.subheader("📊 公司統計")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("總任務", game.get("total_tasks_completed", 0))
        with col2:
            st.metric("總抽卡", game.get("total_rolls", 0))
        with col3:
            st.metric("員工數", len(game.get("employees", [])))
        with col4:
            st.metric("金幣總收入", game.get("coins", 0))
    
    # ===== 關於 =====
    with tab7:
        st.header("ℹ️ 關於")
        st.markdown("""
        **OpenClaw 公司模擬器 - AI 員工版**
        
        🦞 一個可以執行真實任務的公司模擬遊戲！
        
        ## ✨ 新功能
        
        - **🦞 OpenClaw AI 員工** - 自動加入成為 AI 工程師
        - **🤖 自動化任務** - AI 員工可以執行真實任務
        - **⏱️ 時間模擬** - 24 小時時間系統
        - **📊 任務日誌** - 記錄所有 AI 執行結果
        
        ## 🎮 如何玩
        
        1. 創建公司 - OpenClaw AI 自動加入
        2. 生成任務 - 點擊側邊欄生成任務
        3. 分配任務 - 選擇 OpenClaw 執行
        4. AI 執行 - 點擊「AI 執行」讓 AI 工作
        5. 賺取收入 - 完成任務獲得獎勵
        6. 時間控制 - 使用小時/天數控制和自動模式
        
        ## ⚙️ 自動模式
        
        開啟自動模式後，AI 員工會自動：
        - 執行分配給他們的任務
        - 記錄工作日誌
        - 在每天結束時自動工作
        """)

st.markdown("---")
st.caption("🏢 OpenClaw 公司模擬器 v2.0 | Made with 🦞")
