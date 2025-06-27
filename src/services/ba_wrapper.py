import os
from biasanalyzer.api import BIAS


def initilize_bias_analyzer():
    bias = BIAS()
    bias.set_config(os.path.join(os.path.dirname(__file__),
                                 '..', '..', 'config', 'config.yaml'))
    bias.set_root_omop()
    return bias
