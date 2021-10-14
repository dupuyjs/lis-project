
# Import libraries
import argparse
from azureml.core import Run

def main():
    # Get parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_dir', 
                        type=str, 
                        dest='model_dir', 
                        default="outputs",
                        help='model location')
    parser.add_argument("--model_name",
                        type=str,
                        help="Name of the Registered Model",
                        default="lis-gpt2-model")
    parser.add_argument("--register_deploy_link",
                        type=str,
                        help="register_deploy_link",
                        default="register_deploy_link")

   
    args = parser.parse_args()
    model_dir = args.model_dir
    model_name = args.model_name

    # Get the experiment run context
    run = Run.get_context()

    # load the model
    print("Loading model from " + model_dir)
    model_file = os.path.join(model_dir, "tf_model.h5")
    model_config_file = os.path.join(model_dir, "config.json")

    # Get metrics for registration
    metrics = run.parent.get_metrics()

    # Register the model
    run.upload_file("outputs/tf_model.h5", model_file)
    run.upload_file("outputs/config.json", model_config_file)
    
    run.register_model(
        model_path="outputs/",
        model_name=model_name,
        tags=metrics)

    run.complete()


if __name__ == '__main__':
    main()
