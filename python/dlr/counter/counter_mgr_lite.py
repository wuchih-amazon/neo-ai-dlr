from .utils.helper import get_hash_string
from .utils import resturlutils
import time
import json
import atexit

from concurrent.futures import ThreadPoolExecutor
from .config import CALL_HOME_USR_NOTIFICATION
from threading import Thread, Event


def call_home_lite(func):
    def wrapper(*args, **kwargs):

        has_instance = CounterMgrLite.has_instance()
        mgr = CounterMgrLite.get_instances()
        if not has_instance:
            print(CALL_HOME_USR_NOTIFICATION)
            mgr.add_runtime_loaded()

        resp = func(*args, **kwargs)
        if func.__name__ == '__init__':
            model = args[0]
            mgr.add_model_loaded(model.get_model_name())
        elif func.__name__ == 'run':
            model = args[0]
            mgr.add_model_run(model.get_model_name())

        return resp

    return wrapper


class CounterMgrLite:
    _instance = None
    RUNTIME_LOAD = 1
    MODEL_LOAD = 2
    MODEL_RUN = 3

    @staticmethod
    def has_instance():
        return CounterMgrLite._instance is not None

    @staticmethod
    def get_instances():
        if not CounterMgrLite._instance:
            CounterMgrLite._instance = CounterMgrLite()
            atexit.register(CounterMgrLite._instance.clean_up)
        return CounterMgrLite._instance

    def __init__(self):
        self.msgs = []
        self.client = resturlutils.RestUrlUtils()
        self.metrics = {}
        self.is_process = False

        self.stop_evt = None
        self.worker = None

        self.create_thread()

    def add_runtime_loaded(self):
        data = {'record_type': self.RUNTIME_LOAD}
        self.msgs.append(json.dumps(data))

    def add_model_loaded(self, model: str):
        model_name = self.get_model_hash(model)
        data = {'record_type': self.MODEL_LOAD, 'model': model_name}
        self.msgs.append(json.dumps(data))

    def add_model_run(self, model: str):
        model_name = self.get_model_hash(model)
        print('model_name', model_name, self.metrics)
        if self.metrics.get(model_name) is not None:
            self.metrics[model_name] += 1
        else:
            print('model_name not found', model_name)
            self.metrics[model_name] = 1

    def get_model_hash(self, model):
        hashed = get_hash_string(model.encode())
        name = str(hashed.hexdigest())
        return name

    def create_thread(self):
        self.is_process = True

        self.stop_evt = Event()
        self.worker = Worker(self.send_msg, self.stop_evt)
        self.worker.start()

    def worker(self):
        self.send_msg()

    def send_msg(self):
        for k in list(self.metrics):
            pub_data = {'record_type': self.MODEL_RUN, 'model': k, 'run_count': self.metrics[k]}
            self.msgs.append(json.dumps(pub_data))
        self.metrics.clear()

        while len(self.msgs) != 0:
            m = self.msgs.pop()
            print('message: ', m)
            self.client.send(m)

    def clean_up(self):
        print("clean up initiated")
        # self.executor.shutdown()

        self.stop_evt.set()
        self.send_msg()
        print("clean up done")


class Worker(Thread):

    def __init__(self, fn, event: Event):
        self.fn = fn
        self.stop_evt = event

    def run(self):
        while not self.stop_evt.wait(5):
            print("execute thread")
            self.fn()