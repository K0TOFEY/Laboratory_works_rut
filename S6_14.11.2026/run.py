# -*- coding: utf-8 -*-
'''Точка входа: запускает весь анализ от сырых данных до отчёта.'''
import json
from datetime import datetime
from pathlib import Path

import config
from src.load import load_trips, load_carriers
from src.prepare import prepare_trips
from src.analyze import overall_kpi, kpi_by, worst_and_best_carrier
from src.visualize import plot_revenue_by_month, plot_otd_by_carrier


def df_to_markdown(df):
    '''Превращает таблицу в markdown без внешних зависимостей.'''
    header = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep = "|" + "---|" * len(df.columns)
    rows = ["| " + " | ".join(str(v) for v in row) + " |"
            for row in df.itertuples(index=False)]
    return chr(10).join([header, sep] + rows)


def build_report(kpi, quality, by_carrier, test, figures):
    '''Собирает текстовый отчёт в формате Markdown.'''
    lines = ["# Отчёт по перевозкам", ""]
    lines.append("Сформирован: " + datetime.now().strftime("%d.%m.%Y %H:%M"))

    lines += ["", "## Ключевые показатели", ""]
    for k, v in kpi.items():
        lines.append(f"- **{k}**: {v}")

    lines += ["", "## Качество данных", ""]
    for k, v in quality.items():
        lines.append(f"- {k}: {v}")

    lines += ["", "## По перевозчикам", "", df_to_markdown(by_carrier)]

    verdict = "различие значимо" if test["значимо"] else "различий не обнаружено"
    lines += ["", "## Проверка гипотезы", "",
              f"Сравнение OTD: {test['группа A']} против {test['группа B']} — "
              f"{verdict} (p = {test['p']})."]

    lines += ["", "## Графики", ""]
    for path in figures:
        lines.append(f"![{Path(path).stem}]({Path(path).as_posix()})")

    return chr(10).join(lines)


def main():
    started = datetime.now()
    print("=" * 56)
    print("ЗАПУСК PIPELINE", started.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 56)

    for folder in (config.PROCESSED_DIR, config.FIGURES_DIR):
        Path(folder).mkdir(parents=True, exist_ok=True)

    print("[1/5] загрузка")
    raw = load_trips(config.RAW_DIR, config.TRIPS_PATTERN)
    carriers = load_carriers(config.RAW_DIR)

    print("[2/5] подготовка")
    clean, quality = prepare_trips(raw, max_cost_ratio=config.MAX_COST_RATIO)
    clean_path = Path(config.PROCESSED_DIR) / "trips_clean.csv"
    clean.to_csv(clean_path, index=False, encoding="utf-8")
    print(f"    сохранено: {clean_path} ({len(clean)} строк)")

    print("[3/5] расчёт метрик")
    kpi = overall_kpi(clean)
    by_carrier = kpi_by(clean, "carrier")
    by_month = kpi_by(clean, "month")
    test = worst_and_best_carrier(clean, alpha=config.ALPHA)
    by_carrier.to_csv(Path(config.PROCESSED_DIR) / "kpi_by_carrier.csv",
                      index=False, encoding="utf-8")
    by_month.to_csv(Path(config.PROCESSED_DIR) / "kpi_by_month.csv",
                    index=False, encoding="utf-8")

    print("[4/5] графики")
    fig1 = plot_revenue_by_month(by_month, config.FIGURES_DIR)
    fig2 = plot_otd_by_carrier(by_carrier, config.FIGURES_DIR, target=config.OTD_TARGET)
    print(f"    {fig1}")
    print(f"    {fig2}")

    print("[5/5] отчёт")
    report_path = Path(config.REPORTS_DIR) / "report.md"
    report_path.write_text(build_report(kpi, quality, by_carrier, test, [fig1, fig2]),
                           encoding="utf-8")

    manifest = {
        "запуск": started.isoformat(timespec="seconds"),
        "длительность, с": round((datetime.now() - started).total_seconds(), 2),
        "параметры": {"MAX_COST_RATIO": config.MAX_COST_RATIO,
                      "OTD_TARGET": config.OTD_TARGET,
                      "TRIPS_PATTERN": config.TRIPS_PATTERN},
        "качество данных": quality,
        "итоговые метрики": kpi,
    }
    manifest_path = Path(config.PROCESSED_DIR) / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                             encoding="utf-8")

    print(f"    {report_path}")
    print(f"    {manifest_path}")
    print("ГОТОВО")
    return manifest


if __name__ == "__main__":
    main()
