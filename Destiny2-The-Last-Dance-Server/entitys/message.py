from typing import Any, Optional


class Message:
    # 常量定义
    SUCCESS = 'success'
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'
    DATA = 'data'

    def __init__(
        self,
        status: str = SUCCESS,
        event_type: str = None,
        message: str = '',
        message_type: str = INFO,
        message_data: Optional[Any] = None,
        data: Optional[Any] = None,
        to: Optional[Any] = None
    ):
        self.event_type = event_type
        self.status = status
        self.message = message
        self.message_type = message_type
        self.message_data = message_data
        self.data = data
        self.to = to

    def to_dict(self) -> dict:
        return {
            'status': self.status,
            'eventType': self.event_type,
            'message': self.message,
            'messageType': self.message_type,
            'messageData': self.message_data,
            'data': self.data,
            'to': self.to
        }

    # 工厂方法（静态构建器）
    @classmethod
    def info(cls, message: str = 'info', data: Any = None, to: Any = None) -> "Message":
        return cls(status=cls.INFO, message=message, message_type=cls.INFO, data=data, to=to)

    @classmethod
    def success(cls, message: str = 'success', data: Any = None, to: Any = None) -> "Message":
        return cls(status=cls.SUCCESS, message=message, message_type=cls.SUCCESS, data=data, to=to)

    @classmethod
    def error(cls, message: str = 'error', data: Any = None, to: Any = None) -> "Message":
        return cls(status=cls.ERROR, message=message, message_type=cls.ERROR, data=data, to=to)

    @classmethod
    def warning(cls, message: str = 'warning', data: Any = None, to: Any = None) -> "Message":
        return cls(status=cls.WARNING, message=message, message_type=cls.WARNING, data=data, to=to)