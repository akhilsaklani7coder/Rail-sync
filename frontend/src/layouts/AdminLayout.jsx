import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { LayoutDashboard, Train, MapPin, TicketCheck, ArrowLeft, Shield, Cpu } from 'lucide-react';

const AdminLayout = () => {
  const location = useLocation();

  const navItems = [
    { label: 'Dashboard Overview', path: '/admin', icon: LayoutDashboard },
    { label: 'Train Fleet', path: '/admin/trains', icon: Train },
    { label: 'Station Network', path: '/admin/stations', icon: MapPin },
    { label: 'System Bookings', path: '/admin/bookings', icon: TicketCheck },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <div className="bg-slate-900 border-b border-slate-800 py-4 px-4 sm:px-8">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider bg-orange-600 text-white uppercase">
                Admin Control Center
              </span>
              <h1 className="text-xl font-black text-white">RailSync Administration & Telemetry</h1>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Live railway fleet scheduling, station corridors, booking audit trail, and MySQL transaction monitoring.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Link
              to="/"
              className="flex items-center gap-1.5 text-xs font-bold px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
            >
              <ArrowLeft size={14} />
              <span>Back to Portal</span>
            </Link>
          </div>
        </div>

        {/* Admin Navigation Pills */}
        <div className="max-w-7xl mx-auto mt-4 flex items-center gap-2 overflow-x-auto pb-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isCurrent = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                  isCurrent
                    ? 'saffron-gradient text-white shadow-md'
                    : 'bg-slate-800/80 text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <Icon size={14} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        <Outlet />
      </main>

      <Footer />
    </div>
  );
};

export default AdminLayout;
