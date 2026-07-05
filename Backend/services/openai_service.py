from openai import AsyncOpenAI
from config import OPENAI_API_KEY
import base64


client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def generate_thumbnail(prompt_name: str, style_prompt: str, headshot_url: str) -> bytes:
    """
        Use the Responses API withIgpt-image-2 as a built-in image_generation
        tool.
        Pass the headshot URL directly as an input_image.
        Returns raw PNG bytes. 
    """
    full_prompt = (
        f"{style_prompt}\n\n"
        f"User request: {prompt_name}\n\n"
        "IMPORTANT: The generated thumbnail MUST prominently feature the person"
        "shown in the provided reference headshot photo. Keep their likeness accurate."
    )
    # response = await client.responses.create(
    #     model="gpt-4o",
    #     input=[
    #         {
    #             "role": "user",
    #             "content": [
    #                 {"type": "input_text", "text": full_prompt},
    #                 {
    #                     "type": "input_image",
    #                     "image_url": headshot_url,
    #                 },
    #             ],
    #         }
    #     ],
    #     tools=[
    #         {
    #             "type": "image_generation",
    #             "model": "gpt-image-2",
    #             "image_generation": {
    #                 "size": "1536x1024",
    #                 "format": "png",
    #                 "quality": "high",
    #             },
    #         }
    #     ],
    # )

    # for item in response.output:
    #     if item.type == "image_generation_call" and item.result:
    #         return base64.b64decode(item.result)
    
    # raise RuntimeError("No image generated in the response.")


    response = await client.responses.create(
        model="gpt-4.1-nano",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": full_prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": headshot_url,
                    },
                ],
            }
        ],
        tools=[
            {
                "type": "image_generation"
            }
        ],
    )

    for output in response.output:
        if output.type == "image_generation_call":
            return base64.b64decode(output.result)

    raise RuntimeError("No image returned")