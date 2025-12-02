# 1 Introdução:
Este projeto implementa um sistema de orquestração de tarefas distribuídas
utilizando Python, combinando:
* Multiprocessamento
* Multithreading
* Semáforos
* Escalonamento SJF (Shortest Job First)
* Balanceamento de carga baseado em capacidade
* Coleta de métricas (tempo de resposta, throughput, utilização)
## 1.1 Objetivo:
Simular um ambiente de múltiplos servidores executando requisições
concorrentes, com diferentes tempos de processamento, utilizando o algoritmo
SJF.
# 2 Arquitetura Geral do Sistema:
## 2.1 Componentes Principais:
### 2.1.1 main():
Orquestrador central: distribui jobs, controla filas e mede métricas
### 2.1.2 worker_main_process():
Processo que representa um servidor
### 2.1.3 internal_thread_task():
Thread de cada worker que executa de fato um job
### 2.1.4 Arquivo JSON de entrada
Define servidores e requisições
### 2.1.5 Filas (multiprocessing.Queue):
Comunicação entre processos
### 2.1.6 Semáforo:
Garante limite de paralelismo interno por worker
## 2.2 Fluxo de execução:
Entrada JSON → Orquestrador → Fila de Workers → Processos → Threads → Execução
do Job → Resultados → Métricas
# 3 Especificações Técnicas
## 3.1 Tecnologias Utilizadas
* Python 3.10
* multiprocessing
* threading
* queue
* json
* argparse
* Semáforos para controle de jobs simultâneos
## 3.2 Estrutura dos Arquivos:
```
Nome Principal
├── main.py
├── worker.py
├── input.json
```
# 4 Funcionamento
## 4.1 Leitura da Entrada
A função load_input() carrega:
* Lista de servidores e capacidades
* Requisições com: id, tipo, prioridade, tempo_exec, chegada
## 4.2 Inicialização dos Workers:
Para cada servidor no JSON:
* cria-se um processo (mp.Process)
* cria-se uma fila de entrada
* cria-se um conjunto de threads internas
* define-se um semáforo com a capacidade do servidor
## 4.3 Política de Escalonamento (SJF - Shortest Job First):
O orquestrador mantém uma lista de requisições pendentes e sempre envia
primeiro o job com menor tempo de execução.
```
shortest = min(pending, key=lambda j: j["tempo_exec"])
```
## 4.4 Balanceamento de Carga:
É escolhida a máquina com maior capacidade livre:
```
free_caps = [w["capacidade"] - w["carga_atual"] for w in workers]
best = max(range(len(workers)), key=lambda i: free_caps[i])
```
Se todas as máquinas estiverem cheias, o job volta para a lista pendente.
## 4.5 Execução do Job (no Worker):
Cada worker possui N threads, onde N = capacidade.
Passos:
1. Thread recebe job da fila
2. Semáforo é adquirido
3. Envia evento "start"
4. Executa sleep(tempo_exec)
5. Envia evento "finish"
6. Libera semáforo
## 4.6 Coleta de Métricas
O orquestrador calcula:
* tempo médio de resposta
* throughput = jobs / tempo total
* utilização = tempo ocupado / tempo total
* tempo máximo de espera
* quantidade de jobs completados
# 5 Como Utilizar:
No terminal:
```
python master.py --input input.json
```
# 6. Como Alterar a Entrada
Modifique o arquivo Json alterando os valores, mas sempre mantendo os nomes
das chaves, como estão listadas abaixo:
* “servidores”
* “id”
* “capacidade”
* “requisições”
* “tipo”
* “prioridade”
* “tempo_exec”
* “chegada”
#### Ao adicionar um novo servidor ou requisição, mantenha a mesma estrutura como exemplificada abaixo, adicionando o novo elemento entre os colchetes e
#### separando por vírgula:
```
"servidores": [
 {
 "id": 1,
 "capacidade": 1
 },
]
"requisicoes": [
 {
 "id": 101,
 "tipo": "visao_computacional",
 "prioridade": 1,
 "tempo_exec": 15,
 "chegada": 0
 },
```
# 7. Métricas Geradas e Significado
## 7.1 Tempo total
tempo total da simulação
## 7.2 Jobs concluídos
total de Jobs executados e finalizados
## 7.3 Tempo médio de resposta
divisão entre o tempo total de resposta pelo tempo total do processo
## 7.4 Utilização média da CPU
Porcentagem da utilização média da CPU
## 7.5 Throughput
Quantidade de Jobs concluídos pelo tempo total de simulação
## 7.6 Tempo máximo de espera
Maior diferença entre a chegada e o início daquele projeto
