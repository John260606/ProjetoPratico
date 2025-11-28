# master_semaphore.py
import multiprocessing as mp
import json
import time
import argparse

from worker import worker_main_process as worker_process


def timestamp():
    return time.strftime("[%M:%S]")

def load_input(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_best_worker_load(workers):
    free_caps = [w["capacidade"] - w["carga_atual"] for w in workers]
    best = max(range(len(workers)), key=lambda i: free_caps[i])
    if free_caps[best] <= 0:
        return None
    return best

def main(input_path):
    data = load_input(input_path)
    servers = data.get("servidores", [])
    requisicoes = data.get("requisicoes", [])

    manager = mp.Manager()
    worker_queues = []
    workers_meta = []
    result_queue = manager.Queue()

    processes = []
    for s in servers:
        q = manager.Queue()
        worker_queues.append(q)
        workers_meta.append({ "id": s["id"], "capacidade": s["capacidade"], "carga_atual": 0, "jobs_em_execucao": [] })
        p = mp.Process(target=worker_process,
                       args=(s["id"], s["capacidade"], q, result_queue)) 
        p.start()
        processes.append(p)
    

    worker_busy_time = {s["id"]: 0.0 for s in servers}
    worker_last_start = {s["id"]: None for s in servers}
    pending = []
    metrics = {"jobs_total": 0, "completed": 0, "sum_response_time": 0.0, "max_wait": 0.0,}
    job_start_times = {}
    arrivals = sorted(requisicoes, key=lambda r: r.get("chegada", 0))
    arrival_i = 0
    start_sim = time.time()
    now = lambda: time.time()
    print(timestamp(), "Simulação iniciada - política: SJF (Semaphore)")
    sim_time0 = start_sim

    while True:
        t = now() - sim_time0
        while arrival_i < len(arrivals) and arrivals[arrival_i]["chegada"] <= t:
            job = arrivals[arrival_i].copy()
            job["chegada"] = now()
            pending.append(job)
            metrics["jobs_total"] += 1
            print(timestamp(), f"Chegou Requisição {job['id']} (exec={job['tempo_exec']}s)", flush=True)
            arrival_i += 1
        while pending:
            shortest = min(pending, key=lambda j: j["tempo_exec"])
            pending.remove(shortest)
            worker_idx = find_best_worker_load(workers_meta)
            if worker_idx is None:
                pending.append(shortest)
                break
            workers_meta[worker_idx]["carga_atual"] += 1
            workers_meta[worker_idx]["jobs_em_execucao"].append(shortest)
            job_start_times[shortest["id"]] = now()
            worker_queues[worker_idx].put(shortest)
            print(timestamp(), f"Job {shortest['id']} → Servidor {workers_meta[worker_idx]['id']}", flush=True)

        while not result_queue.empty():
            msg = result_queue.get()
           
            if msg["event"] == "start":
                jid = msg["job_id"];wid = msg["worker_id"]
                st = msg.get("start_time", now())
                worker_last_start[wid] = st; job_start_times[jid] = st
                continue
            
            if msg["event"] == "finish":
                jid = msg["job_id"]; 
                wid = msg["worker_id"]; 
                end = msg["end_time"]

                if worker_last_start[wid] is not None:
                    worker_busy_time[wid] += end - worker_last_start[wid]
                    worker_last_start[wid] = None

                idx = next(i for i, w in enumerate(workers_meta) if w["id"] == wid)

                workers_meta[idx]["carga_atual"] -= 1

                workers_meta[idx]["jobs_em_execucao"] = [j for j in workers_meta[idx]["jobs_em_execucao"] if j["id"] != jid]


                start_time = job_start_times.get(jid, msg.get("start_time", now()))
                chegada = msg.get("chegada", None)
                response_time = msg["end_time"] - chegada if chegada is not None else msg["end_time"] - start_time
                metrics["completed"] += 1
                metrics["sum_response_time"] += response_time
                metrics["max_wait"] = max(metrics["max_wait"], (start_time - chegada if chegada is not None else 0.0))
                print(timestamp(), f"Servidor {wid} concluiu Job {jid} (resp={response_time:.2f}s)", flush=True)

        done = (arrival_i >= len(arrivals) and not pending and all(w["carga_atual"] == 0 for w in workers_meta))
        if done:
            break
        time.sleep(0.01)


    for q in worker_queues:
        q.put(None)
    for p in processes:
        p.join(timeout=1)

    total = metrics["completed"] or 1
    avg_response = metrics["sum_response_time"] / total
    elapsed = now() - start_sim
    throughput = metrics["completed"] / elapsed
    util_media = sum(worker_busy_time.values()) / (elapsed * len(worker_busy_time))

    print("\n---------------- RESUMO FINAL (SJF Semaphore) ----------------")
    print(f"Tempo total: {elapsed:.2f}s")
    print(f"Jobs concluídos: {metrics['completed']}")
    print(f"Tempo médio de resposta: {avg_response:.2f}s")
    print(f"Utilização média da CPU: {util_media * 100:.2f}%")
    print(f"Throughput: {throughput:.2f} jobs/s")
    print(f"Tempo máximo de espera: {metrics['max_wait']:.2f}s")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador Orquestrador SJF Semaphore")
    parser.add_argument("--input", "-i", default="input.json", help="Arquivo JSON de entrada")
    args = parser.parse_args()
    main(args.input)
