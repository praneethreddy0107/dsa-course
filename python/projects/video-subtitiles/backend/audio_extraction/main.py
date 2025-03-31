import os
import json
import logging
from google.cloud import pubsub_v1, storage
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config from environment variables (set in GKE)
PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET_NAME = os.getenv("BUCKET_NAME")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC")
SUBSCRIPTION_NAME = "audio-extraction-sub"

storage_client = storage.Client()
subscriber = pubsub_v1.SubscriberClient()
publisher = pubsub_v1.PublisherClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)
topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

def extract_audio(video_path, output_audio_path):
    subprocess.run(
        ["ffmpeg", "-i", video_path, "-vn", "-acodec", "mp3", output_audio_path],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def callback(message):
    try:
        data = json.loads(message.data.decode("utf-8"))
        video_id = data["video_id"]
        gcs_video_path = data["gcs_video_path"]
        source_language = data["source_language"]
        target_languages = data["target_languages"]

        logger.info(f"Processing video_id: {video_id}")

        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_video_path)
        local_video_path = f"/tmp/{video_id}.mp4"
        blob.download_to_filename(local_video_path)
        logger.info(f"Downloaded {gcs_video_path} to {local_video_path}")

        local_audio_path = f"/tmp/{video_id}.mp3"
        extract_audio(local_video_path, local_audio_path)
        logger.info(f"Extracted audio to {local_audio_path}")

        audio_gcs_path = f"audio/{video_id}.mp3"
        audio_blob = bucket.blob(audio_gcs_path)
        audio_blob.upload_from_filename(local_audio_path)
        logger.info(f"Uploaded audio to {audio_gcs_path}")

        next_message = {
            "video_id": video_id,
            "gcs_audio_path": audio_gcs_path,
            "source_language": source_language,
            "target_languages": target_languages
        }
        publisher.publish(topic_path, json.dumps(next_message).encode("utf-8"))
        logger.info(f"Published transcription message: {next_message}")

        os.remove(local_video_path)
        os.remove(local_audio_path)

        message.ack()
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        message.nack()

def main():
    try:
        subscriber.create_subscription(
            name=subscription_path,
            topic=topic_path
        )
        logger.info(f"Created subscription: {subscription_path}")
    except Exception as e:
        logger.info(f"Subscription {subscription_path} already exists or error: {str(e)}")

    logger.info(f"Listening for messages on {subscription_path}...")
    subscriber.subscribe(subscription_path, callback=callback)
    while True:
        pass

if __name__ == "__main__":
    main()