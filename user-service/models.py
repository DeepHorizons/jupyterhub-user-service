import os
import peewee
import peewee_async

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_IP = os.environ.get('DB_IP', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', 5432)

database = peewee_async.PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_IP, port=DB_PORT)


class BaseModel(peewee.Model):
    """Base class for peewee so it can manage the database connection for us"""

    class Meta:
        database = database

    # These must match the name of the input on the spawner, and the <input> fields
    nprocs = peewee.IntegerField(default=1)  # How many CPUs
    memory = peewee.IntegerField(default=1)  # How much memory can they use?
    runtime = peewee.IntegerField(default=1)  # Maximum runtime
    gpu = peewee.BooleanField(default=False)  # Should they have a GPU?


class User(BaseModel):
    """Represents a docker image"""
    # What is the username?
    username = peewee.CharField(unique=True)


class Group(BaseModel):
    """Represents a docker image"""
    # What is the group name?
    groupname = peewee.CharField(unique=True)


database.create_tables([User, Group], safe=True)
database.close()
objects = peewee_async.Manager(database)
database.set_allow_sync(False)
