import numpy as np
import os
import time
import threading

from test_utils import get_arch, get_models


def check_thread():
    all_child_threads = [thread for thread in threading.enumerate() if thread != threading.main_thread()]
    for thread in all_child_threads:
        print(thread.getName())
        print(thread.is_alive())
        print(thread.__dict__)
        print(thread.isDaemon())


def setup_mock_dlr(model_names):
    """setup function mirror load_and_run_tvm_model.py
    """
    print("set up dlr")

    if not model_names:
        raise Exception("model_names is empty")

    arch = get_arch()
    for model_name in model_names:
        get_models(model_name, arch, kind='tvm')


def test_notification(capsys):
    """integration test for phone-home mechanism

    This mirrors load_and_run_tvm_model.py to simulate proper usage of the DLR.
    To run this, just pytest -s test_counter_mgr.py
    """
    from dlr import DLRModel
    from dlr.counter.config import CALL_HOME_USR_NOTIFICATION

    # test the notification capture
    captured = capsys.readouterr()
    print('captured output:', captured.out)
    assert captured.out is not ''
    assert captured.out.find(CALL_HOME_USR_NOTIFICATION) >= 0

    # setup
    setup_mock_dlr(['resnet18_v1'])

    # mirror load_and_run_tvm_model.py for integration test
    # load the model
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resnet18_v1')
    device = 'cpu'
    model = DLRModel(model_path, device)

    # run the model
    image = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dog.npy')).astype(np.float32)
    # flatten within a input array
    input_data = {'data': image}
    print('Testing inference on resnet18...')
    probabilities = model.run(input_data)  # need to be a list of input arrays matching input names

    assert probabilities[0].argmax() == 151


def test_multi_models():
    # setup
    model_names = ['resnet18_v1', '4in2out', 'assign_op']
    setup_mock_dlr(model_names)

    # import like this so won't implicate other tests
    from load_and_run_tvm_model import test_resnet, test_multi_input_multi_output, test_assign_op

    # running load_and_run_tvm model to verify phone-home doesn't break DLR
    for i in range(0, 10):
        test_resnet()
        test_multi_input_multi_output()
        test_assign_op()
        time.sleep(1)
