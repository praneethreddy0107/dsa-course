import os
import json
import logging
from google.cloud import pubsub_v1, storage
import speech_recognition as sr
from googletrans import Translator
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET_NAME = os.getenv("BUCKET_NAME")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC")
SUBSCRIPTION_NAME = "transcription-translation-sub"

storage_client = storage.Client()
subscriber = pubsub_v1.SubscriberClient()
publisher = pubsub_v1.PublisherClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)
topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

def transcribe_audio(audio_path, source_language):
    recognizer = sr.Recognizer()
    wav_path = audio_path.replace(".mp3", ".wav")
    subprocess.run(
        ["ffmpeg", "-i", audio_path, wav_path],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)
    try:
        transcript = recognizer.recognize_sphinx(audio, language=source_language)
        return transcript
    except sr.UnknownValueError:
        return "Could not understand audio"
    finally:
        os.remove(wav_path)

def translate_text(text, target_language):
    translator = Translator()
    return translator.translate(text, dest=target_language).text

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

        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_audio_path)
        local_audio_path = f"/tmp/{video_id}.mp3"
        blob.download_to_filename(local_audio_path)
        logger.info(f"Downloaded {gcs_audio_path} to {local_audio_path}")

        transcript = transcribe_audio(local_audio_path, source_language)
        logger.info(f"Transcript: {transcript}")

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
            "gcs_video_path": f"videos/{video_id}/{gcs_audio_path.split('/')[-1]}",
            "subtitle_urls": subtitle_urls
        }
        publisher.publish(topic_path, json.dumps(completion_message).encode("utf-8"))
        logger.info(f"Published completion: {completion_message}")

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