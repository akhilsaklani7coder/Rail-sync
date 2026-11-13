import React from 'react';
import { CheckCircle2, XCircle, Clock, AlertCircle } from 'lucide-react';

const StatusBadge = ({ status }) => {
  const norm = (status || '').toUpperCase();

  if (norm === 'CONFIRMED' || norm === 'SUCCESS') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <CheckCircle2 size={13} className="text-emerald-600" />
        {norm}
      </span>
    );
  }

  if (norm === 'CANCELLED' || norm === 'FAILED') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
        <XCircle size={13} className="text-rose-600" />
        {norm}
      </span>
    );
  }

  if (norm === 'PENDING') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
        <Clock size={13} className="text-amber-600" />
        {norm}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
      <AlertCircle size={13} className="text-slate-500" />
      {norm || 'UNKNOWN'}
    </span>
  );
};

export default StatusBadge;
