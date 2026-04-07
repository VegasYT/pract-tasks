"""Сравнение подходов для I/O-bound задач: 20 HTTP-запросов."""
import asyncio
import multiprocessing
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import aiohttp
import requests

URL = 'http://testing.edu.aib.pro/api/online_cases/'
REQUESTS_COUNT = 20
SEPARATOR_WIDTH = 50


# =======================
# Синхронный подход
# =======================
def sync_fetch(url: str) -> int:
    """Выполнить один синхронный HTTP-запрос.

    Args:
        url: адрес запроса.

    Returns:
        HTTP-статус ответа.
    """
    response = requests.get(url, timeout=10)
    return response.status_code


def run_sync() -> float:
    """Запустить синхронные запросы последовательно.

    Returns:
        Затраченное время в секундах.
    """
    print('\n[Синхронный] Запуск...')
    start = time.perf_counter()

    for idx in range(REQUESTS_COUNT):
        num = idx + 1
        status = sync_fetch(URL)
        print(f'  Запрос {num:>2}: {status}')

    elapsed = time.perf_counter() - start
    print(f'[Синхронный] Время: {elapsed:.3f} сек')
    return elapsed


# =======================
# Асинхронный подход
# =======================
async def async_fetch(
    session: aiohttp.ClientSession, url: str, idx: int,
) -> int:
    """Выполнить один асинхронный HTTP-запрос.

    Args:
        session: aiohttp-сессия.
        url: адрес запроса.
        idx: порядковый номер запроса для вывода.

    Returns:
        HTTP-статус ответа.
    """
    async with session.get(url) as response:
        print(f'  Запрос {idx:>2}: {response.status}')
        return response.status


async def async_main() -> float:
    """Запустить асинхронные запросы конкурентно.

    Returns:
        Затраченное время в секундах.
    """
    print('\n[Асинхронный] Запуск...')
    start = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        tasks = [
            async_fetch(session, URL, idx + 1)
            for idx in range(REQUESTS_COUNT)
        ]
        await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start
    print(f'[Асинхронный] Время: {elapsed:.3f} сек')
    return elapsed


def run_async() -> float:
    """Запустить асинхронный event loop.

    Returns:
        Затраченное время в секундах.
    """
    return asyncio.run(async_main())


def _log_thread_request(idx: int, status: int, thread_name: str) -> None:
    """Вывести статус запроса из потока.

    Args:
        idx: порядковый номер запроса.
        status: HTTP-статус ответа.
        thread_name: имя потока.
    """
    num = f'{idx:>2}'
    print(f'  Запрос {num}: {status}  [поток: {thread_name}]')


# =======================
# Многопоточный подход
# =======================
def threaded_fetch(args: tuple) -> int:
    """Выполнить запрос из потока.

    Args:
        args: кортеж (порядковый номер, url).

    Returns:
        HTTP-статус ответа.
    """
    idx, url = args
    response = requests.get(url, timeout=10)
    status = response.status_code
    thread_name = threading.current_thread().name
    _log_thread_request(idx, status, thread_name)
    return status


def run_threaded() -> float:
    """Запустить запросы в пуле потоков.

    Returns:
        Затраченное время в секундах.
    """
    print('\n[Многопоточный] ПОЕХАЛИ...')
    start = time.perf_counter()

    arg_list = [(idx + 1, URL) for idx in range(REQUESTS_COUNT)]

    with ThreadPoolExecutor(max_workers=REQUESTS_COUNT) as executor:
        list(executor.map(threaded_fetch, arg_list))

    elapsed = time.perf_counter() - start
    print(f'[Многопоточный] Время: {elapsed:.3f} сек')
    return elapsed


# =======================
# Многопроцессорный подход
# =======================
def process_fetch(args: tuple) -> tuple:
    """Выполнить запрос в отдельном процессе.

    Args:
        args: кортеж (порядковый номер, url).

    Returns:
        Кортеж (порядковый номер, HTTP-статус).
    """
    idx, url = args
    response = requests.get(url, timeout=10)
    return idx, response.status_code


def _fetch_all_processes(arg_list: list) -> list:
    """Запустить все запросы через ProcessPoolExecutor.

    Args:
        arg_list: список кортежей (номер, url).

    Returns:
        Список результатов (номер, статус).
    """
    cpu_count = multiprocessing.cpu_count()
    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        return list(executor.map(process_fetch, arg_list))


def _print_fetch_results(fetch_results: list) -> None:
    """Вывести результаты запросов в порядке номеров.

    Args:
        fetch_results: список кортежей (номер, статус).
    """
    for idx, status in sorted(fetch_results):
        print(f'  Запрос {idx:>2}: {status}')


def run_multiprocess() -> float:
    """Запустить запросы в пуле процессов.

    Returns:
        Затраченное время в секундах.
    """
    print('\n[Многопроцессорный] Запуск...')
    start = time.perf_counter()

    arg_list = [(idx + 1, URL) for idx in range(REQUESTS_COUNT)]
    _print_fetch_results(_fetch_all_processes(arg_list))

    elapsed = time.perf_counter() - start
    print(f'[Многопроцессорный] Время: {elapsed:.3f} сек')
    return elapsed


def _print_results(
    t_sync: float,
    t_async: float,
    t_threaded: float,
    t_multiproc: float,
) -> None:
    """Вывести итоговую таблицу сравнения.

    Args:
        t_sync: время синхронного подхода.
        t_async: время асинхронного подхода.
        t_threaded: время многопоточного подхода.
        t_multiproc: время многопроцессорного подхода.
    """
    x_async = round(t_sync / t_async, 1)
    x_thr = round(t_sync / t_threaded, 1)
    x_mp = round(t_sync / t_multiproc, 1)

    separator = '=' * SEPARATOR_WIDTH
    print(f'\n{separator}')
    print(f'  Синхронный:        {t_sync:.3f} сек')
    print(f'  Асинхронный:       {t_async:.3f} сек  (x{x_async})')
    print(f'  Многопоточный:     {t_threaded:.3f} сек  (x{x_thr})')
    print(f'  Многопроцессорный: {t_multiproc:.3f} сек  (x{x_mp})')


if __name__ == '__main__':
    print(f'I/O-bound: {REQUESTS_COUNT} HTTP-запросов к {URL}')
    print('=' * SEPARATOR_WIDTH)

    _print_results(
        t_sync=run_sync(),
        t_async=run_async(),
        t_threaded=run_threaded(),
        t_multiproc=run_multiprocess(),
    )
