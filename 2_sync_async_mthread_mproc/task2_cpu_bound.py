"""Сравнение подходов для CPU-bound задач: вычисление факториалов."""
import math
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

_NUMBERS_END = 1001
NUMBERS = list(range(1, _NUMBERS_END))
REPEAT = 500  # сколько раз повторяем весь диапазон
SEPARATOR_WIDTH = 55


def compute_factorials(numbers: list) -> list:
    """Вычислить факториалы для списка чисел.

    Args:
        numbers: список целых чисел.

    Returns:
        Список факториалов.
    """
    return [math.factorial(num) for num in numbers]


# =======================
# Синхронный подход
# =======================
def run_sync() -> float:
    """Запустить синхронные вычисления.

    Returns:
        Затраченное время в секундах.
    """
    print('\n[Синхронный] Запуск...')
    start = time.perf_counter()

    computed = []
    for _ in range(REPEAT):
        computed.append(compute_factorials(NUMBERS))

    elapsed = time.perf_counter() - start
    print(f'[Синхронный] Время: {elapsed:.3f} сек')
    return elapsed


# =======================
# Многопоточный подход
# =======================
def _run_thread_pool(tasks: list) -> None:
    """Выполнить задачи в пуле потоков.

    Args:
        tasks: список входных данных для compute_factorials.
    """
    cpu_count = multiprocessing.cpu_count()
    with ThreadPoolExecutor(max_workers=cpu_count) as executor:
        list(executor.map(compute_factorials, tasks))


def run_threaded() -> float:
    """Запустить вычисления в пуле потоков.

    Returns:
        Затраченное время в секундах.
    """
    print('\n[Многопоточный] Запуск...')
    start = time.perf_counter()

    _run_thread_pool([NUMBERS for _ in range(REPEAT)])

    elapsed = time.perf_counter() - start
    print(f'[Многопоточный] Время: {elapsed:.2f} сек')
    return elapsed


# =======================
# Многопроцессорный подход
# =======================
def _run_process_pool(tasks: list) -> None:
    """Выполнить задачи в пуле процессов.

    Args:
        tasks: список входных данных для compute_factorials.
    """
    cpu_count = multiprocessing.cpu_count()
    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        list(executor.map(compute_factorials, tasks))


def run_multiprocess() -> float:
    """Запустить вычисления в пуле процессов.

    Returns:
        Затраченное время в секундах.
    """
    print('\n[Многопроцессорный] Запуск...')
    start = time.perf_counter()

    _run_process_pool([NUMBERS for _ in range(REPEAT)])

    elapsed = time.perf_counter() - start
    cpu_count = multiprocessing.cpu_count()
    timing = f'{elapsed:.2f} сек (ядер CPU: {cpu_count})'
    print(f'[Многопроцессорный] Время: {timing}')
    return elapsed


def _print_results(
    t_sync: float, t_threaded: float, t_multiproc: float,
) -> None:
    """Вывести итоговую таблицу сравнения.

    Args:
        t_sync: время синхронного подхода.
        t_threaded: время многопоточного подхода.
        t_multiproc: время многопроцессорного подхода.
    """
    x_thr = round(t_sync / t_threaded, 2)
    x_mp = round(t_sync / t_multiproc, 2)

    separator = '=' * SEPARATOR_WIDTH
    print(f'\n{separator}')
    print('ИТОГОВОЕ СРАВНЕНИЕ:')
    print(f'  Синхронный:        {t_sync:.2f} сек')
    print(f'  Многопоточный:     {t_threaded:.2f} сек  (x{x_thr})')
    print(f'  Многопроцессорный: {t_multiproc:.2f} сек  (x{x_mp})')


if __name__ == '__main__':
    numbers_count = len(NUMBERS)
    print(f'CPU-bound: факториал чисел 1..{numbers_count}, {REPEAT} итераций')
    print('=' * SEPARATOR_WIDTH)

    _print_results(
        t_sync=run_sync(),
        t_threaded=run_threaded(),
        t_multiproc=run_multiprocess(),
    )
