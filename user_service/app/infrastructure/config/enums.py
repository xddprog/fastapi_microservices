
from enum import Enum


class BrokerQueues(str, Enum):
    AUTH = "auth_queue"
    TASKS = "tasks_queue"
    USERS = "users_queue"


class UserServiceRoutes(str, Enum):
    CREATE = "create_user"
    GET_ALL = "get_all_users"
    GET = "get_user"
    UPDATE = "update_user"
    DELETE = "delete_user"


class AuthServiceRoutes(str, Enum):
    CREATE_ACCESS_TOKEN = "create_access_token"