import React, { useState } from 'react';
import axios from 'axios';
import UploadForm from './components/UploadForm';
import StatusDisplay from './components/StatusDisplay';
import VideoOutput from './components/VideoOutput';
import './App.css';

const App = () => {
  const [videoFile, setVideoFile] = useState(null);
  const [sourceLanguage, setSourceLanguage] = useState('en'); // Default: English
  const [targetLanguages, setTargetLanguages] = useState([]); // Array of { value, label }
  const [videoUrl, setVideoUrl] = useState('');
  const [subtitleUrls, setSubtitleUrls] = useState([]); // Array of { url, language, languageName }
  const [status, setStatus] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!videoFile) {
      setStatus('Please select a video file.');
      return;
    }
    if (!targetLanguages.length) {
      setStatus('Please select at least one target language.');
      return;
    }

    setUploading(true);
    setStatus('Uploading and processing...');
    setVideoUrl('');
    setSubtitleUrls([]);

    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('source_language', sourceLanguage);
    formData.append('target_languages', JSON.stringify(targetLanguages.map((lang) => lang.value)));

    try {
      // Replace with your actual backend API endpoint
      const response = await axios.post('http://your-backend-api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const { video_url, subtitles } = response.data;
      setVideoUrl(video_url);
      setSubtitleUrls(
        subtitles.map((sub) => ({
          url: sub.subtitle_url,
          language: sub.language,
          languageName: sub.language_name,
        }))
      );
      setStatus('Processing complete! Video and subtitles are ready.');
    } catch (error) {
      console.error('Error uploading video:', error);
      setStatus('Error processing video. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="app-container">
      <h1>Video Subtitle Generator</h1>
      <UploadForm
        videoFile={videoFile}
        setVideoFile={setVideoFile}
        sourceLanguage={sourceLanguage}
        setSourceLanguage={setSourceLanguage}
        targetLanguages={targetLanguages}
        setTargetLanguages={setTargetLanguages}
        uploading={uploading}
        handleSubmit={handleSubmit}
      />
      <StatusDisplay status={status} />
      {videoUrl && subtitleUrls.length > 0 && (
        <VideoOutput videoUrl={videoUrl} subtitleUrls={subtitleUrls} />
      )}
    </div>
  );
};

export default App;