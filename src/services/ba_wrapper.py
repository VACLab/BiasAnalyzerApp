import os
import time
from biasanalyzer.api import BIAS


_bias_instance = None


def _initialize_bias_analyzer():
    bias = BIAS()
    config_path = os.getenv(
        "BIASANALYZER_CONFIG_PATH",
        os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
    )
    bias.set_config(config_path)
    bias.set_root_omop()
    return bias

def get_bias_analyzer():
    global _bias_instance

    if _bias_instance is None:
        for attempt in range(10):
            try:
                _bias_instance = _initialize_bias_analyzer()
                break
            except Exception as e:
                print("Waiting for OMOP DB...", e)
                time.sleep(5)

    if _bias_instance is None:
        raise RuntimeError("Could not connect to OMOP database after 50 seconds.")

    return _bias_instance


def cleanup_bias_analyzer():
    global _bias_instance
    if _bias_instance is not None:
        _bias_instance.cleanup()
        _bias_instance = None
