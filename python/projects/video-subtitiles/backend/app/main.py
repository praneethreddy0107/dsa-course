from fastapi import FastAPI, UploadFile, File, HTTPException
from google.cloud import storage, pubsub_v1
import uuid
import json
from app.config import PROJECT_ID, BUCKET_NAME, PUBSUB_TOPIC
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize GCP clients
try:
    storage_client = storage.Client()
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)
except Exception as e:
    logger.error(f"Failed to initialize GCP clients: {str(e)}")
    raise

@app.post("/upload")
async def upload_video(
    video: UploadFile = File(...),
    source_language: str = "en",
    target_languages: str = "[]"
):
    if not video:
        raise HTTPException(status_code=400, detail="No video file provided")
    
    try:
        # Parse target languages
        target_langs = json.loads(target_languages)
        if not target_langs:
            raise HTTPException(status_code=400, detail="At least one target language is required")

        # Generate unique video ID
        video_id = str(uuid.uuid4())
        video_filename = f"videos/{video_id}/{video.filename}"
        
        # Upload video to GCS
        logger.info(f"Uploading {video_filename} to bucket {BUCKET_NAME}")
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(video_filename)
        blob.upload_from_file(video.file, content_type=video.content_type)
        logger.info(f"Uploaded {video_filename} successfully")

        # Publish message to Pub/Sub
        message_data = {
            "video_id": video_id,
            "gcs_video_path": video_filename,
            "source_language": source_language,
            "target_languages": target_langs
        }
        logger.info(f"Publishing message to {PUBSUB_TOPIC}: {message_data}")
        publisher.publish(topic_path, json.dumps(message_data).encode("utf-8"))
        logger.info("Message published")

        return {
            "message": "Video uploaded successfully. Processing started.",
            "video_id": video_id
        }
    except Exception as e:
        logger.error(f"Error in upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading video: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "OK"}