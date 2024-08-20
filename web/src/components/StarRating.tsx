import React from 'react';

interface StarRatingProps {
  rating: number;
}

const StarRating: React.FC<StarRatingProps> = ({ rating }) => {

    const percentage = (rating / 5) * 100; 

  return (
      <svg
        width="24"
        height="24"
      >
        <defs>
          <linearGradient id="starGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset={`${percentage}%`} stopColor="#FFE45A" />
            <stop offset={`${percentage}%`} stopColor="transparent" />
          </linearGradient>
        </defs>
        <g fill="url(#starGrad)" stroke="#FFE45A" strokeWidth="1">
          <path
            d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 3.73L5.82 21z"
          />
        </g>
      </svg>
        );
};

export default StarRating;