# worker.py
import time
import multiprocessing as mp

def ts():
    return time.strftime("[%M:%S]")

def worker_process(worker_id: int, capacity: int, task_queue: mp.Queue, result_queue: mp.Queue):

    while True:
        item = task_queue.get()
        if item is None:
            break

        job = item
        start = time.time()

        result_queue.put({
            "event": "start",
            "job_id": job["id"],
            "worker_id": worker_id,
            "start_time": start
        })


        time.sleep(job["tempo_exec"])


        end = time.time()
        result_queue.put({
            "event": "finish",
            "job_id": job["id"],
            "worker_id": worker_id,
            "start_time": start,
            "end_time": end,
            "tempo_exec": job["tempo_exec"],
            "chegada": job.get("chegada", None),
            "prioridade": job.get("prioridade", None),
            "tipo": job.get("tipo", None)
        })


