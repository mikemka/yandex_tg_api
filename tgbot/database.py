from config import DATABASE
from peewee import SqliteDatabase, Model, IntegerField


database = SqliteDatabase(DATABASE)


def create_tables():
    with database:
        database.create_tables([User])


class User(Model):
    user_id = IntegerField(unique=True)
    
    class Meta:
        database = database


if __name__ == '__main__':
    create_tables()
