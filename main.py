import argparse
import asyncio
import os
import sys
import time
import requests
from datetime import datetime

import genshin
import schedule
from genshin import Game
from rich.console import Console
from rich.table import Table

console = Console()


def check_language(language: str) -> str:
    valid = {
        "zh-cn",
        "zh-tw",
        "de-de",
        "en-us",
        "es-es",
        "fr-fr",
        "id-id",
        "ja-jp",
        "ko-kr",
        "pt-pt",
        "ru-ru",
        "th-th",
        "vi-vn",
    }

    language = language.lower()
    if language not in valid:
        console.log(
            f"'{ language }': not a valid language. Using default language -> 'en-us'."
        )
        language = "en-us"
    return language


def censor_uid(uid: int) -> str:
    uid = str(uid)
    uid = uid[:2] + "■■■■■■" + uid[-1]
    return uid


async def get_daily_reward(
    ltuid: str, ltoken: str, lang: str = "en-us", env_name: str = ""
) -> dict[str, str]:

    client = genshin.Client(lang=lang, game=Game.GENSHIN)
    client.set_cookies(ltuid=ltuid, ltoken=ltoken)

    info = dict(
        uid="❓",
        level="❓",
        name="❓",
        server="❓",
        status="❌ Failed",
        check_in_count="❓",
        reward="❓",
    )

    try:
        await client.claim_daily_reward(reward=False)
    except genshin.InvalidCookies:
        console.log(
            f"{env_name}: Invalid cookie information. Please check ltuid and ltoken.")
        return info
    except genshin.AlreadyClaimed:
        info["status"] = "🟡 Already check in"
    else:
        info["status"] = "✅ Check in success"

    accounts = await client.get_game_accounts()

    # Use only the account information of the region with the highest level in the Wonshin account
    account = max(
        (acc for acc in accounts if acc.game == Game.GENSHIN), key=lambda acc: acc.level
    )
    _, day = await client.get_reward_info()
    rewards = await client.get_monthly_rewards()
    reward = rewards[day - 1]

    info["uid"] = censor_uid(account.uid)
    info["level"] = str(account.level)
    info["name"] = account.nickname
    info["server"] = account.server_name.rsplit(maxsplit=1)[0]
    info["check_in_count"] = str(day)
    info["reward"] = f"{reward.name} x{reward.amount}"

    return info


async def get_all_reward(
    info: list[tuple[str, str, str]], lang: str
) -> tuple[dict[str, str]]:

    funcs = (
        get_daily_reward(ltuid, ltoken, lang, env_name)
        for env_name, ltuid, ltoken in info
    )

    results = await asyncio.gather(*funcs)

    return results


def init_table() -> Table:
    now = datetime.strftime(datetime.now(), "%Y-%m-%d %I:%M:%S %p")
    table = Table(title=now, title_style="bold", header_style="bold")

    table.add_column("UID", justify="center", style="dim")
    table.add_column("Nickname", justify="center")
    table.add_column("Level", justify="center")
    table.add_column("Server", justify="center")
    table.add_column("Day", justify="center")
    table.add_column("Status", justify="right")
    table.add_column("Reward", justify="right", style="green")

    return table


def get_cookie_info_in_env() -> list[tuple[str, str, str]]:
    info = []
    for name, value in os.environ.items():
        if name.startswith("ACCOUNT") and "," in value:
            ltuid, ltoken = map(str.strip, value.split(",", maxsplit=1))
            info.append((name, ltuid, ltoken))
    info.sort()
    return info


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--once", action="store_true", help="Run only once")
    parser.add_argument("-t", "--tele", action="store_true", help="Send message to Telegram")
    args = parser.parse_args()
    return args


def solve_asyncio_windows_error() -> None:
    "https://github.com/encode/httpx/issues/914#issuecomment-622586610"
    if (
        sys.version_info[0] == 3
        and sys.version_info[1] >= 8
        and sys.platform.startswith("win")
    ):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def send_telegram(message):
    api_telegram = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
    requests.get(api_telegram, params={"chat_id": os.getenv('TELEGRAM_TO'), "text": message})


def main() -> None:
    cookies = get_cookie_info_in_env()

    language = os.getenv("LANGUAGE", "en-us")
    language = check_language(language)
    results = asyncio.run(get_all_reward(cookies, language))

    table = init_table()

    for info in results:
        message = f"UID: {info['uid']}\nNickname: {info['name']}\nLevel: {info['level']}\nServer: {info['server']}\nDay: {info['check_in_count']}\nStatus: {info['status']}\nReward: {info['reward']}\n"

        if args.tele:
            send_telegram(message)

        table.add_row(
            info["uid"],
            info["name"],
            info["level"],
            info["server"],
            info["check_in_count"],
            info["status"],
            info["reward"],
        )

    console.print(table)


if __name__ == "__main__":
    solve_asyncio_windows_error()
    args = parse_args()

    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ModuleNotFoundError:
        pass

    if args.once:
        main()
        sys.exit()

    TIME = os.getenv("TIME", "00:00")
    try:
        schedule.every().day.at(TIME).do(main)
    except schedule.ScheduleValueError:
        m = f"'{TIME}' is an invalid time format. Please enter the TIME as HH:MM(:SS)."
        console.log(m)
        console.log("The app has been terminated.")
        sys.exit(1)

    console.log("The app has been launched.")

    while True:
        schedule.run_pending()
        time.sleep(1)
