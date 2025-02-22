import logging
import time
from copy import deepcopy
from typing import Any, Optional, Union
from typing_extensions import TypeAlias

import discord
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection  # noqa

from config import config, get_nested_dict

__all__ = ["db", "read", "write", "add", "delete", "append"]

logger = logging.getLogger("kkutbot")
MODE = "test" if config("test") else "main"

TargetObject: TypeAlias = Union[discord.User, discord.Member, discord.ClientUser, discord.Guild, None, int, str]


def dbconfig(query: str) -> Any:
    """
    gets about db configuration value in 'config.yml' file
    Parameters
    ----------
    query : str
    Returns
    -------
    Any
        value about db configuration in 'config.yml' file
    """
    return config(f"mongo.{MODE}.{query}")


db_options = {}

if all([username := dbconfig("user"), password := dbconfig("password")]):
    db_options["username"] = username
    db_options["password"] = password
    db_options["authSource"] = "admin"

_client = AsyncIOMotorClient(host=dbconfig("ip"), port=dbconfig("port"), **db_options)

logger.info("mongoDB에 연결됨")


db = _client[dbconfig("db")]


def get_collection(target: TargetObject) -> AsyncIOMotorCollection:
    """
    returns collection name

    Arguments
    ---------
    target: TargetObject
        target object to get collection

    Returns
    -------
    AsyncIOMotorCollection
        target's collection
    """
    if isinstance(target, (discord.User, discord.Member, discord.ClientUser, int)):
        return db.user
    elif isinstance(target, discord.Guild):
        return db.guild
    else:
        return db.general


def _get_id(target: TargetObject) -> Union[int, str]:
    """
    returns target id

    Arguments
    ---------
    target: TargetObject
        target object to get id

    Returns
    -------
    int
        target's id
    """
    if target:
        return getattr(target, "id", target)  # type: ignore
    else:
        return "general"


def _get_name(target: TargetObject) -> Optional[str]:
    """
    returns target name

    Arguments
    ---------
    target: TargetObject
        target object to get name

    Returns
    -------
    int
        target's name
    """
    return getattr(target, "name", None)


async def read(target: TargetObject, path: Optional[str] = None) -> Any:
    """
    reads target info

    Arguments
    ---------
    target: TargetObject
        target id to read info
    path: Optional[str]
        data path in nested dictionary

    Returns
    -------
    Any
        target's info
    """
    if target:
        collection = get_collection(target)
        main_data: dict[Any, Any] = await collection.find_one({"_id": _get_id(target)})
        if not main_data:
            if collection.name == "user":
                main_data = deepcopy(config("default_data.user"))
            elif collection.name == "guild":
                main_data = deepcopy(config("default_data.guild"))
            else:
                raise ValueError
    else:
        main_data = await db.general.find_one({"_id": "general"})
        if not main_data:
            main_data = deepcopy(config("default_data.general"))

    if path is None:
        return main_data

    return get_nested_dict(main_data, path.split("."))


async def write(target: TargetObject, path: str, value: Any) -> None:
    """
    writes value to target

    Arguments
    ---------
    target: TargetObject
        target id to read info
    path: str
        data path in nested dictionary
    value
        value to write into DB
    """
    collection = get_collection(target)
    id_ = _get_id(target)
    name = _get_name(target)

    if collection.name == "user":
        if not (await read(target, "registered")):
            if data := await db.unused.find_one({"_id": id_}):
                await db.user.insert_one(data)
                await db.unused.delete_one({"_id": id_})
            else:
                main_data = await read(target)
                main_data["registered"] = round(time.time())
                main_data["_id"] = id_
                main_data["name"] = name
                await db.user.insert_one(main_data)
        if name and name != (await read(target, "name")):
            await db.user.update_one({"_id": id_}, {"$set": {"name": name}})
    elif (collection.name == "guild") and ((main_data := await read(target)) == deepcopy(config("default_data.guild"))):
        main_data["_id"] = id_
        await db.guild.insert_one(main_data)
    elif (collection.name == "general") and ((main_data := await read(target)) == deepcopy(config("default_data.general"))):
        main_data["_id"] = "general"
        await db.general.insert_one(main_data)

    await collection.update_one({"_id": id_}, {"$set": {path: value}})


async def add(target: TargetObject, path: str, value: int) -> None:
    """
    adds value to target data

    Arguments
    ---------
    target: TargetObject
        target id to add value
    path: str
        data path in nested dictionary
    value
        value to add to DB
    """
    data_before = (await read(target, path)) or 0
    await write(target, path, data_before + value)


async def delete(target: TargetObject) -> None:
    """
    deletes target data in DB

    Arguments
    ---------
    target: TargetObject
        target id to delete info
    """
    collection = get_collection(target)
    await collection.delete_one({"_id": _get_id(target)})


async def append(target: TargetObject, path: str, value: Any) -> None:
    """
    appends value to target data(list)

    Arguments
    ---------
    target: TargetObject
        target id to delete info
    path: str
        data path in nested dictionary
    value
        value to append to DB
    """
    collection = get_collection(target)
    await collection.update_one({"_id": _get_id(target)}, {"$push": {path: value}})
