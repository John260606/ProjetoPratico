# worker_threaded_server.py
import time
import multiprocessing as mp
import threading
import queue

def ts():
    return time.strftime("[%M:%S]")

def internal_thread_task(worker_id, internal_queue, result_queue, local_semaphore):
    while True:
        item = internal_queue.get()
        if item is None:
            internal_queue.task_done()
            break
        
        # O semáforo LOCAL é adquirido/liberado aqui para limitar threads internas
        local_semaphore.acquire()
        try:
            job = item
            start = time.time()
            # Note que a result_queue principal ainda é compartilhada via Manager!
            result_queue.put({"event": "start", "job_id": job["id"], "worker_id": worker_id, "start_time": start})
            time.sleep(job["tempo_exec"])
            end = time.time()
            result_queue.put({"event": "finish", "job_id": job["id"], "worker_id": worker_id, "end_time": end})
        finally:
            local_semaphore.release()
            
        internal_queue.task_done()


def worker_main_process(worker_id: int, capacity: int, task_queue: mp.Queue, result_queue: mp.Queue):
    # Este é o ponto principal do processo
    
    internal_queue = queue.Queue() # Fila LOCAL para as threads internas
    local_semaphore = threading.Semaphore(capacity) # Semáforo LOCAL para as threads internas

    threads = []
    # Cria N threads internas com base na capacidade do servidor
    for i in range(capacity):
        t = threading.Thread(
            target=internal_thread_task,
            args=(worker_id, internal_queue, result_queue, local_semaphore),
            daemon=True
        )
        t.start()
        threads.append(t)

    # Move itens da fila de multiprocessing para a fila interna
    while True:
        item = task_queue.get()
        if item is None:
            # Sinaliza o fim para todas as threads internas
            for _ in range(capacity):
                internal_queue.put(None)
            break
        internal_queue.put(item)
    
    internal_queue.join() # Espera todas as threads internas terminarem
    print(f"Processo {worker_id} encerrado.")