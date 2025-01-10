from enum import Enum


class BrokerQueues(str, Enum):
    GATEWAY = "gateway_queue"
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
    REGISTER = "register"
    LOGIN = "login"
    GET_CURRENT_USER = "get_current_user"
