import pandas as pd
import numpy as np

from joblib import Memory

from lotaru.LotaruInstance import LotaruInstance
from lotaru.TraceReader import TraceReader
from lotaru.Scaler import Scaler
from lotaru.Constants import WORKFLOWS, NODES, LOTARU_G_BENCH

memory = Memory(".cache")


@memory.cache
def run_experiment(workflows=WORKFLOWS, nodes=NODES, experiment_number="0",
                   resource_x="taskinputsizeuncompressed",
                   resource_y="realtime", scaler_type="g",
                   scaler_bench_file=LOTARU_G_BENCH, scale_bayesian_model=True,
                   scale_median_model=False):
    trace_reader = TraceReader()

    # create one lotaru instance per workflow
    workflow_lotaru_instance_map = {}
    for workflow in workflows:
        training_data = trace_reader.get_training_data(
            workflow, experiment_number, resource_x, resource_y)
        scaler = Scaler(scaler_type, workflow, scaler_bench_file)
        li = LotaruInstance(training_data, scaler,
                            scale_bayesian_model=scale_bayesian_model,
                            scale_median_model=scale_median_model)
        li.train_models()
        workflow_lotaru_instance_map[workflow] = li

    results = pd.DataFrame(
        columns=["workflow", "task", "node", "model", "x", "yhat", "y", "rae"])
    # print predictions for all workflows, tasks and nodes
    # TODO proper decimals with
    # Decimal('7.325').quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    # .apply(lambda x: int(x))
    for workflow in workflows:
        for task in WORKFLOWS[workflow]:
            for node in nodes:
                lotaru_instance = workflow_lotaru_instance_map[workflow]
                model_type = type(lotaru_instance.get_model_for_task(task))
                test_data = trace_reader.get_test_data(workflow, task, node)
                x = test_data[resource_x].to_numpy().reshape(-1, 1)
                yhat = test_data[resource_y].to_numpy()
                y = lotaru_instance.get_prediction(task, node, x)
                rae = np.abs((y - yhat) / yhat)
                for i in range(x.size):
                    results.loc[results.index.size] = [
                        workflow, task, node, model_type, x[i], yhat[i], y[i], rae[i]]

    return results
