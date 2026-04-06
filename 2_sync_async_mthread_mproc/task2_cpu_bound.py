import time
import math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

NUMBERS = list(range(1, 1001))
REPEAT = 500  # сколько раз повторяем весь диапазон


def compute_factorials(numbers: list) -> list:
    return [math.factorial(n) for n in numbers]


# =======================
# Синхронный подход
# =======================
def run_sync() -> float:
    print("\n[Синхронный] Запуск...")
    start = time.perf_counter()

    results = []
    for _ in range(REPEAT):
        results.append(compute_factorials(NUMBERS))

    elapsed = time.perf_counter() - start
    print(f"[Синхронный] Время: {elapsed:.3f} сек")
    return elapsed


# =======================
# Многопоточный подход
# =======================
def run_threaded() -> float:
    print("\n[Многопоточный] Запуск...")
    start = time.perf_counter()

    tasks = [NUMBERS] * REPEAT
    cpu_count = multiprocessing.cpu_count()

    with ThreadPoolExecutor(max_workers=cpu_count) as executor:
        list(executor.map(compute_factorials, tasks))

    elapsed = time.perf_counter() - start
    print(f"[Многопоточный] Время: {elapsed:.2f} сек")
    return elapsed


# =======================
# Многопроцессорный подход
# =======================
def run_multiprocess() -> float:
    print("\n[Многопроцессорный] Запуск...")
    start = time.perf_counter()

    tasks = [NUMBERS] * REPEAT
    cpu_count = multiprocessing.cpu_count()

    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        list(executor.map(compute_factorials, tasks))

    elapsed = time.perf_counter() - start
    print(
        f"[Многопроцессорный] Время: {elapsed:.2f} сек (ядер CPU: {cpu_count})"
    )
    return elapsed


if __name__ == "__main__":
    print(f"CPU-bound: факториал чисел 1..{len(NUMBERS)}, {REPEAT} итераций")
    print("=" * 55)

    t_sync = run_sync()
    t_threaded = run_threaded()
    t_multiproc = run_multiprocess()

    print("\n" + "=" * 55)
    print("ИТОГОВОЕ СРАВНЕНИЕ:")
    print(f"  Синхронный:        {t_sync:.2f} сек")
    x_thr = t_sync / t_threaded
    x_mp = t_sync / t_multiproc
    print(f"  Многопоточный:     {t_threaded:.2f} сек  (x{x_thr:.2f})")
    print(f"  Многопроцессорный: {t_multiproc:.2f} сек  (x{x_mp:.2f})")
