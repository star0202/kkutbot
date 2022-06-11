import asyncio

from tools.db import db


async def main():
    await db.user.update_many({}, {
        "$rename": {
            "_name": "name",
            "register_date": "registered",
            "info_word": "info",
            "last_vote": "latest_reward",
            "daily_times": "attendance_times",
            "daily": "attendance",
            "last_command": "latest_usage",
            "mail": "mails",
            "alert.daily": "alert.attendance",
            "alert.heart": "alert.reward",
            "alert.mail": "alert.mails",
            "alert": "alerts",
            "game.rank_multi": "game.rank_online",
            "game.apmal": "game.long"
        },
        "$set": {
            "attendance": {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0},
            "announcements": {},
            "alert.announcements": True,
            "banned": {"isbanned": False, "since": 0, "period": 0, "reason": None}
        },
        "$unset": {
            "alerts.start_point": 1
        }
    })
    for user in await (db.user.find()).to_list(None):
        await db.user.update_one({"_id": user["_id"]}, {"$set": {"registered": round(user["registered"].timestamp())}})

    await db.unused.update_many({}, {
        "$rename": {
            "_name": "name",
            "register_date": "registered",
            "info_word": "info",
            "last_vote": "latest_reward",
            "daily_times": "attendance_times",
            "daily": "attendance",
            "last_command": "latest_usage",
            "mail": "mails",
            "alert.daily": "alert.attendance",
            "alert.heart": "alert.reward",
            "alert.mail": "alert.mails",
            "alert": "alerts",
            "game.rank_multi": "game.rank_online",
            "game.apmal": "game.long"
        },
        "$set": {
            "attendance": {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0},
            "announcements": {},
            "alert.announcements": True,
            "banned": {"isbanned": False, "since": 0, "period": 0, "reason": None}
        },
        "$unset": {
            "alerts.start_point": 1
        }
    })
    for user in await (db.unused.find()).to_list(None):
        await db.unused.update_one({"_id": user["_id"]}, {"$set": {"registered": round(user["registered"].timestamp())}})

    await db.guild.update_many({}, {
        "$rename": {
            "last_command": "latest_usage"
        }
    })

    await db.general.update_one({"_id": "general"}, {
        "$rename": {
            "daily": "attendance",
            "last_command": "latest_usage",
            "quest": "quests"
        },
        "$set": {
            "reward": 0,
            "announcements": []
        }
    })


asyncio.get_event_loop().run_until_complete(main())
