import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Ticket, Train, Calendar, Download, Trash2, AlertCircle, ArrowRight, RefreshCw, Filter, QrCode, CheckCircle2, XCircle, Clock } from 'lucide-react';
import api from '../api/axios';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../context/ToastContext';

const MyBookings = () => {
  const { showToast } = useToast();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Tab Filter: 'UPCOMING', 'COMPLETED', 'CANCELLED', 'ALL'
  const [activeTab, setActiveTab] = useState('UPCOMING');
  
  const [cancelTarget, setCancelTarget] = useState(null);
  const [cancelling, setCancelling] = useState(false);

  const fetchBookings = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get('/bookings/my');
      setBookings(res.data.bookings || []);
    } catch {
      setError('Failed to fetch your bookings from the server.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  const handleConfirmCancel = async () => {
    if (!cancelTarget) return;
    setCancelling(true);
    try {
      const res = await api.post(`/bookings/${cancelTarget.pnr}/cancel`);
      showToast(`Booking ${cancelTarget.pnr} successfully cancelled. Refund of ₹${res.data.refund_amount?.toFixed(2)} processed.`, "success");
      setCancelTarget(null);
      await fetchBookings();
    } catch (err) {
      showToast(err.data?.error || err.message || 'Failed to cancel booking.', "error");
    } finally {
      setCancelling(false);
    }
  };

  const todayStr = new Date().toISOString().split('T')[0];

  const filteredBookings = bookings.filter(b => {
    if (activeTab === 'ALL') return true;
    if (activeTab === 'CANCELLED') return b.booking_status === 'CANCELLED';
    if (activeTab === 'UPCOMING') return b.booking_status !== 'CANCELLED' && b.journey_date >= todayStr;
    if (activeTab === 'COMPLETED') return b.booking_status !== 'CANCELLED' && b.journey_date < todayStr;
    return true;
  });

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">My Railway Bookings</h1>
          <p className="text-xs text-slate-500 mt-1">Review upcoming journeys, download official PDF tickets, or cancel seats.</p>
        </div>

        {/* Tab Controls */}
        <div className="inline-flex rounded-2xl bg-white border border-slate-200 p-1.5 shadow-xs text-xs self-start sm:self-auto">
          {[
            { id: 'UPCOMING', label: 'Upcoming', icon: Calendar },
            { id: 'COMPLETED', label: 'Completed', icon: Clock },
            { id: 'CANCELLED', label: 'Cancelled', icon: XCircle },
            { id: 'ALL', label: `All (${bookings.length})`, icon: Ticket }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl font-bold transition-all cursor-pointer ${
                  isActive 
                    ? 'bg-slate-950 text-white shadow-xs' 
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Icon size={13} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
          <button
            onClick={fetchBookings}
            className="text-xs font-bold underline cursor-pointer"
          >
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <LoadingSpinner text="Retrieving booking records from MySQL..." />
      ) : filteredBookings.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-slate-100 text-slate-400 mx-auto flex items-center justify-center">
            <Ticket size={28} />
          </div>
          <h3 className="font-bold text-slate-900 text-base">
            No {activeTab.toLowerCase()} bookings found
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            {activeTab === 'UPCOMING'
              ? "You don't have any upcoming train reservations right now. Plan a new journey!"
              : "Try switching to another tab to view your bookings."}
          </p>
          <Link
            to="/search"
            className="inline-flex items-center gap-2 saffron-gradient text-white font-bold px-6 py-2.5 rounded-xl text-xs shadow-md"
          >
            <span>Search Available Trains</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredBookings.map((b) => (
            <div
              key={b.id}
              className="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200 shadow-sm hover:border-slate-300 transition-all flex flex-col md:flex-row md:items-center justify-between gap-6"
            >
              
              {/* Train and PNR info */}
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-2xl saffron-gradient flex items-center justify-center text-white shrink-0 shadow-sm">
                  <Train size={22} />
                </div>
                <div>
                  <div className="flex items-center gap-2.5">
                    <span className="text-xs font-mono font-black text-slate-900 px-2.5 py-0.5 rounded-full bg-slate-100 border border-slate-200">
                      PNR: {b.pnr}
                    </span>
                    <StatusBadge status={b.booking_status} />
                    <span className="text-[11px] font-bold text-slate-600 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded-md">
                      Class: {b.travel_class || 'CC'}
                    </span>
                  </div>
                  <h3 className="font-bold text-slate-900 text-base mt-1.5">{b.train_name} (#{b.train_number})</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {b.source_station} ({b.source_code}) → {b.dest_station} ({b.dest_code})
                  </p>
                </div>
              </div>

              {/* Schedule and Fare */}
              <div className="flex items-center gap-6 sm:gap-8 border-y md:border-y-0 py-3 md:py-0 border-slate-100 text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 block font-bold uppercase">Journey Date</span>
                  <span className="font-bold text-slate-800 text-sm flex items-center gap-1 mt-0.5">
                    <Calendar size={13} className="text-orange-500" />
                    {b.journey_date}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-bold uppercase">Passengers</span>
                  <span className="font-bold text-slate-800 text-sm mt-0.5 block">{b.passenger_count} {b.passenger_count === 1 ? 'Seat' : 'Seats'}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-bold uppercase">Fare Paid</span>
                  <span className="font-black text-slate-900 text-base mt-0.5 block">₹{b.total_amount?.toFixed(2)}</span>
                </div>
              </div>

              {/* Actions & Cancellation Refund summary */}
              <div className="flex items-center gap-2.5 justify-end">
                {b.booking_status === 'CANCELLED' && b.refund_amount !== null && (
                  <div className="text-right mr-2 hidden sm:block">
                    <span className="text-[10px] text-emerald-600 uppercase font-bold block">Refund Processed</span>
                    <span className="text-xs font-mono font-black text-emerald-700">₹{b.refund_amount?.toFixed(2)}</span>
                  </div>
                )}

                <Link
                  to={`/ticket/${b.pnr}`}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 text-slate-800 hover:bg-slate-200 transition-colors"
                >
                  View Slip
                </Link>

                <a
                  href={`/api/bookings/${b.pnr}/ticket.pdf`}
                  target="_blank"
                  rel="noreferrer"
                  className="p-2.5 rounded-xl text-slate-600 hover:text-orange-600 hover:bg-orange-50 border border-slate-200 transition-colors"
                  title="Download PDF Ticket"
                >
                  <Download size={16} />
                </a>

                {b.booking_status === 'CONFIRMED' && (
                  <button
                    type="button"
                    onClick={() => setCancelTarget(b)}
                    className="p-2.5 rounded-xl text-rose-600 hover:bg-rose-50 border border-rose-200 transition-colors cursor-pointer"
                    title="Cancel Booking & Refund"
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>

            </div>
          ))}
        </div>
      )}

      {/* Cancellation Confirmation Modal */}
      {cancelTarget && (
        <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-lg font-black text-slate-900">Confirm Booking Cancellation</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Are you sure you want to cancel booking for <b>PNR {cancelTarget.pnr}</b> ({cancelTarget.train_name})?
            </p>
            
            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-xs space-y-1.5">
              <div className="flex justify-between text-slate-600">
                <span>Total Fare Paid:</span>
                <span className="font-mono font-bold text-slate-900">₹{cancelTarget.total_amount?.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Cancellation Charges:</span>
                <span className="font-mono font-bold text-rose-600">
                  ₹{cancelTarget.travel_class === 'SL' ? '60.00' : '120.00'} / passenger
                </span>
              </div>
              <div className="pt-2 border-t border-slate-200 flex justify-between font-bold text-emerald-700">
                <span>Net Estimated Refund:</span>
                <span className="font-mono text-sm">
                  ₹{Math.max(0, cancelTarget.total_amount - ((cancelTarget.travel_class === 'SL' ? 60 : 120) * cancelTarget.passenger_count)).toFixed(2)}
                </span>
              </div>
            </div>

            <p className="text-[11px] text-slate-400">
              Released seats will be automatically assigned to queued RAC and Waitlisted travelers in FIFO order.
            </p>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                disabled={cancelling}
                onClick={() => setCancelTarget(null)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
              >
                Keep Booking
              </button>
              <button
                type="button"
                disabled={cancelling}
                onClick={handleConfirmCancel}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-rose-600 text-white hover:bg-rose-700 shadow"
              >
                {cancelling ? 'Cancelling...' : 'Confirm Cancellation & Refund'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default MyBookings;
