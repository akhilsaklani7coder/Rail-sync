import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Train, Clock, ArrowRight, Armchair, ShieldCheck, MapPin, Calendar, CheckSquare, Square, Eye } from 'lucide-react';

const TrainCard = ({ 
  train, 
  journeyDate, 
  onToggleCompare, 
  isCompared = false, 
  onViewTimetable 
}) => {
  const navigate = useNavigate();

  // Find default selected class from train.classes or fallback to CC
  const defaultClass = train.classes && train.classes.length > 0 ? train.classes[0].coach_type : 'CC';
  const [selectedClass, setSelectedClass] = useState(defaultClass);

  const activeClassObj = (train.classes || []).find(c => c.coach_type === selectedClass) || {
    coach_type: selectedClass,
    fare: train.base_fare,
    available: train.total_available_seats,
    status_label: `AVL ${train.total_available_seats}`
  };

  const handleBook = (coachType) => {
    const classToBook = coachType || selectedClass;
    navigate(`/train/${train.id}`, {
      state: {
        train,
        journeyDate,
        travelClass: classToBook
      }
    });
  };

  const getTrainTypeBadge = (type) => {
    switch (type) {
      case 'VANDE_BHARAT':
        return 'bg-blue-600 text-white';
      case 'RAJDHANI':
        return 'bg-red-600 text-white';
      case 'SHATABDI':
        return 'bg-purple-600 text-white';
      case 'DURONTO':
        return 'bg-emerald-600 text-white';
      case 'GARIB_RATH':
        return 'bg-teal-700 text-white';
      case 'SUPERFAST':
        return 'bg-amber-600 text-white';
      case 'MAIL_EXPRESS':
        return 'bg-indigo-600 text-white';
      case 'INTERCITY':
        return 'bg-cyan-700 text-white';
      default:
        return 'bg-slate-700 text-white';
    }
  };

  return (
    <div className="bg-white rounded-3xl border border-slate-200/90 shadow-sm hover:shadow-xl hover:border-orange-300 transition-all overflow-hidden p-6 sm:p-7 group">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        
        {/* Train Identity & Category */}
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl saffron-gradient flex items-center justify-center text-white shrink-0 group-hover:scale-105 transition-transform shadow-md">
            <Train size={24} />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs font-black px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-800">
                #{train.train_number}
              </span>
              <span className={`text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full ${getTrainTypeBadge(train.train_type)}`}>
                {train.train_type ? train.train_type.replace('_', ' ') : 'EXPRESS'}
              </span>
              <span className="text-xs text-emerald-700 font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200">
                Runs {train.running_days || 'Daily'}
              </span>
            </div>
            <h3 className="font-black text-xl text-slate-900 mt-1">{train.train_name}</h3>
            <p className="text-xs text-slate-500 mt-0.5 font-medium flex items-center gap-2">
              <span>{train.distance_km} km</span>
              <span>•</span>
              <button
                type="button"
                onClick={() => onViewTimetable && onViewTimetable(train)}
                className="text-orange-600 hover:text-orange-700 font-semibold inline-flex items-center gap-1 hover:underline cursor-pointer"
              >
                <Eye size={12} /> View Timetable & Intermediate Stops
              </button>
            </p>
          </div>
        </div>

        {/* Schedule & Stations */}
        <div className="flex items-center gap-6 sm:gap-8 justify-between lg:justify-center border-y lg:border-y-0 py-4 lg:py-0 border-slate-100">
          <div className="text-left">
            <div className="text-2xl font-black text-slate-900 tracking-tight">{train.departure_time}</div>
            <div className="text-xs font-bold text-slate-800">{train.source_station_name}</div>
            <div className="text-[11px] font-mono text-slate-400 font-bold">{train.source_station_code}</div>
          </div>

          <div className="flex flex-col items-center px-2 sm:px-4">
            <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1 mb-1">
              <Clock size={13} />
              {train.duration}
            </span>
            <div className="w-24 sm:w-28 h-0.5 bg-slate-200 relative flex items-center justify-center">
              <div className="w-2 h-2 rounded-full bg-orange-500 absolute -top-[3px]"></div>
              <ArrowRight size={14} className="text-slate-400 absolute -right-2" />
            </div>
            <span className="text-[10px] text-slate-400 mt-1 uppercase font-bold tracking-wider">Direct</span>
          </div>

          <div className="text-right">
            <div className="text-2xl font-black text-slate-900 tracking-tight">{train.arrival_time}</div>
            <div className="text-xs font-bold text-slate-800">{train.destination_station_name}</div>
            <div className="text-[11px] font-mono text-slate-400 font-bold">{train.destination_station_code}</div>
          </div>
        </div>

        {/* Selected Class Fare & Action CTAs */}
        <div className="flex items-center justify-between lg:justify-end gap-5 pt-2 lg:pt-0">
          <div className="text-left lg:text-right">
            <div className="flex items-center gap-1.5 lg:justify-end text-xs font-bold text-emerald-600">
              <Armchair size={15} />
              <span>{activeClassObj.status_label || `${activeClassObj.available} Available`}</span>
            </div>
            <div className="text-2xl font-black text-slate-900 mt-0.5">
              ₹{Math.round(activeClassObj.fare || train.base_fare)}
              <span className="text-xs font-normal text-slate-400 ml-1">/ {selectedClass}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {onToggleCompare && (
              <button
                type="button"
                onClick={() => onToggleCompare(train.id)}
                className={`p-2.5 rounded-xl border text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                  isCompared 
                    ? 'bg-orange-500 text-white border-orange-500 shadow-sm' 
                    : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                }`}
                title="Add to train comparison"
              >
                {isCompared ? <CheckSquare size={16} /> : <Square size={16} />}
                <span className="hidden sm:inline">Compare</span>
              </button>
            )}

            <button
              onClick={() => handleBook(selectedClass)}
              className="saffron-gradient hover:brightness-110 text-white font-bold px-6 py-3 rounded-2xl shadow-md hover:shadow-lg transition-all flex items-center gap-2 cursor-pointer active:scale-95 text-xs sm:text-sm"
            >
              <span>Select Seats & Book</span>
              <ArrowRight size={15} />
            </button>
          </div>
        </div>

      </div>

      {/* Interactive Class Selector Cards */}
      {train.classes && train.classes.length > 0 && (
        <div className="mt-5 pt-4 border-t border-slate-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Select Travel Class & Check Availability:</span>
            <span className="text-[11px] text-slate-500">Click class or Book to choose seats</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2.5">
            {train.classes.map((c, i) => {
              const isSelected = selectedClass === c.coach_type;
              const isAvail = c.available > 0;
              return (
                <div
                  key={i}
                  onClick={() => setSelectedClass(c.coach_type)}
                  className={`p-3 rounded-2xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-orange-500/10 border-orange-500 shadow-xs ring-1 ring-orange-500'
                      : 'bg-slate-50/70 border-slate-200 hover:bg-slate-100/80 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-black text-slate-900 text-sm">{c.coach_type}</span>
                    <span className="text-xs font-bold text-slate-900">₹{Math.round(c.fare)}</span>
                  </div>
                  <div className="mt-1 flex items-center justify-between">
                    <span className={`text-[10px] font-bold ${isAvail ? 'text-emerald-700' : 'text-amber-700'}`}>
                      {c.status_label || (isAvail ? `AVL ${c.available}` : 'RAC 4')}
                    </span>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedClass(c.coach_type);
                        handleBook(c.coach_type);
                      }}
                      className={`text-[9px] uppercase font-bold px-1.5 py-0.5 rounded transition-all cursor-pointer ${
                        isSelected 
                          ? 'bg-orange-600 text-white' 
                          : 'text-orange-600 hover:bg-orange-100'
                      }`}
                    >
                      Book
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default TrainCard;
