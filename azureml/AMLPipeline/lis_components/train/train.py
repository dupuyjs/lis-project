
import random
import logging
from importlib import reload  # Not needed in Python 2
from typing import Optional

import numpy as np
import tensorflow as tf
import math
from functools import partial

from transformers import TFTrainingArguments, HfArgumentParser
from transformers import AutoConfig, AutoTokenizer
from transformers import TFAutoModelForCausalLM
from transformers import create_optimizer
from datasets import load_dataset

from dataclasses import dataclass, field

from azureml.core import Run

#reload(logging)
#logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%I:%M:%S')
#logger = logging.getLogger()


# region Command-line arguments
@dataclass
class ModelArguments:
    """
    Arguments pertaining to which model/config/tokenizer we are going to fine-tune, or train from scratch.
    """

    model_name: str = field(
        default="gpt2",
        metadata={
            "help": "The model checkpoint for weights initialization."
        },
    )
        
    def __post_init__(self):
        if self.model_name is None:
            raise ValueError(
                "--cannot call script without model_name argument"
            )

@dataclass
class DataTrainingArguments:
    """
    Arguments pertaining to what data we are going to input our model for training and eval.
    """

    train_file: str = field(default="data/train.csv", metadata={"help": "The input training data file (a csv file)."})
    eval_file: str = field(
        default="data/eval.csv",
        metadata={"help": "The input evaluation data file to evaluate the perplexity on (a csv file)."},
    )
    overwrite_cache: bool = field(
        default=True, metadata={"help": "Overwrite the cached training and evaluation sets"}
    )
    preprocessing_num_workers: Optional[int] = field(
        default=None,
        metadata={"help": "The number of processes to use for the preprocessing."},
    )
    max_train_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": "For debugging purposes or quicker training, truncate the number of training examples to this "
            "value if set."
        },
    )
    max_eval_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": "For debugging purposes or quicker training, truncate the number of evaluation examples to this "
            "value if set."
        },
    )

    def __post_init__(self):
        if self.train_file is None or self.eval_file is None:
            raise ValueError(
                "--cannot call scripts without train_file & eval_file arguments"
            )

def sample_generator(dataset, tokenizer):
    # Trim off the last partial batch if present
    sample_ordering = np.random.permutation(len(dataset))
    for sample_idx in sample_ordering:
        example = dataset[int(sample_idx)]
        # Handle dicts with proper padding and conversion to tensor.
        example = {key: tf.convert_to_tensor(arr, dtype_hint=tf.int64) for key, arr in example.items()}
        yield example, example["labels"]  # TF needs some kind of labels, even if we don't use them
    return

# region Helper classes
class SavePretrainedCallback(tf.keras.callbacks.Callback):
    # Hugging Face models have a save_pretrained() method that saves both the weights and the necessary
    # metadata to allow them to be loaded as a pretrained model in future. This is a simple Keras callback
    # that saves the model with this method after each epoch.
    def __init__(self, output_dir, **kwargs):
        super().__init__()
        self.output_dir = output_dir

    def on_epoch_end(self, epoch, logs=None):
        self.model.save_pretrained(self.output_dir)
        
        
def main():
    # region Argument Parsing
    parser = HfArgumentParser((ModelArguments, DataTrainingArguments, TFTrainingArguments))

    # region Setup logging
    #logger.setLevel(logging.INFO)
    
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    # Load the dataset from the datastore.
    raw_datasets = load_dataset('csv', data_files={'train': data_args.train_file, 'test': data_args.eval_file})

    # Testing loading datasets
    index = random.sample(range(len(raw_datasets["train"])), 1)
    #logger.info(f"  Example raw dataset: %s", raw_datasets["train"][index])

    # Load pretrained model and tokenizer
    
    config = AutoConfig.from_pretrained(model_args.model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_args.model_name)

    text_column_name = "text"
    column_names = raw_datasets["train"].column_names
    
    # Preprocess Dataset & add eos_token 
    # Main data processing function that will add eos_token to each text in the dataset
    def add_eos_token(examples):
        examples_with_eos = examples
        examples_with_eos[text_column_name] = [x + tokenizer.eos_token for x in examples[text_column_name]]  
        return examples_with_eos

    raw_datasets = raw_datasets.map(
        add_eos_token,
        batched=True,
        num_proc=data_args.preprocessing_num_workers,
        load_from_cache_file=not data_args.overwrite_cache,
        desc=f"Adding eos_token to each example in the dataset",
    )
    
    # Testing preprocess
    #logger.info(f"  Example raw dataset with eos token: %s", raw_datasets["train"][index])

    ## Tokenize dataset using gpt2 tokenizer
    def tokenize_function(examples):
        return tokenizer(examples[text_column_name])

    tokenized_datasets = raw_datasets.map(
        tokenize_function,
        batched=True,
        num_proc=data_args.preprocessing_num_workers,
        remove_columns=column_names,
        load_from_cache_file=not data_args.overwrite_cache,
        desc="Running tokenizer on dataset",
    )
    
    # Testing Tokenization
    #logger.info(f"  Example tokenized dataset: %s", tokenized_datasets["train"][index])

    # Concatenate all texts from our dataset and generate chunks of block_size
    
    block_size = tokenizer.model_max_length
    if block_size > 1024:
        # The tokenizer picked seems to have a very large `model_max_length`
        block_size = 1024

    # Main data processing function that will concatenate all texts from our dataset and generate chunks of block_size.
    def group_texts(examples):
        # Concatenate all texts.
        concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
        total_length = len(concatenated_examples[list(examples.keys())[0]])
        # We drop the small remainder, we could add padding if the model supported it instead of this drop, you can
        # customize this part to your needs.
        if total_length >= block_size:
            total_length = (total_length // block_size) * block_size
        # Split by chunks of max_len.
        result = {
            k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
            for k, t in concatenated_examples.items()
        }
        result["labels"] = result["input_ids"].copy()
        return result

    lm_datasets = tokenized_datasets.map(
        group_texts,
        batched=True,
        batch_size=len(tokenized_datasets["train"]), # if training size is very small, like in our case.
        num_proc=data_args.preprocessing_num_workers,
        load_from_cache_file=not data_args.overwrite_cache,
        desc=f"Grouping texts in chunks of {block_size}",
    )
    
    # Testing Grouping Texts
    
    #logger.info(f"  Example 0 raw dataset: %s", raw_datasets["train"][0])
    #logger.info(f"  Example 0 raw dataset: %s", raw_datasets["train"][1])
    #logger.info(f"  Example 0 raw dataset: %s", raw_datasets["train"][2])
    #logger.info(f"  Example 0 raw dataset: %s", raw_datasets["train"][3])

    #logger.info(f"  Example 0 tokenized dataset: %s", tokenized_datasets["train"][0])
    #logger.info(f"  Example 0 tokenized dataset: %s", tokenized_datasets["train"][1])
    #logger.info(f"  Example 0 tokenized dataset: %s", tokenized_datasets["train"][2])
    #logger.info(f"  Example 0 tokenized dataset: %s", tokenized_datasets["train"][3])

   
    #logger.info(f"  Example 0 concatenated tokenized dataset: %s", lm_datasets["train"][0]['input_ids'][:40])

    
    # Prepare Training & Evaluation Datasets
    train_dataset = lm_datasets["train"]
    eval_dataset = lm_datasets["test"]
    
    if data_args.max_train_samples is not None:
        train_dataset = train_dataset.select(range(data_args.max_train_samples))
    if data_args.max_eval_samples is not None:
        eval_dataset = eval_dataset.select(range(data_args.max_eval_samples))
        
    # Logging Training Parameters
    
    num_replicas = training_args.strategy.num_replicas_in_sync
    batches_per_epoch = len(train_dataset) // (num_replicas * training_args.per_device_train_batch_size)
    """
    logger.info(f"  Training Arguments: %s",
    {
        "init_lr": training_args.learning_rate,
        "num_replicas": num_replicas,
        "strategy": training_args.strategy,
        "num_train_epochs": training_args.num_train_epochs,
        "per_device_train_batch_size": training_args.per_device_train_batch_size,
        "batches_per_epoch": len(train_dataset) // (num_replicas * training_args.per_device_train_batch_size),
        "num_train_steps": int(training_args.num_train_epochs * batches_per_epoch),
        "num_warmup_steps": training_args.warmup_steps,
        "adam_beta1": training_args.adam_beta1,
        "adam_beta2": training_args.adam_beta2,
        "adam_epsilon": training_args.adam_epsilon,
        "weight_decay_rate": training_args.weight_decay
    }
    )
    """

    
    # Train Model

    with training_args.strategy.scope():

        config = AutoConfig.from_pretrained(model_args.model_name)
        model = TFAutoModelForCausalLM.from_pretrained(model_args.model_name, config=config)

        model.resize_token_embeddings(len(tokenizer))

        num_replicas = training_args.strategy.num_replicas_in_sync

        # region TF Dataset preparation
        train_generator = partial(sample_generator, train_dataset, tokenizer)
        train_signature = {
            feature: tf.TensorSpec(shape=(None,), dtype=tf.int64)
            for feature in train_dataset.features
            if feature != "special_tokens_mask"
        }
        train_sig = (train_signature, train_signature["labels"])
        options = tf.data.Options()
        options.experimental_distribute.auto_shard_policy = tf.data.experimental.AutoShardPolicy.OFF
        tf_train_dataset = (
            tf.data.Dataset.from_generator(train_generator, output_signature=train_sig)
            .with_options(options)
            .batch(batch_size=num_replicas * training_args.per_device_train_batch_size, drop_remainder=True)
            .repeat(int(training_args.num_train_epochs))
        )
        eval_generator = partial(sample_generator, eval_dataset, tokenizer)
        eval_signature = {
            feature: tf.TensorSpec(shape=(None,), dtype=tf.int64)
            for feature in eval_dataset.features
            if feature != "special_tokens_mask"
        }
        eval_sig = (eval_signature, eval_signature["labels"])
        tf_eval_dataset = (
            tf.data.Dataset.from_generator(eval_generator, output_signature=eval_sig)
            .with_options(options)
            .batch(batch_size=num_replicas * training_args.per_device_eval_batch_size, drop_remainder=True)
            .repeat(int(training_args.num_train_epochs))
        )
        # endregion
        # region Optimizer and loss

        batches_per_epoch = len(train_dataset) // (num_replicas * training_args.per_device_train_batch_size)
        # Bias and layernorm weights are automatically excluded from the decay
        optimizer, lr_schedule = create_optimizer(
            init_lr=training_args.learning_rate,
            num_train_steps=int(training_args.num_train_epochs * batches_per_epoch),
            num_warmup_steps=training_args.warmup_steps,
            adam_beta1=training_args.adam_beta1,
            adam_beta2=training_args.adam_beta2,
            adam_epsilon=training_args.adam_epsilon,
            weight_decay_rate=training_args.weight_decay,
        )

        def dummy_loss(y_true, y_pred):
            return tf.reduce_mean(y_pred)

        model.compile(optimizer=optimizer, loss={"loss": dummy_loss})
        # endregion

        # region Training and validation
        #logger.info("***** Running training *****")
        #logger.info(f"  Num examples = {len(train_dataset)}")
        #logger.info(f"  Num Epochs = {training_args.num_train_epochs}")
        #logger.info(f"  Instantaneous batch size per device = {training_args.per_device_train_batch_size}")
        #logger.info(f"  Total train batch size = {training_args.per_device_train_batch_size * num_replicas}")

        history = model.fit(
            tf_train_dataset,
            validation_data=tf_eval_dataset,
            epochs=int(training_args.num_train_epochs),
            steps_per_epoch=len(train_dataset) // (training_args.per_device_train_batch_size * num_replicas),
            callbacks=[SavePretrainedCallback(output_dir=training_args.output_dir)],
        )
        try:
            train_perplexity = math.exp(history.history["loss"][-1])
        except OverflowError:
            train_perplexity = math.inf
        try:
            validation_perplexity = math.exp(history.history["val_loss"][-1])
        except OverflowError:
            validation_perplexity = math.inf
        #logger.info(f"  Final train loss: {history.history['loss'][-1]:.3f}")
        #logger.info(f"  Final train perplexity: {train_perplexity:.3f}")
        #logger.info(f"  Final validation loss: {history.history['val_loss'][-1]:.3f}")
        #logger.info(f"  Final validation perplexity: {validation_perplexity:.3f}")
        # endregion
        
        # log metrics to AML
        run = Run.get_context()

        run.log("Final train loss", history.history['loss'][-1])
        run.log("Final validation loss", history.history['val_loss'][-1])
        run.log("Final train perplexity", train_perplexity)
        run.log("Final validation perplexity", validation_perplexity)

        run.parent.log("Final train loss", history.history['loss'][-1])
        run.parent.log("Final validation loss", history.history['val_loss'][-1])
        run.parent.log("Final train perplexity", train_perplexity)
        run.parent.log("Final validation perplexity", validation_perplexity)
                
        if training_args.output_dir is not None:
            model.save_pretrained(training_args.output_dir)

if __name__ == "__main__":
    main()
