# -*- coding: utf-8 -*-
'''Все параметры анализа в одном месте.'''

# пути
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
REPORTS_DIR = "reports"
FIGURES_DIR = "reports/figures"

# какие файлы брать
TRIPS_PATTERN = "trips_*.csv"

# параметры очистки
MAX_COST_RATIO = 5.0     # во сколько раз расчётная стоимость может превышать фактическую

# параметры анализа
OTD_TARGET = 90          # целевая доля рейсов без задержки, %
ALPHA = 0.05             # порог значимости при проверке гипотез
