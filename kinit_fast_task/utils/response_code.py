# @Version        : 1.0
# @Create Time    : 2024/5/7 17:20
# @File           : response_code.py
# @IDE            : PyCharm
# @Desc           : 常用的响应状态码（响应体 Code）


class Status:
    """
    常用的响应状态码，可自定义，自定义的前提应与前端提前对接好
    该状态码只应用于响应体中的状态码，因为该状态码是可变的

    HTTP状态码本身已经提供了关于请求是否成功以及失败的原因的信息，为什么还要在请求体中额外添加 `code` 参数？

        1. 细化错误类型：虽然HTTP状态码能够描述请求的基本状态（如200代表成功，404代表未找到等），但它们的信息量有限通过在响应体中添加`code`
            参数后端可以提供更详细的错误代码，这些错误代码可以更具体地描述问题（如数据库错误、业务逻辑错误等）这对于调试和用户反馈是非常有用的。

        2. 业务逻辑状态表示：在复杂的业务逻辑中，可能需要返回更多的状态信息，这些信息不仅仅是关于请求成功或失败的。例如，一个操作可能部分成功，
            或者有特定的警告信息需要传达。`code`参数可以用来传递这些特定的业务逻辑相关的状态信息。

        3. 前后端分离：在现代的应用开发中，前后端分离是一种常见的架构模式。在这种模式中，前端应用往往需要根据不同的业务代码执行不同的逻辑处理。
            包含具体业务相关的`code`可以让前端开发者更精确地控制用户界面的反应。

        4. 国际化和本地化：HTTP状态码的描述通常是标准化且不变的。通过在响应体中包含`message`字段，可以提供本地化的错误信息，这有助于提升用户
            体验，特别是在多语言应用中。

        5. 向后兼容性：在现有系统中引入新的错误类型或状态码时，使用HTTP状态码可能需要大的变动或可能影响到旧版本客户端的处理逻辑。使用`code`和
            `message`提供额外的上下文可以在不影响旧版本客户端的情况下，增加新的逻辑。

    HTTP 状态码大全：https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status
    """  # noqa E501

    HTTP_SUCCESS = 200  # OK 请求成功
    HTTP_ERROR = 400  # BAD_REQUEST 因客户端错误的原因请求失败
    HTTP_401 = 401  # UNAUTHORIZED: 未授权
    HTTP_403 = 403  # FORBIDDEN: 禁止访问
    HTTP_404 = 404  # NOT_FOUND: 未找到
    HTTP_405 = 405  # METHOD_NOT_ALLOWED: 方法不允许
    HTTP_408 = 408  # REQUEST_TIMEOUT: 请求超时
    HTTP_500 = 500  # INTERNAL_SERVER_ERROR: 服务器内部错误
    HTTP_502 = 502  # BAD_GATEWAY: 错误的网关
    HTTP_503 = 503  # SERVICE_UNAVAILABLE: 服务不可用
