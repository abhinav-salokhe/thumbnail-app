import asyncio
import logging

from sqlmodel import Session, select
from database import engine
from models import Job, Thumbnail
from services.openai_service import generate_thumbnail
from services.imagekit_service import upload_file

logger = logging.getLogger(__name__)



# prompt engineering for different styles of thumbnails
STYLES = {
    "bold_dramatic": (
        "Create a bold, dramatic YouTube thumbnail with high contrast, "
        "cinematic lighting, dark moody background, and powerful composition."
        "The person's face should be prominent with a dramatic expression."
    ),
    "clean_minimal": (
        "Create a clean, minimal YouTube thumbnail with bright lighting, "
        "white/light background, modern professional aesthetic, plenty of "
        "whitespace, and sharp clean composition. The person should look "
        "approachable and professional."
    ),
    "vibrant_energetic":(
        "Create a vibrant, energetic YouTube thumbnail with colorful gradients, "
        "dynamic angles, eye-catching pop-art style colors, and energetic "
        "Composition. The person should have an excited or engaging expression."
    ),
}


STYLE_ORDER = ["bold_dramatic", "clean_minimal", "vibrant_energetic"]

async def generate_single_thumbnail(thumbnail_id:str, prompt_name:str,headshot_url:str):
    # Db mark -> generating thumbnail
    with Session(engine) as session:
        thumb = session.get(Thumbnail, thumbnail_id)
        thumb.status = "generating"
        style_name = thumb.style_name
        session.add(thumb)
        session.commit() 

    style_prompt = STYLES[style_name]

    # AI call -> generate thumbnail
    try:
        image_byte = await generate_thumbnail(prompt_name, style_prompt, headshot_url)
        with Session(engine) as session:
            thumb = session.get(Thumbnail, thumbnail_id)
            job_id = thumb.job_id
            

        # upload to imagekit
        url = upload_file(
            # file_bytes=image_byte,
            # file_name=f"{thumbnail_id}.png",
            # file_path=f"thumbnails/{job_id}/",
            file_bytes=image_byte,
            file_name=f"{thumbnail_id}.png",
            folder=f"/thumbnails/{job_id}",
            content_type="image/png",
        )
    # DB call save the url -> mark uploaded
        with Session(engine) as session:
            thumb = session.get(Thumbnail, thumbnail_id)
            thumb.imagekit_url = url
            thumb.status = "uploaded"
            session.add(thumb)
            session.commit()
        
        logger.info(f"Thumbnail {thumbnail_id} generated and uploaded successfully.")
    except Exception as e:
        logger.error(f"Error occurred while generating thumbnail {thumbnail_id}: {e}")
        with Session(engine) as session:
            thumb = session.get(Thumbnail, thumbnail_id)
            thumb.status = "error"
            thumb.error_message = str(e)[:500]  # Truncate error message to avoid exceeding column length
            session.add(thumb)
            session.commit()



# async def process_job(job_id:str):
#     # mark job as processing
#     with Session(engine) as session:
#         job = session.get(Job, job_id)
#         job.status = "processing"
#         prompt_name = job.prompt_name
#         headshot_url = job.headshot_url
#         session.add(job)
#         session.commit()
    
#         # find all thumbnails for the job
#         thumbnails = session.exec(
#             select(Thumbnail).where(Thumbnail.job_id == job_id)
#         ).all()
#         thumbnail_ids = [t.id for t in thumbnails]

#         # start one worker for each thumbnail
#         tasks=[
#             generate_single_thumbnail(tid, prompt_name, headshot_url)
#             for tid in thumbnail_ids
#         ]

#         # run all thumbnail concurrently and wait for them to finish
#         await asyncio.gather(*tasks, return_exceptions=True)

#         # wait for all workers to finish
#         with Session(engine) as session:
#             thumbnails = session.exec(
#                 select(Thumbnail).where(Thumbnail.job_id == job_id)
#             ).all()
#             all_failed =all(t.status == "failed" for t in thumbnails)
#             job = session.get(Job,job_id)
            
#         # mark job as completed/failed
#             job.status = "failed" if all_failed else "completed"
#             session.add(job)
#             session.commit()



async def process_job(job_id:str):
    # mark job as processing
    with Session(engine) as session:
        job = session.get(Job, job_id)
        job.status = "processing"
        prompt_name = job.prompt_name
        headshot_url = job.headshot_url
        session.add(job)
        session.commit()
    
        # find all thumbnails for the job
        thumbnails = session.exec(
            select(Thumbnail).where(Thumbnail.job_id == job_id)
        ).all()
        thumbnail_ids = [t.id for t in thumbnails]

        # start one worker for each thumbnail
        tasks=[
            generate_single_thumbnail(tid, prompt_name, headshot_url)
            for tid in thumbnail_ids
        ]

        # run all thumbnail concurrently and wait for them to finish
        await asyncio.gather(*tasks, return_exceptions=True)

        # wait for all workers to finish
        with Session(engine) as session:
            thumbnails = session.exec(
                select(Thumbnail).where(Thumbnail.job_id == job_id)
            ).all()
            all_failed =all(t.status == "failed" for t in thumbnails)
            job = session.get(Job,job_id)
            
        # mark job as completed/failed
            job.status = "failed" if all_failed else "completed"
            session.add(job)
            session.commit()


