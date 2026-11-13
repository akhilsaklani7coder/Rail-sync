import React, { useState, useEffect } from 'react';
import { Ticket, Search, Download } from 'lucide-react';
import api from '../api/axios';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

const ManageBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    const fetchBookings = async () => {
      setLoading(true);
      try {
        const res = await api.get('/admin/bookings');
        setBookings(res.data.bookings || []);
      } catch (err) {
        console.error("Failed to fetch all bookings", err);
      } finally {
        setLoading(false);
      }
    };
    fetchBookings();
  }, []);

  if (loading) return <LoadingSpinner text="Querying all reservation logs from MySQL..." />;

  const filtered = bookings.filter((b) => {
    const matchesSearch =
      b.pnr.toLowerCase().includes(searchTerm.toLowerCase()) ||
      b.user_email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      b.train_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || b.booking_status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">System Reservation Records</h2>
          <p className="text-xs text-slate-400">Audit trail of all passenger bookings, transactions, and cancellations.</p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <div className="relative">
            <input
              type="text"
              placeholder="Search PNR, User, Train..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-orange-500/30"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300 font-bold"
          >
            <option value="ALL">All Statuses</option>
            <option value="CONFIRMED">CONFIRMED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>
        </div>
      </div>

      <div className="bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
              <th className="py-3 px-4">PNR</th>
              <th className="py-3 px-4">Passenger / User</th>
              <th className="py-3 px-4">Train Details</th>
              <th className="py-3 px-4">Route</th>
              <th className="py-3 px-4">Journey Date</th>
              <th className="py-3 px-4">Amount</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">PDF Ticket</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-300">
            {filtered.map((b) => (
              <tr key={b.id} className="hover:bg-slate-900/50">
                <td className="py-3 px-4 font-mono font-bold text-orange-400">{b.pnr}</td>
                <td className="py-3 px-4">
                  <div className="font-bold text-white">{b.user_name}</div>
                  <div className="text-[10px] text-slate-400">{b.user_email}</div>
                </td>
                <td className="py-3 px-4">
                  <span className="font-semibold text-white">{b.train_name}</span>
                  <span className="text-slate-500 font-mono text-[10px] block">#{b.train_number}</span>
                </td>
                <td className="py-3 px-4 font-mono text-xs">{b.source_code} → {b.dest_code}</td>
                <td className="py-3 px-4">{b.journey_date}</td>
                <td className="py-3 px-4 font-bold text-white">₹{b.total_amount?.toFixed(2)}</td>
                <td className="py-3 px-4">
                  <StatusBadge status={b.booking_status} />
                </td>
                <td className="py-3 px-4 text-right">
                  <a
                    href={`/api/bookings/${b.pnr}/ticket.pdf`}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1.5 rounded-lg text-slate-400 hover:text-orange-400 inline-block"
                    title="Download Ticket"
                  >
                    <Download size={15} />
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
};

export default ManageBookings;
