from config import STATS_DIR
from datetime import datetime, timedelta
from matplotlib import pyplot as plt, dates as mdates
from stats_logs import load_users_log, load_downloaded_log
from pathlib import Path


def generate_users_graph_image(dt_end=datetime.now().date(), dates_count=7) -> tuple[Path | None, int]:
    if not (users_logs := load_users_log()):
        return None
    
    fig_path = STATS_DIR / f'users_{dates_count}.png'
    dt_start = dt_end - timedelta(dates_count - 1)

    delta_all = 0
    
    dates = {dt_end - timedelta(local_delta):0 for local_delta in range(dates_count - 1, -1, -1)}
    for user_log in users_logs:
        current_date = user_log['datetime'].date()
        if dt_start <= current_date <= dt_end:
            dates[current_date] += 1
            delta_all += 1
    
    plt.plot(*zip(*dates.items()), color="#ff3f21")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=90)
    plt.title(f'Прирост пользователей за {dates_count} дней')
    plt.ylabel('Зарегистрировано пользователей')
    plt.savefig(fig_path, dpi=680)
    plt.close()

    return fig_path, delta_all


def generate_downloaded_graph_image(dt_end=datetime.now().date(), dates_count=7) -> tuple[Path | None, int]:
    if not (downloaded_logs := load_downloaded_log()):
        return None
    
    fig_path = STATS_DIR / f'downloaded_{dates_count}.png'
    dt_start = dt_end - timedelta(dates_count - 1)

    delta_all = 0

    dates = {dt_end - timedelta(local_delta):0 for local_delta in range(dates_count - 1, -1, -1)}
    for downloaded_log in downloaded_logs:
        current_date = downloaded_log['datetime'].date()
        if dt_start <= current_date <= dt_end:
            dates[current_date] += 1
            delta_all += 1
    
    plt.plot(*zip(*dates.items()), color="#ff3f21")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=90)
    plt.title(f'Скачано треков за {dates_count} дней')
    plt.ylabel('Кол-во треков')
    plt.savefig(fig_path, dpi=680)
    plt.close()

    return fig_path, delta_all
