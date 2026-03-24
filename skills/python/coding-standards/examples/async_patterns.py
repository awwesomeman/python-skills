"""非同步程式設計模式範例

展示 Python asyncio 的最佳實踐。
"""

import asyncio
from typing import Any, TypeVar, Callable, Awaitable
from dataclasses import dataclass

T = TypeVar("T")

# Sentinel 物件，用於標記佇列結束
_STOP_SENTINEL = object()


# ============================================================================
# 並行執行：asyncio.gather
# ============================================================================

async def fetch_dashboard_data(user_id: str) -> dict:
    """並行取得儀表板所需的所有資料。

    ✅ 良好：使用 gather 並行執行獨立操作
    """
    # 這些操作彼此獨立，可以並行執行
    users, markets, stats, notifications = await asyncio.gather(
        fetch_user_profile(user_id),
        fetch_user_markets(user_id),
        fetch_user_stats(user_id),
        fetch_notifications(user_id),
    )

    return {
        "user": users,
        "markets": markets,
        "stats": stats,
        "notifications": notifications,
    }


# ❌ 不佳：循序執行獨立操作
async def fetch_dashboard_data_bad(user_id: str) -> dict:
    """循序取得資料 - 效能較差。"""
    users = await fetch_user_profile(user_id)
    markets = await fetch_user_markets(user_id)  # 等待上一個完成才開始
    stats = await fetch_user_stats(user_id)       # 等待上一個完成才開始
    notifications = await fetch_notifications(user_id)

    return {
        "user": users,
        "markets": markets,
        "stats": stats,
        "notifications": notifications,
    }


# ============================================================================
# 錯誤處理：return_exceptions
# ============================================================================

async def fetch_all_with_fallback(urls: list[str]) -> list[dict | None]:
    """取得多個資源，部分失敗不影響其他。"""
    results = await asyncio.gather(
        *[fetch_url(url) for url in urls],
        return_exceptions=True  # 失敗不會中斷其他請求
    )

    # 處理結果，將例外轉為 None
    return [
        result if not isinstance(result, Exception) else None
        for result in results
    ]


async def fetch_url(url: str) -> dict:
    """模擬取得 URL 資料。"""
    return {"url": url, "data": "..."}


# ============================================================================
# 限制並發：Semaphore
# ============================================================================

async def fetch_many_with_limit(
    urls: list[str],
    max_concurrent: int = 10
) -> list[dict]:
    """限制並發數量，避免壓垮目標服務。"""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(url: str) -> dict:
        async with semaphore:
            return await fetch_url(url)

    return await asyncio.gather(
        *[fetch_with_semaphore(url) for url in urls]
    )


# ============================================================================
# 超時控制：asyncio.timeout (Python 3.11+)
# ============================================================================

async def fetch_with_timeout(url: str, timeout_seconds: float = 10.0) -> dict:
    """帶超時的資料取得。"""
    try:
        async with asyncio.timeout(timeout_seconds):
            return await fetch_url(url)
    except asyncio.TimeoutError:
        raise TimeoutError(f"請求超時: {url}")


# Python 3.10 及更早版本
async def fetch_with_timeout_legacy(url: str, timeout_seconds: float = 10.0) -> dict:
    """帶超時的資料取得（舊版相容）。"""
    try:
        return await asyncio.wait_for(
            fetch_url(url),
            timeout=timeout_seconds
        )
    except asyncio.TimeoutError:
        raise TimeoutError(f"請求超時: {url}")


# ============================================================================
# 任務取消處理
# ============================================================================

async def cancellable_operation() -> None:
    """可取消的長時間操作。"""
    try:
        while True:
            await do_some_work()
            await asyncio.sleep(1)  # 允許取消點
    except asyncio.CancelledError:
        # 清理資源
        await cleanup_resources()
        raise  # 重新拋出讓呼叫者知道已取消


async def do_some_work() -> None:
    """模擬工作。"""
    pass


async def cleanup_resources() -> None:
    """清理資源。"""
    pass


# ============================================================================
# 生產者-消費者模式
# ============================================================================

@dataclass
class Task:
    """任務資料結構。"""
    id: str
    data: Any


async def producer(queue: asyncio.Queue, tasks: list[Task]) -> None:
    """生產者：將任務放入佇列。"""
    for task in tasks:
        await queue.put(task)

    # 發送結束信號
    await queue.put(_STOP_SENTINEL)


async def consumer(queue: asyncio.Queue, worker_id: int) -> list[Any]:
    """消費者：從佇列取出並處理任務。"""
    results = []

    while True:
        task = await queue.get()

        if task is _STOP_SENTINEL:
            # 收到結束信號，將信號傳遞給下一個消費者
            await queue.put(_STOP_SENTINEL)
            break

        result = await process_task(task)
        results.append(result)
        queue.task_done()

    return results


async def process_task(task: Task) -> dict:
    """處理單一任務。"""
    return {"task_id": task.id, "status": "completed"}


async def run_producer_consumer(tasks: list[Task], num_workers: int = 3) -> list[Any]:
    """執行生產者-消費者模式。"""
    queue: asyncio.Queue = asyncio.Queue()

    # 啟動生產者
    producer_task = asyncio.create_task(producer(queue, tasks))

    # 啟動消費者
    consumer_tasks = [
        asyncio.create_task(consumer(queue, i))
        for i in range(num_workers)
    ]

    # 等待生產者完成
    await producer_task

    # 等待所有消費者完成
    all_results = await asyncio.gather(*consumer_tasks)

    # 合併結果
    return [result for results in all_results for result in results]


# ============================================================================
# 模擬函式（用於範例）
# ============================================================================

async def fetch_user_profile(user_id: str) -> dict:
    """模擬取得使用者資料。"""
    await asyncio.sleep(0.1)
    return {"id": user_id, "name": "Test User"}


async def fetch_user_markets(user_id: str) -> list[dict]:
    """模擬取得使用者市場。"""
    await asyncio.sleep(0.1)
    return [{"id": "m1", "name": "Market 1"}]


async def fetch_user_stats(user_id: str) -> dict:
    """模擬取得使用者統計。"""
    await asyncio.sleep(0.1)
    return {"total_trades": 100}


async def fetch_notifications(user_id: str) -> list[dict]:
    """模擬取得通知。"""
    await asyncio.sleep(0.1)
    return [{"id": "n1", "message": "Welcome!"}]
