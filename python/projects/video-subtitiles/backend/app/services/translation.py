import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))  # Add backend/ to path

from google.cloud import pubsub_v1, storage, speech, translate_v2 as translate
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.config import PROJECT_ID, BUCKET_NAME, PUBSUB_TOPIC

storage_client = storage.Client()
subscriber = pubsub_v1.SubscriberClient()
speech_client = speech.SpeechClient()
translate_client = translate.Client()
publisher = pubsub_v1.PublisherClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, "transcription-translation-sub")
topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

def transcribe_audio(gcs_audio_uri, source_language):
    audio = speech.RecognitionAudio(uri=gcs_audio_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        language_code=source_language,
        enable_automatic_punctuation=True
    )
    response = speech_client.recognize(config=config, audio=audio)
    return " ".join(result.alternatives[0].transcript for result in response.results)

def translate_text(text, target_language):
    result = translate_client.translate(text, target_language=target_language)
    return result["translatedText"]

def generate_srt(transcript, language):
    return f"1\n00:00:00,000 --> 00:00:10,000\n{transcript}"

def callback(message):
    try:
        data = json.loads(message.data.decode("utf-8"))
        video_id = data["video_id"]
        gcs_audio_path = data["gcs_audio_path"]
        source_language = data["source_language"]
        target_languages = data["target_languages"]

        logger.info(f"Transcribing video_id: {video_id}")

        gcs_audio_uri = f"gs://{BUCKET_NAME}/{gcs_audio_path}"
        transcript = transcribe_audio(gcs_audio_uri, source_language)
        logger.info(f"Transcript: {transcript}")

        bucket = storage_client.bucket(BUCKET_NAME)
        subtitle_urls = []
        for lang in target_languages:
            translated_text = translate_text(transcript, lang)
            srt_content = generate_srt(translated_text, lang)
            srt_path = f"subtitles/{video_id}/{lang}.srt"
            blob = bucket.blob(srt_path)
            blob.upload_from_string(srt_content, content_type="text/srt")
            subtitle_urls.append({
                "subtitle_url": f"gs://{BUCKET_NAME}/{srt_path}",
                "language": lang,
                "language_name": lang.capitalize()
            })
            logger.info(f"Uploaded {lang} subtitle to {srt_path}")

        completion_message = {
            "video_id": video_id,
            "gcs_video_path": f"videos/{video_id}/{data['gcs_audio_path'].split('/')[-1]}",
            "subtitle_urls": subtitle_urls
        }
        publisher.publish(topic_path, json.dumps(completion_message).encode("utf-8"))
        logger.info(f"Published completion: {completion_message}")

        message.ack()
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        message.nack()

if __name__ == "__main__":
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