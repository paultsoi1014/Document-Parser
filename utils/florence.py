import os
import subprocess
import torch

from PIL import Image as PILImage
from typing import Tuple
from transformers import AutoProcessor, AutoModelForCausalLM


class FlorenceVisionModel:
    """
    A class that encapsulates the Florence-2 model for image-to-text conversion.
    This model processes images and associated text prompts to generate descriptive
    text based on the visual input
    """

    def __init__(self):
        """
        Initializes the FlorenceVisionModel by loading the model and processor

        Attributes
        ----------
        device : torch.device
            The device on which the model is loaded (GPU or CPU)
        vision_model : AutoModelForCausalLM
            The pre-trained Florence-2 model for generating text from images
        vision_processor : AutoProcessor
            The processor for preparing input data and decoding output from the model
        """
        # Define device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load Florence-2 model for image-to-text conversion
        model_path = os.environ.get("FLORENCE_PATH")

        # Check if florence model exist
        if not os.path.exists(model_path):
            self.vision_model = AutoModelForCausalLM.from_pretrained(
                "microsoft/Florence-2-base",
                trust_remote_code=True,
                torch_dtype=torch.float32,
            ).to(self.device)

            self.vision_processor = AutoProcessor.from_pretrained(
                "microsoft/Florence-2-base", trust_remote_code=True
            )

        else:
            self.vision_model = AutoModelForCausalLM.from_pretrained(
                model_path,
                trust_remote_code=True,
                torch_dtype=torch.float32,
            ).to(self.device)

            self.vision_processor = AutoProcessor.from_pretrained(
                model_path, trust_remote_code=True
            )

    def get_vision_model_processor(self) -> Tuple[AutoModelForCausalLM, AutoProcessor]:
        """Returns the tuple of vision model and processor used in the class"""
        return self.vision_model, self.vision_processor

    def predict(self, inputs: dict) -> str:
        """
        Generate text predictions from the Florence-2 model based on the provided
        inputs, including input ids, attention mask, and pixel values

        Parameters
        ----------
        inputs : dict
            A dictionary containing preprocessed inputs for the model, including
            input ids, attention mask, and pixel values

        Returns
        -------
        str
            The generated text output from the model, decoded from the generated
            token IDs
        """
        # Generate token id for the output
        generated_ids = self.vision_model.generate(
            input_ids=inputs["input_ids"].to(self.device),
            pixel_values=inputs["pixel_values"].to(self.device),
            max_new_tokens=1024,
            early_stopping=False,
            do_sample=False,
            num_beams=3,
        )

        # Decode the generated token id to retrieve text output
        generated_text = self.vision_processor.batch_decode(
            generated_ids, skip_special_tokens=False
        )[0]

        return generated_text

    def __call__(self, image: PILImage.Image, task_prompt: str) -> dict:
        """
        Prepares the input for the Florence model, runs inference, and processes
        the generated text output based on the given image and task prompt

        Parameters
        ----------
        image : PIL.Image
            The image input to be processed by the model
        task_prompt : str
            A text prompt that guides the model on what to generate based on the
            image

        Returns
        -------
        dict
            A dictionary containing the processed output based on the generated
            text and the specified task prompt, along with additional information
        """
        # Prepare input for the florence model
        inputs = self.vision_processor(
            text=task_prompt, images=image, return_tensors="pt"
        ).to("cuda")

        # Model inferences
        generated_text = self.predict(inputs)

        # Result postprocessing
        parsed_answer = self.vision_processor.post_process_generation(
            generated_text, task=task_prompt, image_size=(image.width, image.height)
        )

        return parsed_answer
