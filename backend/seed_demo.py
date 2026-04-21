"""
seed_demo.py — 向后端注入演示数据并推送一条校园通知。

用法：
    # 终端 1：启动后端
    cd backend && uv run uvicorn app.main:app --reload --port 8000

    # 终端 2：播种演示数据（先启动后端）
    cd backend && uv run python seed_demo.py

    # 终端 3：启动 Windows 客户端
    dotnet run --project src/SchoolNotify.WindowsClient
"""

import sys
import time
import httpx

BASE = "http://127.0.0.1:8000"

DEMO_DEVICE_ID = "demo-device-001"
DEMO_DEVICE_NAME = "教学楼A-101通知屏"
DEMO_USER_ID = "demo-user"
DEMO_CLIENT_VERSION = "1.0.0-demo"

NOTIFICATIONS = [
    {
        "title": "紧急通知：全校停水通知",
        "content": "因市政管网检修，明天（4月22日）8:00-18:00 全校停水，请提前蓄水。",
        "level": "urgent",
    },
    {
        "title": "重要通知：期中考试安排",
        "content": "期中考试将于4月28日至30日进行，请各位同学查看考场安排并准时参加。",
        "level": "important",
    },
    {
        "title": "校园活动：春季运动会",
        "content": "第32届春季运动会将于5月10日举行，欢迎各班级踊跃报名参加。",
        "level": "normal",
    },
    {
        "title": "紧急通知：暴雨预警",
        "content": "气象台发布暴雨橙色预警，今天下午请减少外出，注意安全。",
        "level": "urgent",
    },
    {
        "title": "教务通知：选课系统开放",
        "content": "2026年秋季学期选课系统将于4月25日9:00开放，请在规定时间内完成选课。",
        "level": "important",
    },
]


def seed():
    client = httpx.Client(base_url=BASE, timeout=5)

    if not wait_for_backend(client):
        print("X 后端未启动，请先运行: uv run uvicorn app.main:app --port 8000")
        sys.exit(1)

    # 1. 注册设备
    print("\n--- 注册设备 ---")
    r = client.post("/api/devices/register", json={
        "device_id": DEMO_DEVICE_ID,
        "device_name": DEMO_DEVICE_NAME,
        "client_version": DEMO_CLIENT_VERSION,
    })
    r.raise_for_status()
    device = r.json()
    print(f"  设备: {device['device_name']} ({device['device_id']})")
    print(f"  状态: {device['status']}")

    # 2. 获取绑定码
    print("\n--- 获取绑定码 ---")
    r = client.post("/api/bindings/code", json={"device_id": DEMO_DEVICE_ID})
    r.raise_for_status()
    code_data = r.json()
    print(f"  绑定码: {code_data['code']}")
    print(f"  有效期: {code_data['expires_in_seconds']}秒")

    # 3. 绑定用户
    print("\n--- 绑定用户 ---")
    r = client.post("/api/bindings", json={
        "user_id": DEMO_USER_ID,
        "code": code_data["code"],
    })
    r.raise_for_status()
    binding = r.json()
    print(f"  用户 {binding['user_id']} <-> 设备 {binding['device_id']}")

    # 4. 查看用户设备
    print("\n--- 用户绑定设备 ---")
    r = client.get(f"/api/users/{DEMO_USER_ID}/devices")
    r.raise_for_status()
    for d in r.json()["items"]:
        print(f"  - {d['device_name']} ({d['status']})")

    # 5. 推送通知
    print("\n--- 推送通知 ---")
    for i, n in enumerate(NOTIFICATIONS):
        r = client.post("/api/notifications", json={
            "sender_user_id": DEMO_USER_ID,
            "title": n["title"],
            "content": n["content"],
            "level": n["level"],
            "device_ids": [DEMO_DEVICE_ID],
        })
        r.raise_for_status()
        result = r.json()
        print(f"  [{i + 1}] {n['title']} -> status={result['status']}, targets={result['target_count']}")
        time.sleep(0.3)

    # 6. 查看通知记录
    print("\n--- 通知记录 ---")
    r = client.get("/api/notifications", params={"sender_user_id": DEMO_USER_ID})
    r.raise_for_status()
    for record in r.json()["items"]:
        deliveries = record["deliveries"]
        print(f"  - [{record['level']}] {record['title']}")
        for d in deliveries:
            print(f"    设备 {d['device_id']}: received={d['received']} displayed={d['displayed']} spoken={d['spoken']}")

    print("\n=> 演示数据播种完成!")
    print("\n接下来:")
    print("  1. 启动 Windows 客户端: dotnet run --project windows-client/src/SchoolNotify.WindowsClient")
    print("  2. 客户端将自动注册并连接 WebSocket")
    print("  3. 如需再次推送通知，重新运行此脚本即可")


def wait_for_backend(client: httpx.Client):
    for i in range(30):
        try:
            r = client.get("/health", timeout=2)
            if r.is_success:
                print(f"  后端已就绪 ({r.json()})")
                return True
        except (httpx.ConnectError, httpx.TimeoutException):
            pass
        print(f"  等待后端启动... ({i + 1}/30)")
        time.sleep(1)
    return False


if __name__ == "__main__":
    seed()
