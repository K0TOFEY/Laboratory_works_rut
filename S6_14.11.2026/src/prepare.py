# -*- coding: utf-8 -*-
'''Слой 2: приведение сырых данных к пригодному для анализа виду.'''
import pandas as pd

CANON_CARRIERS = {
    "транслогистик": "ТрансЛогистик",
    "рускарго": "РусКарго",
    "сибпуть": "СибПуть",
    "волгатранс": "ВолгаТранс",
    "автодорсервис": "АвтоДорСервис",
}
TARIFFS = {"Контейнер": 7.5, "Нефтепродукты": 9.2, "Зерно": 5.1,
           "Металл": 6.8, "Лес": 4.6, "Стройматериалы": 5.9}


def to_canon(value, canon_map=CANON_CARRIERS):
    '''Приводит название перевозчика к каноническому виду.'''
    s = str(value).strip().lower()
    for prefix in ('ооо "', "ооо ", 'ао "', "ао "):
        if s.startswith(prefix):
            s = s[len(prefix):]
    s = s.strip('"').strip()
    return canon_map.get(s, value)


def to_number(series):
    '''Превращает текст с десятичной запятой в число.'''
    return pd.to_numeric(
        series.astype(str)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False),
        errors="coerce",
    )


def prepare_trips(raw, max_cost_ratio=5.0):
    '''Очищает выгрузку. Возвращает (clean_df, report_dict).'''
    report = {"строк получено": len(raw)}
    df = raw.copy()

    df = df.drop_duplicates(subset=["trip_id"], keep="first")
    report["удалено дублей"] = report["строк получено"] - len(df)

    df["cost_rub"] = to_number(df["cost_rub"])
    df["weight_t"] = to_number(df["weight_t"])
    report["пропусков в весе"] = int(df["weight_t"].isna().sum())
    df["delay_h"] = pd.to_numeric(df["delay_h"], errors="coerce").fillna(0)
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce")
    report["дат не распознано"] = int(df["date"].isna().sum())

    df["carrier"] = df["carrier"].apply(to_canon)
    df["cargo_type"] = df["cargo_type"].str.strip().str.capitalize()
    report["перевозчиков после нормализации"] = int(df["carrier"].nunique())
    if int(df["carrier"].nunique()) != 5:
        known = set(CANON_CARRIERS.values())
        unknown = set(df["carrier"]) - known
        print(f"Внимание! Обнаружены незнакомые перевозчики {unknown}")

    bad_weight = df["weight_t"] <= 0
    report["удалено: нулевой вес"] = int(bad_weight.sum())
    df = df[~bad_weight]

    expected = df["weight_t"] * df["distance_km"] * df["cargo_type"].map(TARIFFS)
    bad_cost = (expected / df["cost_rub"]) > max_cost_ratio
    report["удалено: стоимость не бьётся с тарифом"] = int(bad_cost.sum())
    df = df[~bad_cost]

    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["is_delayed"] = df["delay_h"] > 0
    df["cost_per_km"] = (df["cost_rub"] / df["distance_km"]).round(2)

    report["строк осталось"] = len(df)
    report["доля потерь, %"] = round((1 - len(df) / report["строк получено"]) * 100, 1)
    return df.reset_index(drop=True), report
