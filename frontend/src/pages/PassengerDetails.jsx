import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Users, User, ArrowRight, Train, Calendar, ShieldCheck, 
  AlertCircle, ArrowLeft, Plus, Trash2, CheckCircle, Sparkles, Tag
} from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const PassengerDetails = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();

  const train = location.state?.train;
  const journeyDate = location.state?.journeyDate;
  const selectedSeats = location.state?.selectedSeats || [];
  const initialClass = (selectedSeats.length > 0 && selectedSeats[0]?.coach_type) 
    ? selectedSeats[0].coach_type 
    : (location.state?.travelClass || 'CC');
  const initialCount = location.state?.passengerCount || 1;
  const autoAllocation = location.state?.autoAllocation ?? true;

  const [travelClass, setTravelClass] = useState(initialClass);
  const [passengers, setPassengers] = useState(() => {
    return Array.from({ length: Math.min(6, Math.max(1, initialCount)) }, (_, i) => ({
      full_name: i === 0 && user ? user.full_name : '',
      age: 28,
      gender: 'MALE',
      berth_preference: 'NO_PREFERENCE',
      seat_id: selectedSeats[i]?.id || null,
      seat_label: selectedSeats[i] ? `${selectedSeats[i].coach_number}-${selectedSeats[i].seat_number} (${selectedSeats[i].berth_type})` : null
    }));
  });

  const [fareQuote, setFareQuote] = useState(null);
  const [loadingFare, setLoadingFare] = useState(false);
  const [error, setError] = useState('');

  // Fetch live fare quote from backend whenever passenger count or class changes
  useEffect(() => {
    if (!train) return;

    const fetchQuote = async () => {
      setLoadingFare(true);
      try {
        const res = await api.get(
          `/trains/fare-quote?train_id=${train.id}&class=${travelClass}&passengers=${passengers.length}`
        );
        setFareQuote(res.data);
      } catch (err) {
        console.warn("Fare quote lookup failed", err);
      } finally {
        setLoadingFare(false);
      }
    };

    fetchQuote();
  }, [train, travelClass, passengers.length]);

  if (!train) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center bg-white rounded-3xl border border-slate-200 mt-8 space-y-4">
        <p className="text-slate-600">No active booking session found.</p>
        <button
          onClick={() => navigate('/search')}
          className="saffron-gradient text-white px-6 py-2.5 rounded-xl text-xs font-bold"
        >
          Search Trains
        </button>
      </div>
    );
  }

  const handlePassengerChange = (index, field, value) => {
    const updated = [...passengers];
    updated[index][field] = value;
    setPassengers(updated);
  };

  const handleAddPassenger = () => {
    if (passengers.length >= 6) {
      showToast("Maximum 6 passengers allowed per booking.", "warning");
      return;
    }
    setPassengers([
      ...passengers,
      {
        full_name: '',
        age: 25,
        gender: 'MALE',
        berth_preference: 'NO_PREFERENCE',
        seat_id: null,
        seat_label: null
      }
    ]);
  };

  const handleRemovePassenger = (index) => {
    if (passengers.length <= 1) {
      showToast("At least one passenger is required.", "warning");
      return;
    }
    setPassengers(passengers.filter((_, i) => i !== index));
  };

  const handleProceedToPayment = (e) => {
    e.preventDefault();
    setError('');

    // Form Validation
    for (let i = 0; i < passengers.length; i++) {
      if (!passengers[i].full_name.trim()) {
        setError(`Please enter the full legal name for Passenger #${i + 1}`);
        return;
      }
      if (passengers[i].age < 1 || passengers[i].age > 120) {
        setError(`Please enter a valid age (1-120) for Passenger #${i + 1}`);
        return;
      }
    }

    const calculatedTotal = fareQuote?.total_amount || (train.base_fare * passengers.length);
    const isClassChanged = selectedSeats.length > 0 && selectedSeats[0]?.coach_type !== travelClass;
    const finalAutoAllocation = autoAllocation || isClassChanged;
    const finalSeatIds = finalAutoAllocation ? null : selectedSeats.map(s => s.id);

    navigate('/payment', {
      state: {
        train,
        journeyDate,
        travelClass,
        passengers,
        selectedSeatIds: finalSeatIds,
        totalAmount: calculatedTotal,
        fareQuote,
        autoAllocation: finalAutoAllocation
      }
    });
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Step Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-orange-600">
            Step 2 of 4 • Passenger & Berth Allocation
          </span>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mt-1">
            Traveler Details & Class Selection
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Add up to 6 passengers with berth preferences according to railway regulations.
          </p>
        </div>

        <button
          type="button"
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-800 self-start sm:self-auto cursor-pointer"
        >
          <ArrowLeft size={14} />
          <span>Change Train</span>
        </button>
      </div>

      {/* Train & Journey Summary Card */}
      <div className="bg-slate-950 text-white rounded-3xl p-6 border border-slate-800 shadow-md flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl saffron-gradient flex items-center justify-center text-white shrink-0">
            <Train size={24} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-900 text-orange-400">
                #{train.train_number}
              </span>
              <span className="text-xs text-slate-400">
                {train.departure_time} → {train.arrival_time}
              </span>
            </div>
            <h4 className="font-black text-white text-base mt-1">{train.train_name}</h4>
            <p className="text-xs text-slate-400">
              {train.source_station_name || train.source_name} → {train.destination_station_name || train.dest_name}
            </p>
          </div>
        </div>

        {/* Travel Class Selector Dropdown */}
        <div className="flex items-center gap-4 border-t sm:border-t-0 pt-4 sm:pt-0 border-slate-800 text-xs">
          <div>
            <span className="text-[10px] text-slate-400 uppercase font-bold block">Class</span>
            <select
              value={travelClass}
              onChange={(e) => setTravelClass(e.target.value)}
              className="mt-1 bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 font-bold text-orange-400 text-xs focus:ring-1 focus:ring-orange-500"
            >
              {['1A', '2A', '3A', 'CC', 'SL'].map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase font-bold block">Date</span>
            <span className="font-bold text-white text-sm">{journeyDate}</span>
          </div>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
          <AlertCircle size={16} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Layout: Form + Fare Breakdown Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Passenger Input List (2 Cols) */}
        <form onSubmit={handleProceedToPayment} className="lg:col-span-2 space-y-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Passenger Manifest ({passengers.length} of 6)
            </span>
            <button
              type="button"
              onClick={handleAddPassenger}
              disabled={passengers.length >= 6}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-orange-50 text-orange-600 border border-orange-200 hover:bg-orange-100 transition-colors disabled:opacity-40 cursor-pointer"
            >
              <Plus size={14} /> Add Another Passenger
            </button>
          </div>

          <div className="space-y-4">
            {passengers.map((pax, index) => (
              <div key={index} className="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-xs space-y-4 relative">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <span className="text-xs font-black uppercase tracking-wider text-slate-800 flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-xs">
                      {index + 1}
                    </div>
                    <span>Passenger #{index + 1}</span>
                  </span>

                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-0.5 rounded-full">
                      Class: {travelClass}
                    </span>
                    {passengers.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemovePassenger(index)}
                        className="p-1 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                        title="Remove passenger"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-12 gap-3.5">
                  <div className="sm:col-span-5 space-y-1">
                    <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                      Full Legal Name
                    </label>
                    <input
                      type="text"
                      required
                      value={pax.full_name}
                      onChange={(e) => handlePassengerChange(index, 'full_name', e.target.value)}
                      placeholder="e.g. Ramesh Kumar"
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/30"
                    />
                  </div>

                  <div className="sm:col-span-2 space-y-1">
                    <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                      Age
                    </label>
                    <input
                      type="number"
                      min={1}
                      max={120}
                      required
                      value={pax.age}
                      onChange={(e) => handlePassengerChange(index, 'age', e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/30"
                    />
                  </div>

                  <div className="sm:col-span-2 space-y-1">
                    <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                      Gender
                    </label>
                    <select
                      value={pax.gender}
                      onChange={(e) => handlePassengerChange(index, 'gender', e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-2.5 text-xs font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/30"
                    >
                      <option value="MALE">Male</option>
                      <option value="FEMALE">Female</option>
                      <option value="OTHER">Other</option>
                    </select>
                  </div>

                  <div className="sm:col-span-3 space-y-1">
                    <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                      Berth Preference
                    </label>
                    <select
                      value={pax.berth_preference}
                      onChange={(e) => handlePassengerChange(index, 'berth_preference', e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-2 py-2.5 text-xs font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/30"
                    >
                      <option value="NO_PREFERENCE">No Preference</option>
                      <option value="LOWER">Lower Berth</option>
                      <option value="MIDDLE">Middle Berth</option>
                      <option value="UPPER">Upper Berth</option>
                      <option value="SIDE LOWER">Side Lower</option>
                      <option value="SIDE UPPER">Side Upper</option>
                      <option value="WINDOW">Window Seat</option>
                      <option value="AISLE">Aisle Seat</option>
                    </select>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-2">
            <button
              type="submit"
              className="w-full saffron-gradient hover:brightness-110 text-white font-bold py-3.5 rounded-2xl shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95 text-sm"
            >
              <span>Continue to Payment Simulation</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </form>

        {/* Live Fare Breakdown Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-sm space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-black text-slate-900 text-sm flex items-center gap-2">
                <Tag size={16} className="text-orange-500" />
                Fare Summary
              </h3>
              <span className="text-xs font-bold text-slate-500">
                {passengers.length} {passengers.length === 1 ? 'Passenger' : 'Passengers'}
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between text-slate-600">
                <span>Base Class Fare ({travelClass})</span>
                <span className="font-mono font-bold text-slate-900">
                  ₹{fareQuote?.total_base_amount?.toFixed(2) || '---'}
                </span>
              </div>

              <div className="flex items-center justify-between text-slate-600">
                <span>Reservation Fee</span>
                <span className="font-mono font-bold text-slate-900">
                  ₹{fareQuote?.total_reservation_fee?.toFixed(2) || '---'}
                </span>
              </div>

              <div className="flex items-center justify-between text-slate-600">
                <span>Superfast / Flagship Surcharge</span>
                <span className="font-mono font-bold text-slate-900">
                  ₹{fareQuote?.total_superfast_charge?.toFixed(2) || '---'}
                </span>
              </div>

              <div className="flex items-center justify-between text-slate-600">
                <span>Statutory GST (5% on AC)</span>
                <span className="font-mono font-bold text-slate-900">
                  ₹{fareQuote?.total_gst?.toFixed(2) || '0.00'}
                </span>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-base">
                <span className="font-black text-slate-900">Total Amount</span>
                <span className="text-2xl font-black text-orange-600 font-mono">
                  ₹{fareQuote?.total_amount?.toFixed(2) || '---'}
                </span>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/60 text-[11px] text-slate-500 space-y-1">
              <p className="font-semibold text-slate-700">Fair Cancellation Guarantee:</p>
              <p>Simulated tickets eligible for instant refund upon cancellation. Flat clerkage fee for waitlist tickets.</p>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};

export default PassengerDetails;
