import requests
import time
from celery_app_worker import celery_app

@celery_app.task
def io_bound_task(url):
    response = requests.get(url)
    return response.status_code



@celery_app.task
def collect_results(results, start_time):
    end_time = time.time()
    return {"status": results, "time_taken": end_time - start_time}
