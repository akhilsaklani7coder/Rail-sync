import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { Train, Clock, ArrowRight, Calendar, Armchair, ShieldCheck, Cpu, AlertCircle, Users, Check, RefreshCw } from 'lucide-react';
import api from '../api/axios';
import SeatMap from '../components/SeatMap';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../context/ToastContext';

const TrainDetails = () => {
  const { trainId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [train, setTrain] = useState(location.state?.train || null);
  const [dijkstraInfo, setDijkstraInfo] = useState(null);
  const [journeyDate, setJourneyDate] = useState(() => {
    return location.state?.journeyDate || (() => {
      const d = new Date();
      d.setDate(d.getDate() + 1);
      return d.toISOString().split('T')[0];
    })();
  });

  const [coaches, setCoaches] = useState([]);
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [passengerCount, setPassengerCount] = useState(1);
  const [autoAllocation, setAutoAllocation] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const minDate = new Date().toISOString().split('T')[0];

  // Fetch train details if not passed via router state
  useEffect(() => {
    const fetchTrain = async () => {
      try {
        if (!train) {
          const res = await api.get(`/trains/${trainId}`);
          setTrain(res.data.train);
        }
      } catch (err) {
        setError('Failed to load train details.');
      }
    };
    fetchTrain();
  }, [trainId]);

  // Fetch seat availability map for train on journeyDate
  const fetchAvailability = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/trains/${trainId}/availability?date=${journeyDate}`);
      setCoaches(res.data.coaches || []);
      setSelectedSeats([]);
    } catch (err) {
      setError('Failed to fetch coach layout and seat availability.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (trainId && journeyDate) {
      fetchAvailability();
    }
  }, [trainId, journeyDate]);

  useEffect(() => {
    const fetchDijkstra = async () => {
      const srcId = train?.source_id || train?.source_station_id;
      const dstId = train?.dest_id || train?.destination_station_id;
      if (srcId && dstId && srcId !== dstId) {
        try {
          const res = await api.get(`/trains/shortest-path?source_id=${srcId}&dest_id=${dstId}`);
          setDijkstraInfo(res.data);
        } catch {
          // Non-blocking Dijkstra distance indicator
        }
      }
    };
    if (train) fetchDijkstra();
  }, [train]);

  const handleSeatToggle = (seat, coach) => {
    setAutoAllocation(false);
    const exists = selectedSeats.some(s => s.id === seat.id);
    if (exists) {
      const updated = selectedSeats.filter(s => s.id !== seat.id);
      setSelectedSeats(updated);
      setPassengerCount(Math.max(1, updated.length));
    } else {
      if (selectedSeats.length >= 6) {
        showToast("Maximum 6 seats permitted per reservation.", "error");
        return;
      }
      const updated = [...selectedSeats, { ...seat, coach_number: coach.coach_number, coach_type: coach.coach_type }];
      setSelectedSeats(updated);
      setPassengerCount(updated.length);
    }
  };

  const handleProceed = () => {
    const count = autoAllocation ? passengerCount : selectedSeats.length;
    if (count <= 0) {
      showToast("Please select at least 1 seat or passenger.", "error");
      return;
    }

    // Authoritative class resolution: prioritize selected seat coach_type, then router state, fallback to CC
    const derivedClass = selectedSeats.length > 0
      ? (selectedSeats[0].coach_type || 'CC')
      : (location.state?.travelClass || 'CC');

    navigate('/passenger-details', {
      state: {
        train,
        journeyDate,
        travelClass: derivedClass,
        passengerCount: count,
        selectedSeats: autoAllocation ? [] : selectedSeats,
        autoAllocation
      }
    });
  };

  if (!train && !loading) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center bg-white rounded-3xl border border-slate-200 mt-8 space-y-4">
        <p className="text-rose-600 font-bold">Train record not found.</p>
        <button
          onClick={() => navigate('/search')}
          className="saffron-gradient text-white px-6 py-2.5 rounded-xl text-xs font-bold"
        >
          Return to Train Search
        </button>
      </div>
    );
  }

  const baseFare = train?.base_fare || 500;
  const currentCount = autoAllocation ? passengerCount : (selectedSeats.length || 1);
  const totalEstimatedFare = baseFare * currentCount;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Train Info Banner */}
      <div className="bg-slate-950 text-white rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl saffron-gradient flex items-center justify-center text-white shrink-0 shadow-lg">
              <Train size={30} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-800 text-orange-400 border border-slate-700">
                  #{train?.train_number}
                </span>
                <span className="text-xs text-emerald-400 font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30">
                  Runs {train?.running_days || 'Daily'}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-white mt-1.5">{train?.train_name}</h1>
              <p className="text-xs text-slate-400 mt-0.5 font-medium">
                {train?.source_station_name || train?.source_name} ({train?.source_station_code || train?.source_code}) → {train?.destination_station_name || train?.dest_name} ({train?.destination_station_code || train?.dest_code})
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 border-t md:border-t-0 pt-4 md:pt-0 border-slate-800">
            <div className="text-left">
              <span className="text-[11px] text-slate-400 block font-bold uppercase tracking-wider">Departure</span>
              <span className="text-2xl font-black text-white">{train?.departure_time}</span>
            </div>
            <div className="w-12 h-0.5 bg-slate-800"></div>
            <div className="text-right">
              <span className="text-[11px] text-slate-400 block font-bold uppercase tracking-wider">Arrival</span>
              <span className="text-2xl font-black text-white">{train?.arrival_time}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Date & Allocation Strategy Selector */}
      <div className="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center gap-6 flex-wrap">
          <div className="space-y-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <Calendar size={13} className="text-orange-500" />
              Journey Date
            </label>
            <input
              type="date"
              min={minDate}
              value={journeyDate}
              onChange={(e) => setJourneyDate(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs sm:text-sm font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/30 cursor-pointer"
            />
          </div>

          {/* Allocation Strategy Toggle */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <Cpu size={13} className="text-indigo-600" />
              Allocation Strategy
            </label>
            <div className="inline-flex rounded-xl bg-slate-100 p-1 border border-slate-200 text-xs">
              <button
                type="button"
                onClick={() => {
                  setAutoAllocation(true);
                  setSelectedSeats([]);
                }}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                  autoAllocation ? 'bg-slate-950 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                C++ Auto Contiguous
              </button>
              <button
                type="button"
                onClick={() => setAutoAllocation(false)}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                  !autoAllocation ? 'bg-slate-950 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Manual Seat Picker
              </button>
            </div>
          </div>

          {/* Passenger Count (Visible in Auto Mode) */}
          {autoAllocation && (
            <div className="space-y-1.5">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Users size={13} className="text-orange-500" />
                Passengers
              </label>
              <select
                value={passengerCount}
                onChange={(e) => setPassengerCount(Number(e.target.value))}
                className="bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs sm:text-sm font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/30 cursor-pointer"
              >
                {[1, 2, 3, 4, 5, 6].map(num => (
                  <option key={num} value={num}>{num} {num === 1 ? 'Passenger' : 'Passengers'}</option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Fare and Proceed Button */}
        <div className="flex items-center justify-between md:justify-end gap-6 pt-4 md:pt-0 border-t md:border-t-0 border-slate-100">
          <div className="text-left md:text-right">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Total Estimated Fare</span>
            <span className="text-2xl font-black text-slate-900">₹{totalEstimatedFare.toFixed(2)}</span>
          </div>

          <button
            onClick={handleProceed}
            className="saffron-gradient hover:brightness-110 text-white font-bold px-7 py-3 rounded-2xl shadow-md hover:shadow-lg transition-all flex items-center gap-2 cursor-pointer active:scale-95 text-xs sm:text-sm"
          >
            <span>Proceed to Passengers</span>
            <ArrowRight size={15} />
          </button>
        </div>
      </div>

      {/* Seat Map Layout View */}
      {loading ? (
        <LoadingSpinner text="Retrieving coach layout and row-locked availability..." />
      ) : error ? (
        <div className="p-6 rounded-3xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
          <button
            onClick={fetchAvailability}
            className="px-4 py-2 rounded-xl bg-rose-600 text-white font-bold text-xs"
          >
            Retry
          </button>
        </div>
      ) : (
        <SeatMap
          coaches={coaches}
          selectedSeats={selectedSeats}
          onSeatToggle={handleSeatToggle}
          maxSelectable={6}
        />
      )}

    </div>
  );
};

export default TrainDetails;
