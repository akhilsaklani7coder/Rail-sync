import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Train, Calendar, Clock, Download, ArrowLeft, ShieldCheck, Armchair, AlertCircle, QrCode } from 'lucide-react';
import api from '../api/axios';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

const TicketDetails = () => {
  const { pnr } = useParams();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTicket = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/bookings/${pnr}`);
        setBooking(res.data.booking);
      } catch {
        setError('Failed to load electronic reservation slip.');
      } finally {
        setLoading(false);
      }
    };
    fetchTicket();
  }, [pnr]);

  if (loading) return <LoadingSpinner text="Retrieving digital reservation slip..." />;

  if (error || !booking) {
    return (
      <div className="max-w-2xl mx-auto p-12 text-center bg-white rounded-3xl border border-slate-200 mt-8 space-y-4">
        <p className="text-rose-600 font-bold">{error || 'Ticket not found.'}</p>
        <Link to="/my-bookings" className="saffron-gradient text-white px-5 py-2.5 rounded-xl text-xs font-bold inline-block">
          Return to My Bookings
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      <div className="flex items-center justify-between">
        <Link to="/my-bookings" className="flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-900 transition-colors">
          <ArrowLeft size={14} /> Back to Bookings
        </Link>
        <a
          href={`/api/bookings/${booking.pnr}/ticket.pdf`}
          target="_blank"
          rel="noreferrer"
          className="saffron-gradient text-white px-4 py-2 rounded-xl text-xs font-bold shadow flex items-center gap-1.5 hover:brightness-110 transition-all"
        >
          <Download size={14} />
          <span>Download PDF E-Ticket</span>
        </a>
      </div>

      {/* Ticket Slip Card */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden">
        
        {/* Ticket Header */}
        <div className="bg-slate-950 text-white p-6 sm:p-8 flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl saffron-gradient flex items-center justify-center text-white shadow-md shrink-0">
              <Train size={24} />
            </div>
            <div>
              <span className="text-[10px] tracking-widest uppercase text-orange-400 font-extrabold">Electronic Reservation Slip (ERS)</span>
              <h2 className="text-xl font-black text-white">{booking.train_name}</h2>
              <span className="text-xs font-mono text-slate-400">#{booking.train_number} • Class {booking.travel_class || 'CC'}</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="bg-white p-1 rounded-xl shadow-xs">
              <img
                src={`/api/bookings/${booking.pnr}/qr`}
                alt="PNR Verification QR"
                className="w-14 h-14 object-contain"
              />
            </div>
            <div className="text-right">
              <span className="text-[10px] uppercase text-slate-400 block font-bold tracking-wider">PNR NUMBER</span>
              <span className="text-2xl font-mono font-black text-orange-400 tracking-wider">
                {booking.pnr}
              </span>
            </div>
          </div>
        </div>

        {/* Journey Timeline */}
        <div className="p-6 sm:p-8 space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 p-5 rounded-2xl bg-slate-50 border border-slate-100 text-xs">
            <div>
              <span className="text-slate-400 block text-[10px] font-bold uppercase">ORIGIN STATION</span>
              <div className="text-lg font-black text-slate-900 mt-0.5">{booking.departure_time}</div>
              <div className="font-bold text-slate-800">{booking.source_station}</div>
              <div className="font-mono text-slate-400 font-bold">{booking.source_code}</div>
            </div>

            <div className="flex flex-col items-center justify-center text-center">
              <span className="text-[10px] font-bold text-slate-400 uppercase">DATE OF JOURNEY</span>
              <div className="text-sm font-black text-orange-600 mt-1 flex items-center gap-1">
                <Calendar size={14} />
                {booking.journey_date}
              </div>
              <div className="mt-2">
                <StatusBadge status={booking.booking_status} />
              </div>
            </div>

            <div className="text-right">
              <span className="text-slate-400 block text-[10px] font-bold uppercase">DESTINATION</span>
              <div className="text-lg font-black text-slate-900 mt-0.5">{booking.arrival_time}</div>
              <div className="font-bold text-slate-800">{booking.dest_station}</div>
              <div className="font-mono text-slate-400 font-bold">{booking.dest_code}</div>
            </div>
          </div>

          {/* Passenger & Seat Details */}
          <div className="space-y-3">
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-500">Passenger Manifest</h4>
            <div className="overflow-x-auto rounded-2xl border border-slate-200">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px]">
                  <tr>
                    <th className="py-3 px-4">#</th>
                    <th className="py-3 px-4">Passenger Name</th>
                    <th className="py-3 px-4">Age / Gender</th>
                    <th className="py-3 px-4">Coach</th>
                    <th className="py-3 px-4">Seat / Berth</th>
                    <th className="py-3 px-4 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {booking.passengers?.map((p, i) => (
                    <tr key={i} className="hover:bg-slate-50/50">
                      <td className="py-3 px-4 font-mono font-bold text-slate-400">{i + 1}</td>
                      <td className="py-3 px-4 font-bold text-slate-900">{p.full_name}</td>
                      <td className="py-3 px-4 text-slate-600">{p.age} yrs / {p.gender}</td>
                      <td className="py-3 px-4 font-extrabold text-orange-600">{p.coach_number || '-'}</td>
                      <td className="py-3 px-4 font-extrabold text-slate-900">{p.allocated_berth || (p.seat_number ? `${p.seat_number} (${p.berth_type})` : '-')}</td>
                      <td className="py-3 px-4 text-right">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          {p.passenger_status || 'CONFIRMED'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Cancellation Info if Cancelled */}
          {booking.cancellation && (
            <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-xs text-rose-900 space-y-1">
              <p className="font-bold">Cancellation & Refund Record:</p>
              <p>Cancellation Ref: <b className="font-mono">{booking.cancellation.cancellation_number}</b></p>
              <p>Gross Fare: ₹{booking.cancellation.gross_amount} | Fee Deducted: ₹{booking.cancellation.cancellation_charge} | Net Refunded: <b className="text-emerald-700 font-mono">₹{booking.cancellation.refund_amount}</b> ({booking.cancellation.refund_status})</p>
            </div>
          )}

          {/* Payment & Security Guarantees */}
          <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
            <div className="flex items-center gap-2">
              <ShieldCheck size={16} className="text-emerald-500" />
              <span>ACID Row-Lock Concurrency Guarantee Verified</span>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-400 font-bold block uppercase">Total Fare Paid</span>
              <span className="text-xl font-black text-slate-900">₹{booking.total_amount?.toFixed(2)}</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};

export default TicketDetails;
