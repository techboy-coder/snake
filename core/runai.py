from multiprocessing import Process
import subprocess


def runInParallel(*fns):
  proc = []
  for fn in fns:
    p = Process(target=fn)
    p.start()
    proc.append(p)
  for p in proc:
    p.join()

def runai():
  subprocess.Popen(["python", "client.py"])

if __name__ == "__main__":
    num_clients = 10
    print("Starting", num_clients, "clients")
    runInParallel(*[runai() for _ in range(num_clients)])
