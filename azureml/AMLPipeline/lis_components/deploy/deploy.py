
from azureml.core.webservice import AciWebservice
from azureml.core.model import InferenceConfig
from azureml.core import Run
from azureml.core.model import Model

import argparse
import os

def main():
    # Get parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("--service_name",
                        type=str,
                        help="Name of the Web Service",
                        default="lis-gpt2-webservice")
    parser.add_argument("--model_name",
                        type=str,
                        help="Name of the registered model name",
                        default="lis-gpt2-model")
    parser.add_argument("--cpu_cores",
                        type=int,
                        help="CPU reserve capacity",
                        default=1)
    parser.add_argument("--memory_gb",
                        type=float,
                        help="Memory reserve capacity",
                        default=2)
    parser.add_argument("--register_deploy_link",
                        type=str,
                        help="register_deploy_link",
                        default="register_deploy_link")
    args = parser.parse_args()
    service_name = args.service_name
    model_name = args.model_name
    cpu_cores = args.cpu_cores
    memory_gb = args.memory_gb    
    components_dir = "lis_components"
    
    # Configure the scoring environment
    inference_config = InferenceConfig(runtime= "python",
                                       entry_script=os.path.join(components_dir, "deploy", "score.py"),
                                       conda_file=os.path.join(components_dir, "dependencies_scoring.yml"))

    deployment_config = AciWebservice.deploy_configuration(cpu_cores = cpu_cores, memory_gb = memory_gb)
    
    # Get the experiment run context
    run = Run.get_context()
    ws = run.experiment.workspace
    
    model = ws.models[model_name]
    print(model.name, 'version', model.version)

    service = Model.deploy(ws, service_name, [model], inference_config, deployment_config)

    service.wait_for_deployment(True)
    
    print(service.state)
    
if __name__ == '__main__':
    main()
