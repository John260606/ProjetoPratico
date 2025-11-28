# worker_threaded_server.py
import time
import multiprocessing as mp
import threading
import queue

def ts():
    return time.strftime("[%M:%S]")

def internal_thread_task(worker_id, task_queue, result_queue, local_semaphore):
    while True:
        item = task_queue.get()
        if item is None:
            task_queue.task_done()
            break
        
        local_semaphore.acquire()
        job = item
        start = time.time()
        result_queue.put({"event": "start", "job_id": job["id"], "worker_id": worker_id, "start_time": start})
        time.sleep(job["tempo_exec"])
        end = time.time()
        result_queue.put({"chegada":job.get("chegada", None),
                           "event": "finish", "job_id": job["id"],
                             "worker_id": worker_id, "end_time": end,
                               "tempo_exec": job["tempo_exec"],
                                 "prioridade": job.get("prioridade", None),
                                   "tipo": job.get("tipo", None)})
        local_semaphore.release()
            
        task_queue.task_done()


def worker_main_process(worker_id: int, capacity: int, task_queue: mp.Queue, result_queue: mp.Queue):

    local_semaphore = threading.Semaphore(capacity)

    threads = []
    for i in range(capacity):
        t = threading.Thread(
            target=internal_thread_task,
            args=(worker_id, task_queue, result_queue, local_semaphore),
            daemon=True
        )
        t.start()
        threads.append(t)    
    task_queue.join() 
    for t in threads:
        t.join()
    print(f"Processo {worker_id} encerrado.")