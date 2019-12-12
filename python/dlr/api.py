# coding: utf-8
from __future__ import absolute_import as _abs

import abc
import glob
import logging
import os

from .counter.counter_mgr import CallCounterMgr


# Interface
class IDLRModel:
    __metaclass__=abc.ABCMeta

    @abc.abstractmethod
    def get_input_names(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_input(self, name, shape=None):
        raise NotImplementedError

    @abc.abstractmethod
    def get_output_names(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_version(self):
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, input_data):
        raise NotImplementedError


def _find_model_file(model_path, ext):
    if os.path.isfile(model_path) and model_path.endswith(ext):
        return model_path
    model_files = glob.glob(os.path.abspath(os.path.join(model_path, '*'+ext)))
    if len(model_files) > 1:
        raise ValueError('Multiple {} files found under {}'.format(ext, mdel_path))
    elif len(model_files) == 1:
        return model_files[0]
    return None


def call_home(func):
    def wrapped_call_home(*args, **kwargs):
        call_counter = CallCounterMgr.get_instance()
        if call_counter:
            if func.__name__ == "init_call_home":
                func(*args, **kwargs)
                call_counter.runtime_loaded()
            elif func.__name__ == "__init__":
                func(*args, **kwargs)
                obj = args[0]
                call_counter.model_count(CallCounterMgr.MODEL_LOAD, obj._model)
            else:
                res = func(*args, **kwargs)
                obj = args[0]
                call_counter.model_count(CallCounterMgr.MODEL_RUN, obj._model)
                return res

    return wrapped_call_home


# Wrapper class
class DLRModel(IDLRModel):
    @call_home
    def __init__(self, model_path, dev_type=None, dev_id=None):
        # Find correct runtime implementation for the model
        self._model = model_path
        tf_model_path = _find_model_file(model_path, '.pb')
        tflite_model_path = _find_model_file(model_path, '.tflite')
        # Check if found both Tensorflow and TFLite files
        if tf_model_path is not None and tflite_model_path is not None:
            raise ValueError('Found both .pb and .tflite files under {}'.format(mdel_path))
        # Tensorflow
        if tf_model_path is not None:
            from .tf_model import TFModelImpl
            self._impl = TFModelImpl(tf_model_path, dev_type, dev_id)
            return
        # TFLite
        if tflite_model_path is not None:
            if dev_type is not None:
                logging.warning("dev_type parameter is not supported")
            if dev_id is not None:
                logging.warning("dev_id parameter is not supported")
            from .tflite_model import TFLiteModelImpl
            self._impl = TFLiteModelImpl(tflite_model_path)
            return
        # Default to TVM+Treelite
        from .dlr_model import DLRModelImpl
        if dev_type is None:
            dev_type = 'cpu'
        if dev_id is None:
            dev_id = 0
        self._impl = DLRModelImpl(model_path, dev_type, dev_id)

    @call_home
    def run(self, input_values):
        return self._impl.run(input_values)

    def get_input_names(self):
        return self._impl.get_input_names()

    def get_input(self, name, shape=None):
        return self._impl.get_input(name, shape)

    def get_output_names(self):
        return self._impl.get_output_names()

    def get_version(self):
        return self._impl.get_version()


# call home feature starts
@call_home
def init_call_home():
    pass


init_call_home()
