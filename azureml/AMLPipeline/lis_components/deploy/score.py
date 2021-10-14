
import json
from transformers import TFGPT2LMHeadModel
from transformers import GPT2Tokenizer
from azureml.core.model import Model

# Called when the service is loaded
def init():
    ## TODO
    global model, tokenizer
    # Get the path to the deployed model file and load it
    model_path = Model.get_model_path('lis-gpt2-model')    
    model = TFGPT2LMHeadModel.from_pretrained(model_path)
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Called when a request is received
def run(raw_data):

    input_ids = tokenizer.encode(json.loads(raw_data)['data'], return_tensors='tf')

    generated_text_samples = model.generate(
        input_ids, 
        max_length=30,  
        num_return_sequences=5,
        no_repeat_ngram_size=2,
        do_sample=True,
        early_stopping=True
    )

    json_output = {}
    for i, beam in enumerate(generated_text_samples):
        json_output[i+1] = tokenizer.decode(beam, skip_special_tokens=True)
        
    # Return the predictions as JSON
    return json.dumps(json_output)
