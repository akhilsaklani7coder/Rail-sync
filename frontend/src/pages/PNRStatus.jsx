import React, { useState } from 'react';
import { Ticket, Search, Train, Calendar, Download, AlertCircle, CheckCircle2, ShieldCheck, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

const PNRStatus = () => {
  const [pnrInput, setPnrInput] = useState('');
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!pnrInput.trim()) return;

    setLoading(true);
    setError('');
    setBooking(null);

    try {
      const res = await api.get(`/bookings/${pnrInput.trim().toUpperCase()}`);
      setBooking(res.data.booking);
    } catch (err) {
      setError(err.message || 'No booking found matching this PNR.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      <div className="text-center space-y-2 max-w-xl mx-auto">
        <div className="w-12 h-12 rounded-2xl saffron-gradient flex items-center justify-center text-white mx-auto shadow-md">
          <Ticket size={24} />
        </div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Check PNR Status</h1>
        <p className="text-xs text-slate-500">
          Enter your 10-character RailSync PNR number to check current booking and coach allocation status.
        </p>
      </div>

      {/* PNR Search Input */}
      <div className="max-w-xl mx-auto bg-white p-3 sm:p-4 rounded-3xl border border-slate-200 shadow-sm">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            required
            maxLength={12}
            value={pnrInput}
            onChange={(e) => setPnrInput(e.target.value.toUpperCase())}
            placeholder="Enter PNR (e.g. RS29384751)"
            className="flex-1 font-mono font-bold tracking-wider uppercase bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/30"
          />
          <button
            type="submit"
            disabled={loading}
            className="saffron-gradient hover:brightness-110 text-white font-bold px-6 py-3 rounded-2xl shadow transition-all flex items-center gap-1.5 cursor-pointer active:scale-95 text-xs sm:text-sm disabled:opacity-50"
          >
            <Search size={15} />
            <span>{loading ? 'Checking...' : 'Check Status'}</span>
          </button>
        </form>
      </div>

      {error && (
        <div className="max-w-xl mx-auto p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
          <AlertCircle size={16} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading && <LoadingSpinner text="Querying PNR records from MySQL InnoDB..." />}

      {/* PNR Result Display */}
      {booking && (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-md p-6 sm:p-8 space-y-6">
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-100 gap-4">
            <div>
              <span className="text-[11px] uppercase tracking-widest text-slate-400 font-bold">PNR Number</span>
              <div className="text-3xl font-mono font-black text-slate-900 tracking-wider mt-0.5">
                {booking.pnr}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <StatusBadge status={booking.booking_status} />
              <a
                href={`/api/bookings/${booking.pnr}/ticket.pdf`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 text-xs font-bold text-orange-600 px-3.5 py-2 rounded-xl bg-orange-50 hover:bg-orange-100 border border-orange-200 transition-colors"
              >
                <Download size={14} />
                <span>PDF Ticket</span>
              </a>
            </div>
          </div>

          {/* Train & Journey Details */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 p-5 rounded-2xl bg-slate-50 border border-slate-100 text-xs">
            <div>
              <span className="text-slate-400 block font-bold uppercase text-[10px]">Train Details</span>
              <div className="font-extrabold text-slate-900 text-sm mt-0.5">{booking.train_name}</div>
              <span className="font-mono text-slate-500 font-bold">#{booking.train_number}</span>
            </div>

            <div>
              <span className="text-slate-400 block font-bold uppercase text-[10px]">Corridor</span>
              <div className="font-bold text-slate-900 mt-0.5">{booking.source_station} → {booking.dest_station}</div>
              <span className="text-slate-400 text-[11px]">{booking.departure_time} to {booking.arrival_time}</span>
            </div>

            <div>
              <span className="text-slate-400 block font-bold uppercase text-[10px]">Journey Date</span>
              <div className="font-bold text-slate-900 mt-0.5 flex items-center gap-1">
                <Calendar size={13} className="text-orange-500" />
                <span>{booking.journey_date}</span>
              </div>
              <span className="text-slate-500 font-medium">Booked on {booking.created_at?.split(' ')[0]}</span>
            </div>
          </div>

          {/* Passengers & Seat Allocation */}
          <div className="space-y-3">
            <h4 className="font-bold text-slate-900 text-sm">Passenger Allocation Details</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {booking.passengers?.map((p, idx) => (
                <div key={idx} className="p-3.5 rounded-2xl border border-slate-200 bg-white flex items-center justify-between text-xs">
                  <div>
                    <div className="font-bold text-slate-900">{p.full_name}</div>
                    <div className="text-slate-400 text-[11px]">Age: {p.age} • {p.gender}</div>
                  </div>
                  <div className="text-right">
                    <span className="font-black text-orange-600 block">
                      Coach {p.coach} • Seat {p.seat_number}
                    </span>
                    <span className="text-[10px] text-slate-400 uppercase font-bold">
                      {p.berth_type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-2 flex items-center justify-end">
            <Link
              to={`/ticket/${booking.pnr}`}
              className="text-xs font-bold text-orange-600 hover:text-orange-700 flex items-center gap-1"
            >
              <span>View Full Reservation Slip</span>
              <ArrowRight size={14} />
            </Link>
          </div>

        </div>
      )}

    </div>
  );
};

export default PNRStatus;
