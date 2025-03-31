import React from 'react';
import Select from 'react-select';

const UploadForm = ({
  videoFile,
  setVideoFile,
  sourceLanguage,
  setSourceLanguage,
  targetLanguages,
  setTargetLanguages,
  uploading,
  handleSubmit,
}) => {
  const sourceLanguages = [
    { value: 'en', label: 'English' },
    { value: 'hi', label: 'Hindi' },
    { value: 'ta', label: 'Tamil' },
    { value: 'te', label: 'Telugu' },
  ];

  const indianLanguages = [
    { value: 'hi', label: 'Hindi' },
    { value: 'ta', label: 'Tamil' },
    { value: 'te', label: 'Telugu' },
    { value: 'bn', label: 'Bengali' },
    { value: 'mr', label: 'Marathi' },
    { value: 'gu', label: 'Gujarati' },
    { value: 'kn', label: 'Kannada' },
    { value: 'ml', label: 'Malayalam' },
    { value: 'pa', label: 'Punjabi' },
    { value: 'or', label: 'Odia' },
  ];

  const handleFileChange = (e) => {
    setVideoFile(e.target.files[0]);
  };

  return (
    <div className="upload-section">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="video">Upload Video:</label>
          <input
            type="file"
            id="video"
            accept="video/*"
            onChange={handleFileChange}
            disabled={uploading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="source-language">Source Language:</label>
          <select
            id="source-language"
            value={sourceLanguage}
            onChange={(e) => setSourceLanguage(e.target.value)}
            disabled={uploading}
          >
            {sourceLanguages.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="target-languages">Target Languages:</label>
          <Select
            id="target-languages"
            isMulti
            options={indianLanguages}
            value={targetLanguages}
            onChange={setTargetLanguages}
            isDisabled={uploading}
            placeholder="Select target languages..."
          />
        </div>

        <button type="submit" disabled={uploading || !targetLanguages.length}>
          {uploading ? 'Processing...' : 'Upload & Generate Subtitles'}
        </button>
      </form>
    </div>
  );
};

export default UploadForm;