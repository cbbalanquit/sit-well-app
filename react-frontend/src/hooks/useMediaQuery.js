// src/hooks/useMediaQuery.js
import { useState, useEffect } from 'react';

export const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    
    // Update the state initially
    if (media.matches !== matches) {
      setMatches(media.matches);
    }
    
    // Create a listener function to respond to changes
    const listener = () => {
      setMatches(media.matches);
    };
    
    // Add the listener
    media.addEventListener('change', listener);
    
    // Clean up the listener when the component unmounts
    return () => {
      media.removeEventListener('change', listener);
    };
  }, [query, matches]);

  return matches;
};