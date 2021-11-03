from .db import DB
from tool.type_ import *


def get_store_item_list(db: DB) -> Optional[List]:
    cur = db.search(columns=["Name", "Score", "Quantity", "GoodsID"],
                    table="goods")
    if cur is None or cur.rowcount == 0:
        return None
    return cur.fetchall()


def get_store_item(goods_id: int, db: DB) -> Optional[List]:
    cur = db.search(columns=["Name", "Score", "Quantity", "GoodsID"],
                    table="goods",
                    where=f"GoodsID={goods_id}")
    if cur is None:
        return None
    assert cur.rowcount == 1
    return cur.fetchone()


def update_goods(goods_id: int, quantity: int, db: DB):
    cur = db.update(table="goods", kw={"Quantity": f"{quantity}"}, where=f"GoodsID={goods_id}")
    assert cur.rowcount == 1


def get_order_id(uid: uid_t, db: DB):
    cur = db.search(columns=["OrderID"],
                    table="orders",
                    where=f"UserID = '{uid}' and status=0")
    if cur is None or cur.rowcount == 0:
        cur = db.insert(table="orders", columns=["UserID"], values=f"'{uid}'")
        if cur is None:
            return None
        return cur.lastrowid
    assert cur.rowcount == 1
    return cur.fetchone()[0]


def write_goods(goods_id: int, quantity: int, order_id: int, db: DB):
    cur = db.insert(table="ordergoods",
                    columns=["OrderID", "GoodsID", "Quantity"],
                    values=f"{order_id}, {goods_id}, {quantity}")
    if cur is None:
        return False
    assert cur.rowcount == 1
    return True


def check_order(order: int, uid: uid_t, db: DB) -> bool:
    cur = db.search(columns=["OrderID"],
                    table="orders",
                    where=[f"OrderID={order}", f"UserID='{uid}'", "Status=0"])
    if cur is None or cur.rowcount == 0:
        return False
    assert cur.rowcount == 1
    cur = db.update(table="orders",
                    kw={"Status": "1"},
                    where=[f"OrderID={order}", f"UserID='{uid}'", "Status=0"])
    if cur is None:
        return False
    assert cur.rowcount == 1
    return True
