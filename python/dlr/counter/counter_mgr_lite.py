from .utils.helper import get_hash_string
from .utils import resturlutils
import time
from concurrent.futures import ThreadPoolExecutor


def call_home_lite(func):
    def wrapper(*args, **kwargs):

        has_instance = CounterMgrLite.has_instance()
        mgr = CounterMgrLite.get_instances()
        if not has_instance:
            print('disclaimer')
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

    metrics = {}

    @staticmethod
    def has_instance():
        return CounterMgrLite._instance is not None

    @staticmethod
    def get_instances():
        CounterMgrLite._instance = CounterMgrLite()
        return CounterMgrLite._instance

    def __init__(self):
        self.msgs = []
        self.client = resturlutils.RestUrlUtils()

    def add_runtime_loaded(self):
        data = {'record_type': self.RUNTIME_LOAD}
        self.msgs.append(data)

    def add_model_loaded(self, model: str):
        model_name = self.get_model_hash(model)
        data = {'record_type': self.MODEL_LOAD, 'model': model_name}
        self.msgs.append(data)

    def add_model_run(self, model: str):
        model_name = self.get_model_hash(model)
        if model in self.metrics:
            val = self.metrics[model_name]
            self.metrics[model_name] = val + 1
        else:
            self.metrics[model_name] = 1

    def get_model_hash(self, model):
        hashed = get_hash_string(model.encode())
        name = str(hashed.hexdigets())
        return name

    def create_thread(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.send_msg)

    def send_msg(self):
        while True:
            for m in self.msgs:
                self.client.send(m)
            time.sleep(300)
