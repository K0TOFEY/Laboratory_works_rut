"""my_stats — учебная библиотека описательных статистик."""


def mean(values):
    """Среднее арифметическое."""
    return sum(values) / len(values)


def variance(values):
    """Дисперсия."""
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / len(values)


def describe(values, name='данные'):
    """Печатает краткую сводку по данным."""
    print(f'{name}: n={len(values)}, mean={mean(values):.2f}, var={variance(values):.2f}')


if __name__ == '__main__':
    # Выполнится только при прямом запуске файла: python my_stats.py
    print('Самопроверка:', mean([1, 2, 3]))
