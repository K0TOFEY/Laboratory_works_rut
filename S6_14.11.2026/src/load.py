# -*- coding: utf-8 -*-
'''Слой 1: загрузка сырых данных. Читает файлы как есть, ничего не исправляет.'''
from pathlib import Path

import pandas as pd


def load_trips(raw_dir, pattern="trips_*.csv"):
    '''Читает все месячные выгрузки из raw_dir и склеивает в одну таблицу.'''
    files = sorted(Path(raw_dir).glob(pattern))
    if not files:
        raise FileNotFoundError(f"в {raw_dir} нет файлов по шаблону {pattern}")

    frames = []
    for path in files:
        part = pd.read_csv(path, sep=";", encoding="cp1251")
        part["source_file"] = path.name          # помним, откуда пришла строка
        frames.append(part)
        print(f"    {path.name}: {len(part)} строк")

    return pd.concat(frames, ignore_index=True)


def load_carriers(raw_dir, filename="carriers.csv"):
    '''Читает справочник перевозчиков.'''
    return pd.read_csv(Path(raw_dir) / filename)

def load_all(raw_dir, pattern="trips_*.csv"):
    '''Загружает рейсы и справочник и возвращает их одним словарём.'''
    trips = load_trips(raw_dir, pattern=pattern)
    carriers = load_carriers(raw_dir)

    return {
        "trips": trips,
        "carriers": carriers,
    }