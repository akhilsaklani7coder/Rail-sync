import React from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { CheckCircle2, Ticket, Download, ArrowRight, Train, Armchair, ShieldCheck, History, QrCode } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';

const BookingConfirmation = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const bookingResult = location.state?.bookingResult;
  const train = location.state?.train;
  const journeyDate = location.state?.journeyDate;

  if (!bookingResult) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center bg-white rounded-3xl border border-slate-200 mt-8 space-y-4">
        <p className="text-slate-600">No recent booking found in this session.</p>
        <button
          onClick={() => navigate('/')}
          className="saffron-gradient text-white px-6 py-2.5 rounded-xl text-xs font-bold"
        >
          Return to Home
        </button>
      </div>
    );
  }

  const { pnr, ticket_number, assigned_seats, total_amount, travel_class, booking_status } = bookingResult;

  const handleDownloadPdf = () => {
    window.open(`/api/bookings/${pnr}/ticket.pdf`, '_blank');
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      {/* Success Badge Header */}
      <div className="text-center space-y-3">
        <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 mx-auto flex items-center justify-center shadow-inner">
          <CheckCircle2 size={36} />
        </div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Booking Confirmed!</h1>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          Your reservation has been transactionally allocated in MySQL InnoDB with row-level concurrency locking.
        </p>
      </div>

      {/* Official PNR Slip Box with live QR */}
      <div className="bg-slate-950 text-white rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-2xl space-y-6">
        
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-800 gap-4">
          <div>
            <span className="text-[11px] uppercase tracking-widest text-slate-400 font-bold">Official PNR Number</span>
            <div className="text-3xl sm:text-4xl font-mono font-black text-orange-400 tracking-wider mt-0.5">
              {pnr}
            </div>
            <span className="text-xs text-slate-400 mt-1 block">Class: <b className="text-white">{travel_class || 'CC'}</b></span>
          </div>

          <div className="flex items-center gap-4">
            <div className="bg-white p-1.5 rounded-2xl shadow-md">
              <img
                src={`/api/bookings/${pnr}/qr`}
                alt="Verification QR"
                className="w-16 h-16 object-contain"
              />
            </div>
            <div className="space-y-1">
              <StatusBadge status={booking_status || 'CONFIRMED'} />
              <span className="text-[11px] font-mono text-slate-400 block">Tkt: {ticket_number}</span>
            </div>
          </div>
        </div>

        {/* Train & Journey Summary */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="space-y-1">
            <span className="text-slate-400">Train Details:</span>
            <div className="font-bold text-white text-sm">{train?.train_name} (#{train?.train_number})</div>
            <div className="text-slate-300">
              {train?.source_station_name || train?.source_name} → {train?.destination_station_name || train?.dest_name}
            </div>
          </div>
          <div className="space-y-1 sm:text-right">
            <span className="text-slate-400">Date of Journey:</span>
            <div className="font-bold text-white text-sm">{journeyDate}</div>
            <div className="text-orange-400 font-bold">Total Paid: ₹{total_amount?.toFixed(2)}</div>
          </div>
        </div>

        {/* Assigned Passengers & Berths */}
        <div className="pt-4 border-t border-slate-800 space-y-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Assigned Passengers & Berths:</span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {assigned_seats?.map((s, idx) => (
              <div key={idx} className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                <div>
                  <div className="font-bold text-white">{s.passenger_name}</div>
                  <div className="text-slate-400 text-[11px]">{s.gender}, {s.age} yrs</div>
                </div>
                <div className="text-right">
                  <div className="font-extrabold text-orange-400">
                    {s.coach === 'WL' ? s.allocated_berth : `Coach ${s.coach} • Seat ${s.seat_number}`}
                  </div>
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">
                    {s.berth_type} • {s.status || 'CONFIRMED'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
        <button
          onClick={handleDownloadPdf}
          className="w-full sm:w-auto saffron-gradient hover:brightness-110 text-white font-bold px-6 py-3 rounded-2xl shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95 text-xs sm:text-sm"
        >
          <Download size={16} />
          <span>Download PDF E-Ticket</span>
        </button>

        <Link
          to="/my-bookings"
          className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-bold border border-slate-800 transition-all flex items-center justify-center gap-2 text-xs sm:text-sm"
        >
          <History size={16} />
          <span>View in My Bookings</span>
        </Link>

        <Link
          to="/search"
          className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold transition-all flex items-center justify-center gap-2 text-xs sm:text-sm"
        >
          <span>Book Another Trip</span>
          <ArrowRight size={14} />
        </Link>
      </div>

    </div>
  );
};

export default BookingConfirmation;
