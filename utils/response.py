import base64

from io import BytesIO
from PIL import Image as PILImage
from pydantic import BaseModel, Field
from typing import Callable, List, Dict, Any, Union

from utils.process import encode_image_to_base64


class ImageResponse(BaseModel):
    image: str = ""
    image_name: str = ""
    image_info: Union[Dict[str, Any], None] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    text: str = ""
    images: List[ImageResponse] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunks: List[str] = Field(default_factory=list)

    def add_image(
        self,
        image_name: str,
        image_data: Union[str, PILImage.Image],
        image_info: Union[Dict[str, Any], None] = {},
    ):
        if isinstance(image_data, str):
            # Decode image if image is base64 encoded
            image_bytes = base64.b64decode(image_data)
            pil_image = PILImage.open(BytesIO(image_bytes))

        # Use the image directly if it is already a PIL.Image instance
        elif isinstance(image_data, PILImage.Image):
            pil_image = image_data

        # Append as list of image object
        new_image = ImageResponse(
            image=encode_image_to_base64(pil_image),
            image_name=image_name,
            image_info=image_info,
        )
        self.images.append(new_image)

        return None
