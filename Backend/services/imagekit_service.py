# import libraries
# import values from config file -> imagekitPublicKey, imagekitPrivateKey, imagekitUrlEndpoint
from imagekitio import ImageKit
from config import IMAGEKIT_PUBLIC_KEY, IMAGEKIT_PRIVATE_KEY, IMAGEKIT_URL_ENDPOINT

    


#  create the instance of imagekit using only private key
imagekit = ImageKit(
    private_key=IMAGEKIT_PRIVATE_KEY
)

# function upload files which will take file_bytes, file_name, folder and content_type
# inside function call upload method of imagekit instance and pass the parameters use documentation of imagekit to know the parameters and their types
def upload_file(file_bytes: bytes, file_name: str, folder: str, content_type: str) :
    
    result = imagekit.files.upload(
        file=file_bytes,
        file_name=file_name,
        folder=folder,
        is_private_file=False,
        use_unique_file_name=True,
    )

    return result.url

def get_variants(base_url: str) -> dict:
    """Return 3 sizes variant URLs using imagekit transformations."""
    return {
        "youtube": f"{base_url}?tr=w-1280, h-720, c-maintain_ratio, fo-auto",
        "shorts": f"{base_url}?tr=w-1080, h-1920, c-maintain_ratio, fo-auto",
        "square": f"{base_url}?tr=w-1080, h-1080, c-maintain_ratio, fo-auto",
    }
