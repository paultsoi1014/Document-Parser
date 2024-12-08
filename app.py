import base64
import os
import re
import subprocess
import tempfile

from dotenv import load_dotenv
from io import BytesIO
from pydantic import BaseModel
from PIL import Image as PILImage
from typing import Any, Optional, Tuple, List

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

from utils.florence import FlorenceVisionModel
from utils.response import DocumentResponse


load_dotenv(override=True)


class PhiloDocumentParser:
    """
    A class to parse various document formats (PDF, DOC, PPT) and convert images
    within them into textual descriptions using the marker and Florence-2 vision
    model
    """

    def __init__(self):
        """
        Initializes the PhiloDocumentParser, loading necessary models for parsing
        documents and initializing the marker and Florence vision model for
        document conversion

        Attributes
        ----------
        florence : FlorenceVisionModel
            An instance of the Florence vision model for image-to-text conversion
        """
        # Init converter for converting PDF into markdown format
        self.converter = PdfConverter(artifact_dict=create_model_dict())

        # Init florence vision language model for image to text conversion
        self.florence = FlorenceVisionModel()

    @staticmethod
    def _encode_image(images: dict, pdf_result: DocumentResponse) -> None:
        """
        Encodes images to base64 and adds them to the DocumentResponse

        Parameters
        ----------
        images : dict
            A dictionary containing image filenames as keys and PIL images as values
        pdf_result : DocumentResponse
            The DocumentResponse instance to which the encoded images will be added
        """
        for filename, image in images.items():
            # Save image as PNG
            image.save(filename, "PNG")

            # Read the saved image as byte
            with open(filename, "rb") as f:
                image_bytes = f.read()

            # Convert image into base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            # Add to document response instance
            pdf_result.add_image(image_name=filename, image_data=image_base64)

            # Remove the temporary file
            os.remove(filename)
            f.close()

            return None

    def _image_to_text_conversion(self, document: str, images: List[PILImage.Image]):
        """
        Converts images in the document to text and replaces image references
        with their textual descriptions.

        Parameters
        ----------
        document : str
            The markdown document string containing image references
        images : List[PILImage.Image]
            A list of PIL images to be processed for text extraction

        Returns
        -------
        str
            The document string with image references replaced by their
            corresponding text representations
        """
        for filename, image in images.items():
            # Convert image into text
            text_representation = self.parse_img(
                image, image_name=filename, task_prompt="<MORE_DETAILED_CAPTION>"
            ).text

            # Pattern to find the image by name and replace with the representation
            pattern = rf"!\[{filename}\]\({filename}\)"

            # Replace with the text representation in the markdown text
            document = re.sub(pattern, text_representation, document)

        return document

    def parse_pdf(self, input_data: Optional[Tuple[str, bytes]]):
        """
        Parses a PDF document and extracts its content, including images,
        converting them to text

        Parameters
        ----------
        input_data : Optional[Tuple[str, bytes]]
            The input PDF data, which can be a file path or raw bytes

        Returns
        -------

        """
        # Check input data format
        if isinstance(input_data, str) and input_data.endswith(".pdf"):
            input_path = input_data
            cleanup_tempfile = False

        elif isinstance(input_data, bytes):
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".pdf"
            ) as temp_pdf_file:
                temp_pdf_file.write(input_data)
                temp_pdf_path = temp_pdf_file.name

            input_path = temp_pdf_path
            cleanup_tempfile = True

        # Convert the document content into markdown
        rendered = self.converter(input_path)
        full_text, _, images = text_from_rendered(rendered)

        # Image to text conversion
        full_text_refined = self._image_to_text_conversion(
            document=full_text, images=images
        )

        # Store parsed result
        parse_pdf_result = DocumentResponse(text=full_text_refined)
        self._encode_image(images, parse_pdf_result)

        # Delete temporarily file
        if cleanup_tempfile:
            os.remove(input_path)

        return parse_pdf_result

    def parse_doc_ppt(
        self, input_data: Optional[Tuple[str, bytes]]
    ) -> DocumentResponse:
        """
        Parses DOC or PPT documents, converts them to PDF, and extracts text
        and images from them.

        Parameters
        ----------
        input_data : Optional[Tuple[str, bytes]]
            The input DOC or PPT data, which can be a file path or raw bytes

        Returns
        -------
        DocumentResponse
            The parsed result containing extracted text and images
        """
        # Check input data format
        if isinstance(input_data, str) and (
            input_data.endswith(".ppt")
            or input_data.endswith(".pptx")
            or input_data.endswith(".doc")
            or input_data.endswith(".docx")
        ):
            input_path = input_data

        elif isinstance(input_data, bytes):
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(input_data)
                tmp_file.flush()
                input_path = tmp_file.name

        # Convert the document into pdf format
        if input_path.endswith((".ppt", ".pptx", ".doc", ".docx")):
            output_dir = tempfile.mkdtemp()
            command = [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir,
                input_path,
            ]
            subprocess.run(command, check=True)
            output_pdf_path = os.path.join(
                output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
            )
            input_path = output_pdf_path

        # Convert the document content into markdown
        rendered = self.converter(input_path)
        full_text, _, images = text_from_rendered(rendered)

        # Image to text conversion
        full_text_refined = self._image_to_text_conversion(
            document=full_text, images=images
        )

        # Store parsed result
        parse_doc_ppt_result = DocumentResponse(text=full_text_refined)
        self._encode_image(images, parse_doc_ppt_result)

        if input_data != input_path:
            os.remove(input_path)

        return parse_doc_ppt_result

    def parse_img(
        self,
        image_data: Optional[Tuple[str, bytes]],
        image_name: Optional[str] = None,
        task_prompt: Optional[str] = "<MORE_DETAILED_CAPTION>",
    ) -> DocumentResponse:
        """
        Parses an image, converting it to text using the Florence vision model

        Parameters
        ----------
        image_data : Optional[Tuple[str, bytes]]
            The input image data, which can be bytes or a base64-encoded string
        image_name : Optional[str], optional
            The name of the image file, used for metadata (default is None)
        task_prompt : str, optional
            A prompt to guide the model on what to generate (default is
            "<MORE_DETAILED_CAPTION>")

        Returns
        -------
        DocumentResponse
            The result containing the generated text and metadata
        """
        # Check input data format
        if isinstance(image_data, bytes):
            pil_image = PILImage.open(BytesIO(image_data))

        elif isinstance(image_data, str):
            image_bytes = base64.b64decode(image_data)
            pil_image = PILImage.open(BytesIO(image_bytes))

        elif isinstance(image_data, PILImage.Image):
            pil_image = image_data

        else:
            raise ValueError(
                "Invalid input data format. Expected image bytes or image file path."
            )

        # image-to-text conversion
        response = self.florence(pil_image, task_prompt=task_prompt)

        # Store parsed result
        if image_name:
            parsed_img_result = DocumentResponse(
                text=str(response[task_prompt]), metadata={"image_name": image_name}
            )
        else:
            parsed_img_result = DocumentResponse(text=str(response[task_prompt]))

        return parsed_img_result


if __name__ == "__main__":
    document_parser = PhiloDocumentParser()
    parse_result = document_parser.parse_pdf("./playground/test_3.pdf")
    print(parse_result.text)
