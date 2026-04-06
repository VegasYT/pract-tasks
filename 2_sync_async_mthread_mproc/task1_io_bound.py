import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

import requests
import aiohttp

URL = "http://testing.edu.aib.pro/api/online_cases/"
N = 20


# =======================
# Синхронный подход
# =======================
def sync_fetch(url: str) -> int:
    response = requests.get(url, timeout=10)
    return response.status_code


def run_sync() -> float:
    print("\n[Синхронный] Запуск...")
    start = time.perf_counter()

    for i in range(N):
        status = sync_fetch(URL)
        print(f"  Запрос {i + 1:>2}: {status}")

    elapsed = time.perf_counter() - start
    print(f"[Синхронный] Время: {elapsed:.3f} сек")
    return elapsed


# =======================
# Асинхронный подход
# =======================
async def async_fetch(session: aiohttp.ClientSession, url: str, idx: int) -> int:
    async with session.get(url) as response:
        print(f"  Запрос {idx:>2}: {response.status}")
        return response.status


async def async_main() -> float:
    print("\n[Асинхронный] Запуск...")
    start = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        # Наши 20 корутин
        tasks = [async_fetch(session, URL, i + 1) for i in range(N)]
        # Запускаем конкурентно
        await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start
    print(f"[Асинхронный] Время: {elapsed:.3f} сек")
    return elapsed


def run_async() -> float:
    return asyncio.run(async_main())


# =======================
# Многопоточный подход
# =======================
def threaded_fetch(args: tuple) -> int:
    """Выполняет запрос из потока."""
    idx, url = args
    response = requests.get(url, timeout=10)
    thread_name = threading.current_thread().name
    print(f"  Запрос {idx:>2}: {response.status_code}  [поток: {thread_name}]")
    return response.status_code


def run_threaded() -> float:
    print("\n[Многопоточный] ПОЕХАЛИ...")
    start = time.perf_counter()

    args = [(i + 1, URL) for i in range(N)]

    with ThreadPoolExecutor(max_workers=N) as executor:
        list(executor.map(threaded_fetch, args))

    elapsed = time.perf_counter() - start
    print(f"[Многопоточный] Время: {elapsed:.3f} сек")
    return elapsed


# =======================
# Многопроцессорный подход
# =======================
def process_fetch(args: tuple) -> int:
    idx, url = args
    response = requests.get(url, timeout=10)
    return idx, response.status_code


def run_multiprocess() -> float:
    print("\n[Многопроцессорный] Запуск...")
    start = time.perf_counter()

    args = [(i + 1, URL) for i in range(N)]
    cpu_count = multiprocessing.cpu_count()

    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        results = list(executor.map(process_fetch, args))

    for idx, status in sorted(results):
        print(f"  Запрос {idx:>2}: {status}")

    elapsed = time.perf_counter() - start
    print(f"[Многопроцессорный] Время: {elapsed:.3f} сек")
    return elapsed


if __name__ == "__main__":
    print(f"I/O-bound: {N} HTTP-запросов к {URL}")
    print("=" * 50)

    t_sync = run_sync()
    t_async = run_async()
    t_threaded = run_threaded()
    t_multiproc = run_multiprocess()

    print("\n" + "=" * 50)
    print(f"  Синхронный:        {t_sync:.3f} сек")
    x_async = t_sync / t_async
    x_thr = t_sync / t_threaded
    x_mp = t_sync / t_multiproc
    print(f"  Асинхронный:       {t_async:.3f} сек  (ускорение x{x_async:.1f})")
    print(f"  Многопоточный:     {t_threaded:.3f} сек  (ускорение x{x_thr:.1f})")
    print(f"  Многопроцессорный: {t_multiproc:.3f} сек  (ускорение x{x_mp:.1f})")
