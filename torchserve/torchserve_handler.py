import sys
import os
import ast
import json
import logging
import os
from abc import ABC
from typing import Dict, List, Tuple

import torch
import transformers

# from captum.attr import LayerIntegratedGradients
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)

import zipfile
import torch.cuda.amp as amp

from ts.torch_handler.base_handler import BaseHandler

logger = logging.getLogger(__name__)
logger.info("Transformers version %s", transformers.__version__)

SETUP_CONFIG = {
    "model_name": "bigscience/bloomz-3b",
    "mode": "chatbot",
    "save_mode": "pretrained",
    "max_length": "2176",
    # --deprecated
    "FasterTransformer": False,
    "BetterTransformer": False,
}


class TransformersSeqClassifierHandler(BaseHandler, ABC):
    """
    Transformers handler class for sequence, token classification and question answering.
    """

    def __init__(self):
        super(TransformersSeqClassifierHandler, self).__init__()
        self.initialized = False

    def initialize(self, ctx):
        """In this initialize function, the BERT model is loaded and
        the Layer Integrated Gradients Algorithm for Captum Explanations
        is initialized here.
        Args:
            ctx (context): It is a JSON Object containing information
            pertaining to the model artefacts parameters.
        """
        self.manifest = ctx.manifest
        properties = ctx.system_properties
        model_dir = properties.get("model_dir")
        serialized_file = self.manifest["model"]["serializedFile"]
        model_pt_path = os.path.join(model_dir, serialized_file)

        self.device = torch.device(
            "cuda:" + str(properties.get("gpu_id"))
            if torch.cuda.is_available() and properties.get("gpu_id") is not None
            else "cpu"
        )

        # with zipfile.ZipFile(model_dir + "/module.zip", "r") as zip_ref:
        #     zip_ref.extractall(model_dir)

        # read configs for the mode, model_name, etc. from setup_config.json
        setup_config_path = os.path.join(model_dir, "setup_config.json")
        if os.path.isfile(setup_config_path):
            with open(setup_config_path) as setup_config_file:
                self.setup_config = json.load(setup_config_file)
        else:
            logger.warning("Missing the setup_config.json file.")

        self.setup_config = SETUP_CONFIG

        # Loading the shared object of compiled Faster Transformer Library if Faster Transformer is set
        if self.setup_config["FasterTransformer"]:
            faster_transformer_complied_path = os.path.join(
                model_dir, "libpyt_fastertransformer.so"
            )
            torch.classes.load_library(faster_transformer_complied_path)
        # Loading the model and tokenizer from checkpoint and config files based on the user's choice of mode
        # further setup config can be added.
        if self.setup_config["save_mode"] == "torchscript":
            self.model = torch.jit.load(model_pt_path, map_location=self.device)
        elif self.setup_config["save_mode"] == "pretrained":
            if self.setup_config["mode"] == "chatbot":
                self.model = AutoModelForCausalLM.from_pretrained(model_dir, device_map="auto", load_in_8bit=True)

            else:
                logger.warning("Missing the operation mode.")
            # Using the Better Transformer integration to speedup the inference
            if self.setup_config["BetterTransformer"]:
                try:
                    from optimum.bettertransformer import BetterTransformer

                    self.model = BetterTransformer.transform(self.model)
                except ImportError as error:
                    logger.warning(
                        "HuggingFace Optimum is not installed. Proceeding without BetterTransformer"
                    )
                except RuntimeError as error:
                    logger.warning(
                        "HuggingFace Optimum is not supporting this model,for the list of supported models, please refer to this doc,https://huggingface.co/docs/optimum/bettertransformer/overview"
                    )
            self.model.to(self.device)

        else:
            logger.warning("Missing the checkpoint or state_dict.")

        print("model_dir", model_dir)
        print("os.listdir(model_dir)", os.listdir(model_dir))
        print("self.setup_config", self.setup_config)
        print("self.setup_config['model_name']", self.setup_config["model_name"])
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)

        self.model.eval()
        logger.info("Transformer model from path %s loaded successfully", model_dir)

        self.initialized = True

    def preprocess(self, requests):
        """Basic text preprocessing, based on the user's chocie of application mode.
        Args:
            requests (str): The Input data in the form of text is passed on to the preprocess
            function.
        Returns:
            list : The preprocess function returns a list of Tensor for the size of the word tokens.
        """
        input_ids_batch = []
        attention_mask_batch = []
        for idx, data in enumerate(requests):
            input_text = data.get("data")
            if input_text is None:
                input_text = data.get("body")
            if isinstance(input_text, (bytes, bytearray)):
                input_text = input_text.decode("utf-8")

            max_length = self.setup_config["max_length"]
            logger.info("Received text: '%s'", input_text)
            # preprocessing text for sequence_classification, token_classification or text_generation
            # question_context = ast.literal_eval(input_text)
            question_context = json.loads(input_text)

            # temperature = question_context.get("temperature", 0.7)
            prompt = question_context.get("prompt", "")
            # num_beams = question_context.get("num_beams", 1)
            # min_tokens = question_context.get("min_tokens", 30)
            # max_tokens = question_context.get("max_tokens", 4096)

            print(f"Received request: {question_context}")

            text = prompt

            # Get chat answer
            print(f"Input: {text}")

            logger.info(f"Final input into model {text}")
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=int(max_length),
                truncation=True,
            )

            input_ids = inputs["input_ids"].to(self.device)
            attention_mask = inputs["attention_mask"].to(self.device)

            decoded_text = self.tokenizer.batch_decode(input_ids)
            logger.info(f"Decoded text after tokenizer: {decoded_text}")
            logger.info(f"input_ids {input_ids}")
            logger.info(f"attention_mask {attention_mask}")
            logger.info(f"input_ids.shape {input_ids.shape}")
            logger.info(f"attention_mask.shape {attention_mask.shape}")
            logger.info(f"Total words of original text {len(text.split())}")
            logger.info(
                f"Total words of processed text {len(decoded_text[0].split())}"
            )
            logger.info(f"Total tokens of processed text {input_ids.shape[1]}")

            input_ids_batch.append(input_ids)
            attention_mask_batch.append(attention_mask)

        logger.info(f"----- Done preprocessing ------")
        logger.info(f"input_ids_batch {input_ids_batch}")
        logger.info(f"attention_mask_batch {attention_mask_batch}")
        return (input_ids_batch, attention_mask_batch)

    def inference(self, input_batch):
        """Predict the class (or classes) of the received text using the
        serialized transformers checkpoint.
        Args:
            input_batch (list): List of Text Tensors from the pre-process function is passed here
        Returns:
            list : It returns a list of the predicted value for the input text
        """
        input_ids_batch, attention_mask_batch = input_batch

        inferences: List[str]

        with torch.inference_mode():
            inferences = self.model.generate(
                input_ids=input_ids_batch,
                attention_mask=attention_mask_batch,
                max_length=4096,
                num_beams=4,
                early_stopping=True,
                repetition_penalty=2.5,
                length_penalty=1.0,
            )

        # inferences = self._generate(
        #     dict(input_ids=input_ids_batch, attention_mask=attention_mask_batch),
        #     model=self.model,
        #     tokenizer=self.tokenizer,
        #     max_target_length=512,
        #     num_beams=8,
        #     early_stopping=True,
        #     repetition_penalty=2.5,
        #     length_penalty=1.0,
        #     filter_beam_rule_based=True,
        #     verbose=True,
        # )

        logging.info(
            "Generated text chatbot: '%s'", inferences
        )
        return inferences

    def postprocess(self, inference_output):
        """Post Process Function converts the predicted response into Torchserve readable format.
        Args:
            inference_output (list): It contains the predicted response of the input text.
        Returns:
            (list): Returns a list of the Predictions and Explanations.
        """
        inferences = inference_output

        response = []
        for out in inferences:
            response.append(
                json.dumps({
                    "text": out,
                },
                ensure_ascii=False,)
            )
        logger.info("Batch Response: '%s'", response)
        return response

    def get_insights(self, input_batch, text, target):
        """This function initialize and calls the layer integrated gradient to get word importance
        of the input text if captum explanation has been selected through setup_config
        Args:
            input_batch (int): Batches of tokens IDs of text
            text (str): The Text specified in the input request
            target (int): The Target can be set to any acceptable label under the user's discretion.
        Returns:
            (list): Returns a list of importances and words.
        """

        return None

