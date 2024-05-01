import os
import subprocess
from multiprocessing import Process


COMMANDS = [
    f"python3 -m llava.serve.controller"
    f" --port {os.getenv('CONTROLLER_PORT')}"
    f" --host 0.0.0.0",
    
    f"python3 -m llava.serve.model_worker"
    f" --host 0.0.0.0"
    f" --controller http://localhost:{os.getenv('CONTROLLER_PORT')}"
    f" --port {os.getenv('MAIN_WORKER_PORT')}"
    f" --worker http://0.0.0.0:{os.getenv('MAIN_WORKER_PORT')}"
    f" --model-path {os.getenv('MODEL_NAME')}"
    f" --load-4bit",

    f"python3 -m llava.serve.model_worker"
    f" --host 0.0.0.0"
    f" --controller http://localhost:{os.getenv('CONTROLLER_PORT')}"
    f" --port {os.getenv('ADD_WORKER_PORT')}"
    f" --worker http://0.0.0.0:{os.getenv('ADD_WORKER_PORT')}"
    f" --model-path {os.getenv('MODEL_NAME')}"
    f" --load-4bit",
]


def launch_llava_process(cmd):
    subprocess.run(cmd.split())


if __name__ == "__main__":
    p = [Process(target=launch_llava_process, args=(c, )) 
         for c in COMMANDS[:int(os.getenv("WORKER_AMNT")) + 1]]
    
    for _p in p:
        _p.start()
    for _p in p:
        _p.join()