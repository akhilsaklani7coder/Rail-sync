import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Users, Train, Ticket, CheckCircle2, XCircle, IndianRupee, ArrowRight, Shield, Cpu, RefreshCw, Database, Download } from 'lucide-react';
import api from '../api/axios';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

const AdminDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const [dashRes, diagRes] = await Promise.all([
        api.get('/admin/dashboard'),
        api.get('/admin/diagnostics')
      ]);
      setData({ ...dashRes.data, diagnostics: diagRes.data });
    } catch (err) {
      console.error("Failed to load admin metrics", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) return <LoadingSpinner text="Aggregating metrics from MySQL InnoDB..." />;

  const m = data?.metrics || {};
  const recent = data?.recent_bookings || [];
  const diag = data?.diagnostics || {};

  return (
    <div className="space-y-8">
      
      {/* Stat Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        
        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Total Registered Users</span>
            <Users size={16} className="text-orange-500" />
          </div>
          <div className="text-3xl font-black text-white mt-2">{m.total_users || 0}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Live passenger accounts in MySQL</span>
        </div>

        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Active Trains</span>
            <Train size={16} className="text-orange-500" />
          </div>
          <div className="text-3xl font-black text-white mt-2">{m.total_trains || 0}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Express, Shatabdi & Vande Bharat</span>
        </div>

        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Simulated Revenue</span>
            <IndianRupee size={16} className="text-emerald-500" />
          </div>
          <div className="text-3xl font-black text-emerald-400 mt-2">₹{m.total_revenue?.toFixed(2) || '0.00'}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">From confirmed simulated bookings</span>
        </div>

        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Total Bookings</span>
            <Ticket size={16} className="text-indigo-400" />
          </div>
          <div className="text-3xl font-black text-white mt-2">{m.total_bookings || 0}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Cumulative reservation records</span>
        </div>

        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Confirmed Bookings</span>
            <CheckCircle2 size={16} className="text-emerald-500" />
          </div>
          <div className="text-3xl font-black text-emerald-400 mt-2">{m.confirmed_bookings || 0}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Active seats locked in MySQL</span>
        </div>

        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Cancelled Bookings</span>
            <XCircle size={16} className="text-rose-500" />
          </div>
          <div className="text-3xl font-black text-rose-400 mt-2">{m.cancelled_bookings || 0}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Released back to availability</span>
        </div>

      </div>

      {/* OS & DBMS Telemetry Panel (Integrated into Admin Dashboard) */}
      {diag.status && (
        <div className="bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-xl space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-2">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-orange-500/20 text-orange-400 flex items-center justify-center">
                <Cpu size={18} />
              </div>
              <div>
                <h3 className="font-black text-base text-white">System Engine & Concurrency Telemetry</h3>
                <p className="text-xs text-slate-400">Verified OS primitives and database guarantees in current runtime.</p>
              </div>
            </div>
            <button
              onClick={fetchDashboard}
              className="flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 self-start sm:self-auto"
            >
              <RefreshCw size={12} />
              <span>Refresh Metrics</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2 text-orange-400 font-bold uppercase text-[10px]">
                <Cpu size={14} />
                <span>C++ Native Engine</span>
              </div>
              <div className="text-slate-200 font-semibold">{diag.cpp_engine?.mode || 'Active'}</div>
              <p className="text-slate-400 text-[11px]">
                Guarded by <code className="text-orange-300">std::mutex</code> with deterministic contiguous seat allocation.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2 text-indigo-400 font-bold uppercase text-[10px]">
                <Database size={14} />
                <span>MySQL 8.4 InnoDB ACID</span>
              </div>
              <div className="text-slate-200 font-semibold">{diag.database?.rdbms}</div>
              <p className="text-slate-400 text-[11px]">
                Row-level locking via <code className="text-indigo-300">SELECT ... FOR UPDATE</code> with foreign key enforcement.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2 text-emerald-400 font-bold uppercase text-[10px]">
                <Shield size={14} />
                <span>Concurrency Controls</span>
              </div>
              <div className="text-slate-200 font-semibold">{diag.os_primitives?.counting_semaphore}</div>
              <p className="text-slate-400 text-[11px]">
                Dijkstra graph min-heap: <code className="text-emerald-300">O((V+E)log V)</code>.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Recent Bookings Table */}
      <div className="bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="font-black text-white text-base">Recent Railway Reservations</h3>
            <p className="text-xs text-slate-400">Latest passenger bookings across all routes.</p>
          </div>
          <Link to="/admin/bookings" className="text-xs font-bold text-orange-400 hover:text-orange-300 flex items-center gap-1">
            <span>View All Records</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
              <tr>
                <th className="py-3 px-4">PNR</th>
                <th className="py-3 px-4">Passenger</th>
                <th className="py-3 px-4">Train</th>
                <th className="py-3 px-4">Route</th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">PDF</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {recent.map((b) => (
                <tr key={b.id} className="hover:bg-slate-800/40">
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
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white inline-flex"
                      title="Download PDF"
                    >
                      <Download size={13} />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default AdminDashboard;
