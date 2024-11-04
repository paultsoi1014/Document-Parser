import base64

from io import BytesIO
from PIL import Image as PILImage


def encode_image_to_base64(image: PILImage.Image) -> str:
    """
    Encodes a PIL Image object to a base64-encoded string

    Parameters
    ----------
    image: PILImage.Image
        The image to be encoded, represented as a PIL Image object

    Returns
    -------
    str
        The base64-encoded string representation of the image
    """
    # Create a BytesIO buffer to store image data temporarily in memory
    buffered = BytesIO()

    # Save the PIL image into the buffer in JPEG format with specified quality
    image.save(buffered, format="JPEG", quality=85)

    # Encode the buffer's binary image data to a base64 string and decode to utf-8 for easier handling
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_base64
