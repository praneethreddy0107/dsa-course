import React from 'react';

const StatusDisplay = ({ status }) => {
  return (
    <div className="status-section">
      <p>{status}</p>
    </div>
  );
};

export default StatusDisplay;