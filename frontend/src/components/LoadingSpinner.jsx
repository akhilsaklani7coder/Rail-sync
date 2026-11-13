import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ text = "Loading data...", size = 32 }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-slate-500">
      <Loader2 className="animate-spin text-orange-600 mb-3" size={size} />
      <span className="text-sm font-medium tracking-wide">{text}</span>
    </div>
  );
};

export default LoadingSpinner;
