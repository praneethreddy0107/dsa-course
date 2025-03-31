import React from 'react';
import ReactPlayer from 'react-player';

const VideoOutput = ({ videoUrl, subtitleUrl, targetLanguage }) => {
  return (
    <div className="output-section">
      <h2>Output</h2>
      <ReactPlayer
        url={videoUrl}
        controls
        width="100%"
        height="auto"
        config={{
          file: {
            attributes: {
              crossOrigin: 'anonymous',
            },
            tracks: [
              {
                kind: 'subtitles',
                src: subtitleUrl,
                srcLang: targetLanguage,
                default: true,
              },
            ],
          },
        }}
      />
    </div>
  );
};

export default VideoOutput;