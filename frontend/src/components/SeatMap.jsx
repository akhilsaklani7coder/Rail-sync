import React, { useState } from 'react';
import { Armchair, Check, Lock, Info } from 'lucide-react';

const SeatMap = ({ coaches, selectedSeats = [], onSeatToggle, maxSelectable = 6 }) => {
  const [activeCoachIdx, setActiveCoachIdx] = useState(0);

  if (!coaches || coaches.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400 bg-white rounded-3xl border border-slate-200">
        No coach seat map layout available for this train.
      </div>
    );
  }

  const currentCoach = coaches[activeCoachIdx] || coaches[0];

  return (
    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
      
      {/* Coach Selector Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-4">
        <div>
          <h4 className="font-black text-slate-900 text-lg">Interactive Coach Seat Map</h4>
          <p className="text-xs text-slate-500">Pick preferred seats or let our C++ allocator choose optimal contiguous seats automatically.</p>
        </div>
        <div className="flex items-center gap-2 overflow-x-auto">
          {coaches.map((c, idx) => (
            <button
              key={c.id}
              onClick={() => setActiveCoachIdx(idx)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer shrink-0 ${
                activeCoachIdx === idx
                  ? 'bg-slate-950 text-white shadow-md'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              Coach {c.coach_number} ({c.coach_type})
            </button>
          ))}
        </div>
      </div>

      {/* Visual Legend */}
      <div className="flex items-center gap-6 py-2 text-xs font-medium text-slate-600 flex-wrap">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-lg bg-emerald-50 border-2 border-emerald-500 flex items-center justify-center"></div>
          <span className="font-semibold text-slate-700">Available</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-lg bg-orange-500 border-2 border-orange-600 flex items-center justify-center text-white">
            <Check size={12} />
          </div>
          <span className="font-semibold text-slate-700">Selected</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-lg bg-slate-200 border-2 border-slate-300 flex items-center justify-center text-slate-400">
            <Lock size={12} />
          </div>
          <span className="font-semibold text-slate-700">Booked (Row-Locked)</span>
        </div>
        <div className="ml-auto text-xs text-slate-500 bg-slate-50 px-3 py-1 rounded-full border border-slate-200">
          Selected: <span className="font-black text-orange-600">{selectedSeats.length}</span> / {maxSelectable} max
        </div>
      </div>

      {/* Coach Interior Layout Visual */}
      <div className="p-6 sm:p-8 bg-slate-50 rounded-3xl border border-slate-200 space-y-4">
        <div className="flex items-center justify-between text-xs font-bold text-slate-400 uppercase tracking-widest px-2">
          <span>Coach {currentCoach.coach_number} • Class {currentCoach.coach_type}</span>
          <span className="flex items-center gap-1 text-[11px] font-semibold text-slate-400">
            <span>Central Corridor</span>
            <span>→</span>
          </span>
        </div>

        {/* Responsive Seat Grid */}
        <div className="grid grid-cols-4 sm:grid-cols-8 gap-3 sm:gap-4">
          {currentCoach.seats?.map((seat) => {
            const isBooked = seat.status === 'BOOKED';
            const isSelected = selectedSeats.some(s => s.id === seat.id);

            let btnStyle = "bg-white border-2 border-emerald-400 text-slate-800 hover:border-emerald-600 hover:shadow-md";
            if (isBooked) {
              btnStyle = "bg-slate-200 border-2 border-slate-300 text-slate-400 cursor-not-allowed opacity-75";
            } else if (isSelected) {
              btnStyle = "bg-orange-500 border-2 border-orange-600 text-white shadow-md scale-102";
            }

            return (
              <button
                key={seat.id}
                type="button"
                disabled={isBooked}
                onClick={() => onSeatToggle(seat, currentCoach)}
                className={`flex flex-col items-center justify-center p-3 rounded-2xl transition-all cursor-pointer ${btnStyle}`}
              >
                {isBooked ? (
                  <Lock size={16} className="text-slate-400 mb-1" />
                ) : (
                  <Armchair size={16} className={isSelected ? "text-white mb-1" : "text-emerald-600 mb-1"} />
                )}
                <span className="font-black text-xs">{seat.seat_number}</span>
                <span className="text-[9px] font-bold tracking-tight truncate max-w-full">
                  {seat.berth_type?.replace('SIDE ', 'S.')}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex items-center justify-center gap-1.5 text-[11px] text-slate-500 bg-slate-100/70 p-3 rounded-2xl border border-slate-200/80">
        <Info size={14} className="text-orange-500 shrink-0" />
        <span>
          Seat selection is validated with MySQL row-level locks upon booking submission.
        </span>
      </div>

    </div>
  );
};

export default SeatMap;
