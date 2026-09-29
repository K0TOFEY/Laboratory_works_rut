# Решение задания 7

def load_data():
    return [3, 17, 8, 25, 6, 12, 25, 9, 14]

def filter_above(values, threshold=10):
    for el in values:
        if el > threshold:
            pass
        else:
            values.remove(el)
    return values

def mean(values):
    return sum(values) / len(values)

if __name__ == '__main__':
    print("Аброкадабра")
