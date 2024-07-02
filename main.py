from fastapi import FastAPI
import time
from celery_tasks.tasks import io_bound_task, collect_results
from celery import chord

app =  FastAPI()



@app.get("/sequential")
def sequential_task():
    start_time = time.time()
    urls = ["https://httpbin.org/delay/3" for n in range(10)]
    results = []
    for url in urls:
        results.append(io_bound_task(url))
    end_time = time.time()
    return {"status": results, "time_taken": end_time - start_time}


@app.get("/sequential_celery")
def celery_task():
    start_time = time.time()
    urls = ["https://httpbin.org/delay/3" for n in range(10)]
    tasks = [io_bound_task.s(url) for url in urls]
    callback = chord(tasks)(collect_results.s(start_time))
    return {"task_id": callback.id}


@app.get("/result/{task_id}")
def get_result(task_id: str):
    task = collect_results.AsyncResult(task_id)
    if task.state == 'PENDING':
        return {"status": "Task is still in progress", "state": task.state}
    elif task.state != 'FAILURE':
        return task.result
    else:
        return {"status": "Task failed", "state": task.state, "error": str(task.info)}
