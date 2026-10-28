"""
Лабораторная работа № 2. Вариант 13.
Дисциплина: Теория алгоритмов.
Выполнила: Кугушева Арина Вячеславовна, группа БИ 2-1.

Эмпирический анализ временной сложности квадратичных сортировок:
сортировка обменом («пузырьком», с флагом) и сортировка вставками.

Исходные данные варианта 13:
    размеры n = 1000, 2000, 3000, 4000, 5000;
    тип данных S (упорядоченные), диапазон значений [0; 1000];
    число повторов k = 5 (в качестве результата берётся медиана);
    дополнительное задание М1 - подсчёт числа сравнений и числа
    обменов (сдвигов) для каждого алгоритма, проверка соотношений
    ~ n^2/2 и ~ n^2/4.

Запуск:  python lr2_variant13.py          (график сохраняется в lr2_plot.png)
         python lr2_variant13.py --show   (дополнительно показать график)
Требуется: matplotlib.
"""
import platform
import random
import statistics
import sys
import time

import matplotlib

if "--show" not in sys.argv:
    matplotlib.use("Agg")          # без окна: график только сохраняется в файл
import matplotlib.pyplot as plt

# ----------------------------- параметры варианта -----------------------------
SIZES = [1000, 2000, 3000, 4000, 5000]
KIND = "sorted"                    # тип S - упорядоченные данные
LO, HI = 0, 1000                   # диапазон значений
REPEATS = 5                        # число повторов k
SEED = 42


# ------------------------------ генерация данных ------------------------------
def generate_data(n, kind="random", lo=LO, hi=HI, seed=SEED):
    """Генерирует массив длины n заданного типа.

    kind: "random" (R), "sorted" (S), "reversed" (V).
    Генератор с фиксированным seed делает эксперимент воспроизводимым.
    """
    rng = random.Random(seed + n)
    data = [rng.randint(lo, hi) for _ in range(n)]
    if kind == "sorted":
        data.sort()
    elif kind == "reversed":
        data.sort(reverse=True)
    return data


# ------------------------------ алгоритмы сортировки --------------------------
# Все функции НЕ изменяют исходный массив и возвращают новый список.
def bubble_sort(arr):
    """Сортировка пузырьком с флагом досрочного выхода."""
    a = arr.copy()
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def insertion_sort(arr):
    """Сортировка вставками."""
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


# Версии со счётчиками для задания М1 (отдельные, чтобы счётчики не влияли
# на измерение времени). Возвращают (отсортированный список, сравнений, обменов).
def bubble_sort_counted(arr):
    """Пузырёк с флагом: считает сравнения и обмены."""
    a = arr.copy()
    n = len(a)
    comparisons = swaps = 0
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return a, comparisons, swaps


def insertion_sort_counted(arr):
    """Вставки: считает сравнения элементов и сдвиги."""
    a = arr.copy()
    comparisons = shifts = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1               # сравнение a[j] > key
            if a[j] > key:
                a[j + 1] = a[j]
                shifts += 1
                j -= 1
            else:
                break
        a[j + 1] = key
    return a, comparisons, shifts


# ------------------------------- замер времени --------------------------------
def measure(sort_func, data, repeats=REPEATS):
    """Медианное время работы sort_func на данных data, с (perf_counter)."""
    expected = sorted(data)
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = sort_func(data)
        times.append(time.perf_counter() - start)
        assert result == expected, f"{sort_func.__name__}: ошибка сортировки"
    return statistics.median(times)


def run_series(kind):
    """Времена обоих алгоритмов для всех n из SIZES на данных типа kind."""
    res = {"Пузырьком": [], "Вставками": []}
    for n in SIZES:
        data = generate_data(n, kind)
        res["Пузырьком"].append(measure(bubble_sort, data))
        res["Вставками"].append(measure(insertion_sort, data))
    return res


def system_info():
    """Характеристики вычислительной системы (для отчёта)."""
    cpu = platform.processor() or platform.machine()
    try:                                           # Linux: точное имя процессора
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("model name"):
                    cpu = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    return (f"ОС: {platform.system()} {platform.release()}; процессор: {cpu}; "
            f"Python {platform.python_version()}")


def ratio_line(times, label):
    """Отношения T(2n)/T(n) для пар 1000->2000 и 2000->4000."""
    t = dict(zip(SIZES, times))
    parts = []
    for n in (1000, 2000):
        parts.append(f"{n}->{2 * n}: {t[2 * n] / t[n]:.2f}")
    return f"{label:<11}" + "   ".join(parts)


# ------------------------------------ main ------------------------------------
def main():
    print("Лабораторная работа № 2, вариант 13")
    print(system_info())
    print(f"n = {SIZES}, тип данных: {KIND} (упорядоченные), диапазон [{LO}; {HI}], "
          f"k = {REPEATS}\n")

    # 1. Основной эксперимент варианта: упорядоченные данные (S)
    res_s = run_series("sorted")
    print("Таблица 1. Медианное время сортировки УПОРЯДОЧЕННЫХ массивов, мс")
    print(f"{'n':>6}{'Пузырьком':>13}{'Вставками':>13}{'Пузырёк/Вставки':>18}"
          f"{'T/n, мкс (п.)':>16}{'T/n, мкс (в.)':>16}")
    for i, n in enumerate(SIZES):
        tb, ti = res_s["Пузырьком"][i], res_s["Вставками"][i]
        print(f"{n:>6}{tb * 1e3:>13.4f}{ti * 1e3:>13.4f}{tb / ti:>18.2f}"
              f"{tb / n * 1e6:>16.4f}{ti / n * 1e6:>16.4f}")
    print("\nОтношения T(2n)/T(n) на упорядоченных данных (теория для Θ(n): 2)")
    for name, times in res_s.items():
        print(ratio_line(times, name))

    # 2. М1: сравнения и обмены на упорядоченных данных (вариант 13)
    print("\nТаблица 2 (М1). Сравнения и обмены на УПОРЯДОЧЕННЫХ данных")
    print(f"{'n':>6}{'Пузырёк: сравн.':>18}{'обмены':>9}{'Вставки: сравн.':>18}{'сдвиги':>9}")
    for n in SIZES:
        data = generate_data(n, "sorted")
        _, cb, sb = bubble_sort_counted(data)
        _, ci, si = insertion_sort_counted(data)
        print(f"{n:>6}{cb:>18}{sb:>9}{ci:>18}{si:>9}")

    # 3. М1: проверка соотношений ~ n^2/2 и ~ n^2/4 на СЛУЧАЙНЫХ данных
    print("\nТаблица 3 (М1). Сравнения и обмены на СЛУЧАЙНЫХ данных, "
          "отношение к n^2")
    print(f"{'n':>6}{'П.сравн./n²':>13}{'П.обмены/n²':>13}"
          f"{'В.сравн./n²':>13}{'В.сдвиги/n²':>13}")
    for n in SIZES:
        data = generate_data(n, "random")
        _, cb, sb = bubble_sort_counted(data)
        _, ci, si = insertion_sort_counted(data)
        print(f"{n:>6}{cb / n**2:>13.4f}{sb / n**2:>13.4f}"
              f"{ci / n**2:>13.4f}{si / n**2:>13.4f}")
    print("Теория: 0.5000 / 0.2500 / 0.2500 / 0.2500")

    # 4. Дополнение: время на случайных данных (проверка квадратичного роста)
    res_r = run_series("random")
    print("\nТаблица 4. Медианное время сортировки СЛУЧАЙНЫХ массивов, с")
    print(f"{'n':>6}{'Пузырьком':>13}{'Вставками':>13}{'Пузырёк/Вставки':>18}"
          f"{'T/n² п., нс':>14}{'T/n² в., нс':>14}")
    for i, n in enumerate(SIZES):
        tb, ti = res_r["Пузырьком"][i], res_r["Вставками"][i]
        print(f"{n:>6}{tb:>13.4f}{ti:>13.4f}{tb / ti:>18.2f}"
              f"{tb / n**2 * 1e9:>14.2f}{ti / n**2 * 1e9:>14.2f}")
    print("\nОтношения T(2n)/T(n) на случайных данных (теория для Θ(n²): 4)")
    for name, times in res_r.items():
        print(ratio_line(times, name))

    # 5. График T(n)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    for ax, res, title in [(axes[0], res_s, "Упорядоченные данные (вариант 13)"),
                           (axes[1], res_r, "Случайные данные (для сравнения)")]:
        for name, times in res.items():
            ax.plot(SIZES, times, marker="o", label=name)
        ax.set_xlabel("Размер массива n")
        ax.set_ylabel("Время, с")
        ax.set_title(title)
        ax.grid(True)
        ax.legend()
    fig.tight_layout()
    fig.savefig("lr2_plot.png", dpi=150)
    print("\nГрафик сохранён в файл lr2_plot.png")
    if "--show" in sys.argv:
        plt.show()


if __name__ == "__main__":
    main()
