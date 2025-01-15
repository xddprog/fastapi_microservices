from enum import Enum


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


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


class TaskServiceRoutes(str, Enum):
    CREATE = "create_task"
    GET_USER_TASKS = "get_user_tasks"
    GET = "get_task"
    UPDATE = "update_task"
    DELETE = "delete_task"