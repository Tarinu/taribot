"""
Schedule module
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""CREATE TABLE schedule (
        id integer primary key autoincrement,
        user_id integer not null,
        command varchar(100) not null,
        interval integer not null
    )""", "DROP TABLE schedule"),
    step("CREATE UNIQUE INDEX IF NOT EXISTS unique_user_id ON schedule (user_id)")
]
