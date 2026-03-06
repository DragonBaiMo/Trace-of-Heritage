"""自定义业务异常定义。"""


class BusinessException(Exception):
    """用于标识可预期的业务错误。"""

    def __init__(self, message: str, code: int = 40001) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
