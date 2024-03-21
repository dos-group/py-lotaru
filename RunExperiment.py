import os
import sys
import argparse

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from Lotaru import LotaruInstance
from TraceReader import TraceReader

# runs an experiment, returns resuls as pandas dataframe
def run_experiment(
        workflows=["eager", "methylseq", "chipseq", "atacseq", "bacass"],
        nodes=["asok01", "asok02", "n1", "n2", "c2", "local"],
        experiment_number="0",
        resource_x="TaskInputSizeUncompressed",
        resource_y="Realtime",
        scale_bayesian_model=True,
        scale_median_model=False):
    trace_reader = TraceReader(os.path.join("data", "traces"))

    # create one lotaru instance per workflow
    workflow_lotaru_instance_map = {}
    for workflow in workflows:
        workflow_lotaru_instance_map[workflow] = LotaruInstance(workflow, experiment_number,
                resource_x, resource_y, trace_reader, scale_bayesian_model, scale_median_model)
        workflow_lotaru_instance_map[workflow].train_models()

    results = pd.DataFrame(columns=["workflow", "task", "node", "x", "yhat", "y"])
    # print predictions for all workflows, tasks and nodes
    for workflow in workflows:
        lotaru_instance = workflow_lotaru_instance_map[workflow]
        for task in lotaru_instance.get_tasks():
            for node in nodes:
                test_data = trace_reader.get_test_data(workflow, task, node)
                x = test_data[resource_x].to_numpy()
                yhat = test_data[resource_y].to_numpy()
                y = lotaru_instance.get_prediction(task, node, x.reshape(-1, 1))
                for i in range(x.size):
                    results.loc[results.index.size] = [workflow, task, node, x[i], yhat[i], y[i]]

    return results

