
from enum import Enum


class BrokerQueues(str, Enum):
    AUTH = "auth_queue"
    TASKS = "tasks_queue"
    USERS = "users_queue"


class UserServiceRoutes(str, Enum):
    CREATE = "create_user"
    GET = "get_user"
    UPDATE = "update_user"
    CHECK_USER_EXIST = "check_user_exist"


class AuthServiceRoutes(str, Enum):
    CREATE_ACCESS_TOKEN = "create_access_token"