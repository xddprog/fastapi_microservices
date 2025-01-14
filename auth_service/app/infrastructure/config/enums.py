from enum import Enum


class TokenTypes(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    

class BrokerQueues(str, Enum):
    AUTH = "auth_queue"
    TASKS = "tasks_queue"
    USERS = "users_queue"
    GATEWAY = "gateway_queue"


class UserServiceRoutes(str, Enum):
    CREATE = "create_user"
    GET_ALL = "get_all_users"
    GET = "get_user"
    UPDATE = "update_user"
    DELETE = "delete_user"
    CHECK_USER_EXIST = "check_user_exist"



class AuthServiceRoutes(str, Enum):
    REGISTER = "register"
    LOGIN = "login"
    GET_CURRENT_USER = "get_current_user"
    REFRESH = "refresh"
    LOGOUT = "logout"