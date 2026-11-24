# -*- coding: utf-8 -*-
'''Слой 4: построение графиков по готовым метрикам.'''
from pathlib import Path

import matplotlib
matplotlib.use("Agg")      # рисуем в файл, без окна: нужно для запуска из терминала
import matplotlib.pyplot as plt


def plot_revenue_by_month(metrics, out_dir):
    '''Динамика выручки по месяцам.'''
    data = metrics.sort_values("month")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(data["month"], data["revenue"] / 1_000_000, marker="o", linewidth=2.5)
    ax.set_title("Выручка по месяцам")
    ax.set_xlabel("Месяц")
    ax.set_ylabel("Выручка, млн руб.")
    ax.set_ylim(0, (data["revenue"].max() / 1_000_000) * 1.2)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    path = Path(out_dir) / "revenue_by_month.png"
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_otd_by_carrier(metrics, out_dir, target=90):
    '''OTD по перевозчикам с линией целевого значения.'''
    data = metrics.sort_values("otd")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#C44E52" if v < target else "#55A868" for v in data["otd"]]
    ax.barh(data["carrier"], data["otd"], color=colors)
    ax.axvline(target, color="black", linestyle="--", linewidth=1.5,
               label=f"цель: {target}%")
    ax.set_title("Доля рейсов без задержки (OTD)")
    ax.set_xlabel("OTD, %")
    ax.set_xlim(0, 100)
    ax.legend()
    fig.tight_layout()

    path = Path(out_dir) / "otd_by_carrier.png"
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path
