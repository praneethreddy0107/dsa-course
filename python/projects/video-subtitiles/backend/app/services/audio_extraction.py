from google.cloud import pubsub_v1, storage
import subprocess
import os
import json
from app.config import PROJECT_ID, BUCKET_NAME, PUBSUB_SUBSCRIPTION, PUBSUB_TOPIC

subscriber = pubsub_v1.SubscriberClient()
storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, PUBSUB_SUBSCRIPTION)
topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

def extract_audio(video_path, output_audio_path):
    subprocess.run(
        ["ffmpeg", "-i", video_path, "-vn", "-acodec", "mp3", output_audio_path],
        check=True
    )

def callback(message):
    data = json.loads(message.data.decode("utf-8"))
    video_id = data["video_id"]
    gcs_video_path = data["gcs_video_path"]
    source_language = data["source_language"]
    target_languages = data["target_languages"]

    # Download video from GCS
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(gcs_video_path)
    local_video_path = f"/tmp/{video_id}.mp4"
    blob.download_to_filename(local_video_path)

    # Extract audio
    local_audio_path = f"/tmp/{video_id}.mp3"
    extract_audio(local_video_path, local_audio_path)

    # Upload audio to GCS
    audio_gcs_path = f"audio/{video_id}.mp3"
    audio_blob = bucket.blob(audio_gcs_path)
    audio_blob.upload_from_filename(local_audio_path)

    # Publish to next step (transcription)
    next_message = {
        "video_id": video_id,
        "audio_gcs_path": audio_gcs_path,
        "source_language": source_language,
        "target_languages": target_languages
    }
    publisher.publish(topic_path, json.dumps(next_message).encode("utf-8"))

    # Cleanup
    os.remove(local_video_path)
    os.remove(local_audio_path)
    message.ack()

if __name__ == "__main__":
    subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")
    while True:
        pass  # Keep the script running