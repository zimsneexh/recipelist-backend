import sqlite3
import os

import blog

DB_FILE="rating.db"

def init_setup():
    CONNECTION = sqlite3.connect(DB_FILE)
    
    # TODO: Maybe add (ratingtext?)
    cur = CONNECTION.cursor()
    try:
        cur.execute("CREATE TABLE rating(id, author, rating, UNIQUE(id, author))")
    except sqlite3.OperationalError:
        pass

#
# True on success, False on failure
# 
def add_rating(oid, author, rating):
    CONNECTION = sqlite3.connect(DB_FILE)
    cur = CONNECTION.cursor()

    try:
        rating = int(rating)
    except ValueError:
        return False

    data = (oid, author, rating)

    try:
        cur.execute("INSERT INTO rating VALUES(?, ?, ?)", data)
    except sqlite3.IntegrityError:
        return False

    CONNECTION.commit()
    return True

#
# Average rating by ODH ID
#
def get_avg_by_id(oid):
    CONNECTION = sqlite3.connect(DB_FILE)
    cur = CONNECTION.cursor()
    res = cur.execute("SELECT AVG(rating) FROM rating WHERE id = ?", (oid,))
    avg = res.fetchone()

    if(avg == (None,)):
        avg = 0
    else:
        avg = avg[0]

    return avg


#
# get all ratings by id
#
def get_all_ratings_by_id(oid):
    CONNECTION = sqlite3.connect(DB_FILE)
    cur = CONNECTION.cursor()
    res = cur.execute("SELECT author, rating FROM rating WHERE id = ?", (oid,))
   
    result = res.fetchall()

    _dict = { }

    for res in result:
        key, val = res
        _dict[key] = val
    
    return _dict
