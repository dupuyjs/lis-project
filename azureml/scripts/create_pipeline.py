import os
import sys

from azureml.core import Datastore, Environment, Workspace
from azureml.core.authentication import AzureCliAuthentication
from azureml.core.compute import ComputeTarget
from azureml.core.compute_target import ComputeTargetException
from azureml.core.runconfig import RunConfiguration
from azureml.data import OutputFileDatasetConfig
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep

subscription_id = sys.argv[1]
resource_group = sys.argv[2]
workspace_name = sys.argv[3]
cluster_name = sys.argv[4]
storage_account_name = sys.argv[5]

cli_auth = AzureCliAuthentication()

ws = Workspace(
    subscription_id=subscription_id,
    resource_group=resource_group,
    workspace_name=workspace_name,
    auth=cli_auth
)

# Datastore

blob_store = Datastore.register_azure_blob_container(
    workspace=ws,
    datastore_name='lis_artifacts',
    container_name='lis-artifacts',
    account_name=storage_account_name)

blob_store = Datastore.get(ws, datastore_name='lis_artifacts')

ws.set_default_datastore('lis_artifacts')

print("Datastore created.")

# Pipeline

components_dir = 'lis_components'

try:
    # Check for existing compute target
    pipeline_cluster = ComputeTarget(workspace=ws, name=cluster_name)
    print('Found existing cluster, use it.')
except ComputeTargetException:
    print('Compute cluster not found, aborting.')
    exit(1)

# Create a Python environment for the pipeline experiment
pipeline_environment = Environment.from_conda_specification(
    name='pipeline-env',
    file_path=os.path.join(components_dir, "dependencies.yml"))
pipeline_environment.python.user_managed_dependencies = False  # Let Azure ML manage dependencies
pipeline_environment.docker.enabled = True  # Use a docker container

# Create a new runconfig object for the pipeline
pipeline_run_config = RunConfiguration()

# Use the compute you created above.
pipeline_run_config.target = pipeline_cluster

# Assign the environment to the run configuration
pipeline_run_config.environment = pipeline_environment

print("Pipeline configuration created.")

# train_file, eval_file and output_file are passed as a datastore path between steps
train_datastore_path = DataReference(
    data_reference_name="train_datastore_path",
    datastore=ws.datastores['lis_artifacts'],
    path_on_datastore="data/train.csv")

eval_datastore_path = DataReference(
    data_reference_name="eval_datastore_path",
    datastore=ws.datastores['lis_artifacts'],
    path_on_datastore="data/eval.csv")

output_datastore_path = OutputFileDatasetConfig(
    "output_datastore_path",
    destination=(ws.datastores['lis_artifacts'], "outputs")).as_mount()

num_train_epochs_param = PipelineParameter(
    name="num_train_epochs",
    default_value=3)

aml_model_name_param = PipelineParameter(
    name="aml_model_name",
    default_value="lis-gpt2-model")

register_deploy_link = PipelineData("register_deploy_link")

aml_service_name_param = PipelineParameter(
    name="aml_service_name",
    default_value="lis-gpt2-serviceapp")
cpu_cores_param = PipelineParameter(name="cpu_cores", default_value=1)
memory_gb_param = PipelineParameter(name="memory_gb", default_value=2)

# Create Step 1, which runs the PythonScriptStep to train / finetune
train_step = PythonScriptStep(
    name="Train",
    source_directory=".",
    script_name=os.path.join(components_dir, "train/train.py"),
    arguments=[
        '--model_name', "gpt2", 
        '--output_dir', output_datastore_path,
        '--train_file', train_datastore_path,
        '--eval_file', eval_datastore_path,
        '--num_train_epochs', num_train_epochs_param,
        # '--per_gpu_train_batch_size', 8,
        # '--per_gpu_eval_batch_size', 8,
        # '--fp16'
    ],
    inputs=[train_datastore_path, eval_datastore_path],
    compute_target=pipeline_cluster,
    runconfig=pipeline_run_config,
    allow_reuse=False)

# Create Step 2, which runs the PythonScriptStep to register model
register_step = PythonScriptStep(
    name="Register",
    source_directory=".",
    script_name=os.path.join(components_dir, "register/register.py"),
    arguments=[
        '--model_name', aml_model_name_param,
        '--model_dir', output_datastore_path.as_input(),
        '--register_deploy_link', register_deploy_link
    ],
    outputs=[register_deploy_link],
    compute_target=pipeline_cluster,
    runconfig=pipeline_run_config,
    allow_reuse=False)

# Construct the pipeline
pipeline_steps = [train_step, register_step]
pipeline = Pipeline(workspace=ws, steps=pipeline_steps)

print("Pipeline is built.")

# Publish the pipeline
pipeline_pub = pipeline.publish(name='lis_pipeline')

print("Pipeline is published: " + str(pipeline_pub))
