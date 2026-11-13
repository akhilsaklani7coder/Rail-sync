import React from 'react';
import { Link } from 'react-router-dom';
import { Train, Database, Cpu, ShieldCheck, ArrowRight } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-slate-950 text-slate-400 border-t border-slate-800 text-sm mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          
          {/* Brand Info */}
          <div className="space-y-3 md:col-span-1">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl saffron-gradient flex items-center justify-center text-white shadow-sm">
                <Train size={18} />
              </div>
              <span className="font-black text-xl text-white">RailSync</span>
            </Link>
            <p className="text-xs text-slate-400 leading-relaxed">
              Full-Stack Indian Railway Reservation System built for academic Project-Based Learning (Phase 2 Prototype).
            </p>
            <div className="flex items-center gap-2 text-xs text-emerald-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>MySQL InnoDB & C++ Native Engine Active</span>
            </div>
          </div>

          {/* Working Quick Navigation Links */}
          <div>
            <h4 className="text-white font-bold text-xs uppercase tracking-wider mb-3">Portal Navigation</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link to="/" className="hover:text-white transition-colors">
                  Home Portal
                </Link>
              </li>
              <li>
                <Link to="/search" className="hover:text-white transition-colors">
                  Search Trains & Schedules
                </Link>
              </li>
              <li>
                <Link to="/pnr-status" className="hover:text-white transition-colors">
                  Check PNR Status
                </Link>
              </li>
              <li>
                <Link to="/my-bookings" className="hover:text-white transition-colors">
                  My Bookings & E-Tickets
                </Link>
              </li>
              <li>
                <Link to="/profile" className="hover:text-white transition-colors">
                  Passenger Profile & Account
                </Link>
              </li>
              <li>
                <Link to="/login" className="hover:text-white transition-colors">
                  Sign In / Register
                </Link>
              </li>
            </ul>
          </div>

          {/* Railway Platform Features */}
          <div>
            <h4 className="text-white font-bold text-xs uppercase tracking-wider mb-3">Railway Platform Features</h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center gap-1.5 text-slate-300">
                <Train size={13} className="text-orange-400 shrink-0" />
                <span>IRCTC-Inspired Multi-Class Booking</span>
              </li>
              <li className="flex items-center gap-1.5 text-slate-300">
                <Cpu size={13} className="text-orange-400 shrink-0" />
                <span>C++17 Dijkstra Shortest-Path Route Engine</span>
              </li>
              <li className="flex items-center gap-1.5 text-slate-300">
                <Database size={13} className="text-indigo-400 shrink-0" />
                <span>MySQL 8.4 InnoDB ACID Concurrency & Row-Locking</span>
              </li>
              <li className="flex items-center gap-1.5 text-slate-300">
                <ShieldCheck size={13} className="text-emerald-400 shrink-0" />
                <span>Automated Waitlist (WL/RAC) Queue Promotion</span>
              </li>
            </ul>
          </div>

          {/* Simulation Notice */}
          <div>
            <h4 className="text-white font-bold text-xs uppercase tracking-wider mb-3">Simulation Notice</h4>
            <p className="text-xs text-slate-400 leading-relaxed mb-3">
              RailSync is an educational railway reservation simulation system. It does not connect to live Indian Railways/IRCTC servers and payments are simulated.
            </p>
            <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
              <ShieldCheck size={18} className="text-orange-500 shrink-0" />
              <span>Full-stack reservation engine with PDF tickets & QR verification.</span>
            </div>
          </div>

        </div>

        <div className="border-t border-slate-800/80 mt-10 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-3">
          <p>© 2026 RailSync — Full-Stack Indian Railway Reservation PBL System.</p>
          <div className="flex items-center gap-3">
            <span>React 19 & Vite</span>
            <span>•</span>
            <span>Flask REST API</span>
            <span>•</span>
            <span>MySQL 8.4 InnoDB</span>
            <span>•</span>
            <span>C++17 Engine</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
