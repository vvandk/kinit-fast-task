如果你想在 FastAPI 中使用 `BackgroundTasks` 而不通过依赖注入的方式，你可以直接在函数中创建 `BackgroundTasks` 实例并在返回的响应中明确地将其作为参数传递。这允许你在响应对象中手动管理后台任务，而不是依赖 FastAPI 的自动注入机制。

下面是如何在 FastAPI 路由函数中手动创建 `BackgroundTasks` 实例并确保任务执行的示例：

### 示例代码

```python
from fastapi import FastAPI, BackgroundTasks, Response

app = FastAPI()

def write_log():
    print("Log message: Background task is running")

@app.post("/tasks/")
async def run_background_task():
    tasks = BackgroundTasks()
    tasks.add_task(write_log)
    # 返回响应时，手动传递 BackgroundTasks 实例
    return Response(content="Background task has been added", background=tasks)
```

### 代码解释

1. **创建 `BackgroundTasks` 实例**：在函数 `run_background_task` 中，我们创建了一个 `BackgroundTasks` 对象的实例 `tasks`。

2. **添加任务**：通过调用 `tasks.add_task(write_log)`，我们把 `write_log` 函数作为后台任务添加到了 `tasks` 实例中。

3. **手动传递 BackgroundTasks 实例**：在返回响应时，我们使用 `Response` 对象，并通过 `background` 参数将 `BackgroundTasks` 实例传递进去。这样 FastAPI 就会在完成 HTTP 响应后执行指定的后台任务。

### 注意

这种方法不使用依赖注入，而是直接操作 `BackgroundTasks` 对象，并确保它与响应对象关联，从而让 FastAPI 能够正确地处理后台任务。这样做提供了对后台任务管理的完全控制，同时仍然利用 FastAPI 的内置支持来确保任务在适当的时机执行。

使用这种方法时，你需要确保正确地将 `BackgroundTasks` 实例与响应对象关联，否则后台任务不会执行。通过 `Response` 对象的 `background` 参数传递后台任务是一种确保 FastAPI 正确管理并执行这些任务的有效方式。