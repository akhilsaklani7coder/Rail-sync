import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, Train, Calendar, MapPin, ArrowRight, ArrowLeftRight, 
  Cpu, Database, CheckCircle2, Route, Clock, Ticket, Lock, Zap,
  Compass, AlertCircle, ShieldCheck, Download, RefreshCw
} from 'lucide-react';
import api from '../api/axios';
import { useToast } from '../context/ToastContext';
import StatusBadge from '../components/StatusBadge';

const Home = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();

  // Search Panel Tabs
  const [activeTab, setActiveTab] = useState('BOOK'); // 'BOOK', 'PNR', 'ROUTE'

  // Tab 1: Book Tickets State
  const [stations, setStations] = useState([]);
  const [sourceId, setSourceId] = useState('');
  const [destId, setDestId] = useState('');
  const [journeyDate, setJourneyDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split('T')[0];
  });
  const [loadingStations, setLoadingStations] = useState(true);
  const [stationsError, setStationsError] = useState(null);
  const [stationFilter, setStationFilter] = useState('');

  // Tab 2: PNR Status State
  const [pnrQuery, setPnrQuery] = useState('');
  const [pnrResult, setPnrResult] = useState(null);
  const [pnrLoading, setPnrLoading] = useState(false);
  const [pnrError, setPnrError] = useState('');

  // Tab 3: Route Planning (C++ Dijkstra Native Engine)
  const [plannerSrc, setPlannerSrc] = useState('');
  const [plannerDst, setPlannerDst] = useState('');
  const [plannerResult, setPlannerResult] = useState(null);
  const [plannerLoading, setPlannerLoading] = useState(false);

  // Dynamic Data from MySQL Backend
  const [popularRoutes, setPopularRoutes] = useState([]);
  const [featuredTrains, setFeaturedTrains] = useState([]);
  const [loadingRoutes, setLoadingRoutes] = useState(true);

  // Validation
  const isSameStation = sourceId && destId && Number(sourceId) === Number(destId);
  const minDate = new Date().toISOString().split('T')[0];

  // Dedicated station loader with automatic fallback and error tracking
  const loadStations = useCallback(async () => {
    setLoadingStations(true);
    setStationsError(null);
    try {
      let res;
      try {
        res = await api.get('/stations');
      } catch (e1) {
        // Fallback to legacy endpoint if /stations fails
        res = await api.get('/trains/stations');
      }

      const sts = res.data.stations || [];
      setStations(sts);
      if (sts.length >= 2) {
        setSourceId(prev => (prev && sts.some(s => s.id === Number(prev)) ? prev : sts[0].id));
        setDestId(prev => (prev && sts.some(s => s.id === Number(prev)) ? prev : sts[1].id));
        setPlannerSrc(prev => (prev && sts.some(s => s.id === Number(prev)) ? prev : sts[0].id));
        setPlannerDst(prev => (prev && sts.some(s => s.id === Number(prev)) ? prev : sts[sts.length - 1].id));
      }
    } catch (err) {
      console.error("Failed to load railway stations from MySQL", err);
      setStationsError("Could not retrieve stations from database. Please verify backend service.");
      showToast("Error connecting to railway database.", "error");
    } finally {
      setLoadingStations(false);
    }
  }, [showToast]);

  // Load secondary marketing & route cards
  const loadSecondaryData = useCallback(async () => {
    try {
      const [routeRes, trainRes] = await Promise.allSettled([
        api.get('/trains/popular-routes'),
        api.get('/trains/featured')
      ]);
      if (routeRes.status === 'fulfilled') {
        setPopularRoutes(routeRes.value.data.routes || []);
      }
      if (trainRes.status === 'fulfilled') {
        setFeaturedTrains(trainRes.value.data.trains || []);
      }
    } catch (e) {
      console.warn("Secondary train card loading error", e);
    } finally {
      setLoadingRoutes(false);
    }
  }, []);

  useEffect(() => {
    loadStations();
    loadSecondaryData();
  }, [loadStations, loadSecondaryData]);

  const handleSwapStations = () => {
    if (sourceId && destId) {
      const prevSrc = sourceId;
      setSourceId(destId);
      setDestId(prevSrc);
      showToast("Stations swapped", "info", 1500);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!sourceId || !destId) {
      showToast("Please select both source and destination stations.", "error");
      return;
    }
    if (isSameStation) {
      showToast("Origin and destination cannot be the same station.", "error");
      return;
    }
    navigate(`/search?source_id=${sourceId}&dest_id=${destId}&date=${journeyDate}`);
  };

  const handlePnrLookup = async (e) => {
    e.preventDefault();
    if (!pnrQuery.trim()) return;

    setPnrLoading(true);
    setPnrError('');
    setPnrResult(null);

    try {
      const res = await api.get(`/bookings/${pnrQuery.trim().toUpperCase()}`);
      setPnrResult(res.data.booking);
    } catch (err) {
      setPnrError(err.message || 'No booking found matching this PNR.');
    } finally {
      setPnrLoading(false);
    }
  };

  const handleRunPlanner = async (e) => {
    if (e) e.preventDefault();
    if (!plannerSrc || !plannerDst) return;
    if (Number(plannerSrc) === Number(plannerDst)) {
      showToast("Origin and destination must be distinct for route calculation.", "error");
      return;
    }
    setPlannerLoading(true);
    try {
      const res = await api.get(`/trains/shortest-path?source_id=${plannerSrc}&dest_id=${plannerDst}`);
      setPlannerResult(res.data);
      showToast("Shortest path computed via C++ Dijkstra Engine!", "success", 2500);
    } catch (err) {
      showToast(err.message || "Failed to calculate shortest path", "error");
    } finally {
      setPlannerLoading(false);
    }
  };

  const handleRouteCardClick = (srcId, dstId) => {
    setSourceId(srcId);
    setDestId(dstId);
    navigate(`/search?source_id=${srcId}&dest_id=${dstId}&date=${journeyDate}`);
  };

  // Helper map for destination images
  const getDestinationImage = (cityName) => {
    const city = (cityName || '').toLowerCase();
    if (city.includes('delhi')) return '/delhi.jpg';
    if (city.includes('mumbai')) return '/mumbai.jpg';
    if (city.includes('jaipur')) return '/jaipur.jpg';
    if (city.includes('varanasi') || city.includes('haridwar') || city.includes('dehradun')) return '/varanasi.jpg';
    return '/delhi.jpg';
  };

  return (
    <div className="space-y-16 sm:space-y-24 pb-20">
      
      {/* Cinematic Hero Section */}
      <section className="relative min-h-[640px] lg:min-h-[700px] flex items-center bg-slate-950 overflow-hidden text-white">
        
        {/* Photographic Background with Layered Navy Gradients */}
        <div className="absolute inset-0 z-0">
          <img
            src="/hero-train.jpg"
            alt="Modern Indian Railway Vande Bharat Express on Scenic Bridge"
            className="w-full h-full object-cover object-center"
          />
          {/* Deep Navy/Black Gradient Overlay for Maximum Readability */}
          <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/85 to-slate-900/70"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-slate-950/50"></div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 w-full">
          
          <div className="max-w-3xl space-y-5">
            
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-orange-500/15 border border-orange-500/30 text-orange-400 text-xs font-semibold backdrop-blur-md">
              <span className="w-2 h-2 rounded-full bg-orange-500 animate-pulse"></span>
              <span>RailSync 2.0 • Full-Stack Indian Railway Reservation</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-tight">
              Your Journey, <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-amber-300">
                Seamlessly Connected.
              </span>
            </h1>

            <p className="text-slate-300 text-base sm:text-lg max-w-2xl font-normal leading-relaxed">
              Search trains, reserve seats, track bookings, and discover connected routes through a smarter railway reservation experience.
            </p>

          </div>

          {/* Unified High-Contrast Booking Search Panel */}
          <div className="mt-8 sm:mt-12 bg-white text-slate-900 rounded-3xl p-5 sm:p-7 shadow-2xl border border-slate-100 max-w-5xl backdrop-blur-xl">
            
            {/* Unified Mode Tabs */}
            <div className="flex items-center gap-2 pb-5 border-b border-slate-100 overflow-x-auto">
              <button
                type="button"
                onClick={() => setActiveTab('BOOK')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer whitespace-nowrap ${
                  activeTab === 'BOOK'
                    ? 'bg-slate-950 text-white shadow-md'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                <Train size={16} className={activeTab === 'BOOK' ? 'text-orange-400' : 'text-slate-500'} />
                <span>Book Tickets</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('PNR')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer whitespace-nowrap ${
                  activeTab === 'PNR'
                    ? 'bg-slate-950 text-white shadow-md'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                <Ticket size={16} className={activeTab === 'PNR' ? 'text-orange-400' : 'text-slate-500'} />
                <span>PNR Status</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('ROUTE')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer whitespace-nowrap ${
                  activeTab === 'ROUTE'
                    ? 'bg-slate-950 text-white shadow-md'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                <Route size={16} className={activeTab === 'ROUTE' ? 'text-orange-400' : 'text-slate-500'} />
                <span>Plan Route (C++ Dijkstra)</span>
              </button>
            </div>

            {/* TAB 1: BOOK TICKETS */}
            {activeTab === 'BOOK' && (
              <div>
                {/* Error Banner with Retry */}
                {stationsError && (
                  <div className="mt-4 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 flex flex-col sm:flex-row items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
                      <span className="text-xs sm:text-sm font-semibold">{stationsError}</span>
                    </div>
                    <button
                      type="button"
                      onClick={loadStations}
                      className="px-3.5 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 shrink-0 cursor-pointer shadow-sm"
                    >
                      <RefreshCw size={12} className={loadingStations ? 'animate-spin' : ''} />
                      Retry Loading Stations
                    </button>
                  </div>
                )}

                {/* Quick Station Filter Bar */}
                {stations.length > 0 && (
                  <div className="mt-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs text-slate-500 pb-1">
                    <div className="flex items-center gap-1.5 font-medium text-slate-600">
                      <CheckCircle2 size={13} className="text-emerald-500" />
                      <span>{stations.length} Indian Railway Stations Available</span>
                    </div>
                    <div className="flex items-center gap-1.5 w-full sm:w-auto">
                      <Search size={13} className="text-slate-400" />
                      <input
                        type="text"
                        placeholder="Filter stations by city/code..."
                        value={stationFilter}
                        onChange={(e) => setStationFilter(e.target.value)}
                        className="px-2.5 py-1 rounded-lg border border-slate-200 text-xs bg-slate-50 focus:outline-none focus:ring-1 focus:ring-orange-500 w-full sm:w-56"
                      />
                      {stationFilter && (
                        <button
                          type="button"
                          onClick={() => setStationFilter('')}
                          className="text-[11px] text-slate-400 hover:text-slate-600"
                        >
                          Clear
                        </button>
                      )}
                    </div>
                  </div>
                )}

                <form onSubmit={handleSearchSubmit} className="mt-3 grid grid-cols-1 md:grid-cols-11 gap-4 items-end">
                  {/* Origin Station */}
                  <div className="md:col-span-3 space-y-1.5">
                    <label className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                      <MapPin size={14} className="text-orange-500" />
                      From Station
                    </label>
                    <select
                      value={sourceId}
                      onChange={(e) => setSourceId(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-3 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-orange-500/30 focus:border-orange-500 transition-all cursor-pointer disabled:bg-slate-100 disabled:text-slate-400"
                      disabled={loadingStations || stations.length === 0}
                    >
                      {loadingStations && <option value="">Loading railway stations...</option>}
                      {!loadingStations && stations.length === 0 && <option value="">No stations available</option>}
                      {stations
                        .filter(s => !stationFilter.trim() || 
                                     s.station_name.toLowerCase().includes(stationFilter.toLowerCase()) || 
                                     s.station_code.toLowerCase().includes(stationFilter.toLowerCase()) || 
                                     s.city.toLowerCase().includes(stationFilter.toLowerCase()) ||
                                     s.id === Number(sourceId))
                        .map(s => (
                          <option key={s.id} value={s.id} disabled={s.id === Number(destId)}>
                            {s.city} ({s.station_code}) - {s.station_name}
                          </option>
                        ))}
                    </select>
                  </div>

                  {/* Swap Button */}
                  <div className="md:col-span-1 flex items-center justify-center pb-1">
                    <button
                      type="button"
                      onClick={handleSwapStations}
                      disabled={loadingStations || stations.length < 2}
                      className="w-10 h-10 rounded-full bg-slate-100 hover:bg-orange-50 hover:text-orange-600 text-slate-600 border border-slate-200 flex items-center justify-center transition-all cursor-pointer hover:rotate-180 duration-300 disabled:opacity-40 disabled:cursor-not-allowed"
                      title="Swap Origin and Destination"
                      aria-label="Swap stations"
                    >
                      <ArrowLeftRight size={16} />
                    </button>
                  </div>

                  {/* Destination Station */}
                  <div className="md:col-span-3 space-y-1.5">
                    <label className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                      <MapPin size={14} className="text-orange-500" />
                      To Station
                    </label>
                    <select
                      value={destId}
                      onChange={(e) => setDestId(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-3 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-orange-500/30 focus:border-orange-500 transition-all cursor-pointer disabled:bg-slate-100 disabled:text-slate-400"
                      disabled={loadingStations || stations.length === 0}
                    >
                      {loadingStations && <option value="">Loading railway stations...</option>}
                      {!loadingStations && stations.length === 0 && <option value="">No stations available</option>}
                      {stations
                        .filter(s => !stationFilter.trim() || 
                                     s.station_name.toLowerCase().includes(stationFilter.toLowerCase()) || 
                                     s.station_code.toLowerCase().includes(stationFilter.toLowerCase()) || 
                                     s.city.toLowerCase().includes(stationFilter.toLowerCase()) ||
                                     s.id === Number(destId))
                        .map(s => (
                          <option key={s.id} value={s.id} disabled={s.id === Number(sourceId)}>
                            {s.city} ({s.station_code}) - {s.station_name}
                          </option>
                        ))}
                    </select>
                  </div>

                  {/* Journey Date */}
                  <div className="md:col-span-2 space-y-1.5">
                    <label className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                      <Calendar size={14} className="text-orange-500" />
                      Journey Date
                    </label>
                    <input
                      type="date"
                      min={minDate}
                      value={journeyDate}
                      onChange={(e) => setJourneyDate(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-orange-500/30 focus:border-orange-500 transition-all cursor-pointer"
                      required
                    />
                  </div>

                  {/* Submit Action */}
                  <div className="md:col-span-2">
                    <button
                      type="submit"
                      disabled={loadingStations || isSameStation || stations.length === 0}
                      className="w-full saffron-gradient hover:brightness-110 text-white font-bold py-3 px-4 rounded-xl shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Search size={16} />
                      <span>Search Trains</span>
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* TAB 2: PNR STATUS */}
            {activeTab === 'PNR' && (
              <div className="mt-5 space-y-4">
                <form onSubmit={handlePnrLookup} className="flex flex-col sm:flex-row gap-3">
                  <input
                    type="text"
                    required
                    maxLength={12}
                    value={pnrQuery}
                    onChange={(e) => setPnrQuery(e.target.value.toUpperCase())}
                    placeholder="Enter 10-character PNR (e.g. RS29384751)"
                    className="flex-1 font-mono font-bold tracking-wider uppercase bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/30 focus:border-orange-500"
                  />
                  <button
                    type="submit"
                    disabled={pnrLoading}
                    className="saffron-gradient hover:brightness-110 text-white font-bold px-6 py-3 rounded-xl shadow transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95 text-sm disabled:opacity-50"
                  >
                    <Search size={16} />
                    <span>{pnrLoading ? 'Verifying...' : 'Check PNR Status'}</span>
                  </button>
                </form>

                {pnrError && (
                  <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
                    <AlertCircle size={15} />
                    <span>{pnrError}</span>
                  </div>
                )}

                {pnrResult && (
                  <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-200 gap-2">
                      <div>
                        <span className="text-[10px] font-mono uppercase font-bold text-slate-400">PNR NUMBER</span>
                        <div className="font-mono font-black text-xl text-slate-900">{pnrResult.pnr}</div>
                      </div>
                      <div className="flex items-center gap-3">
                        <StatusBadge status={pnrResult.booking_status} />
                        <a
                          href={`/api/bookings/${pnrResult.pnr}/ticket.pdf`}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center gap-1.5 text-xs font-bold text-orange-600 hover:text-orange-700 bg-orange-50 border border-orange-200 px-3 py-1.5 rounded-lg"
                        >
                          <Download size={14} />
                          <span>PDF Ticket</span>
                        </a>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                      <div>
                        <span className="text-slate-400 block font-medium">Train</span>
                        <div className="font-bold text-slate-900">{pnrResult.train_name} (#{pnrResult.train_number})</div>
                      </div>
                      <div>
                        <span className="text-slate-400 block font-medium">Route</span>
                        <div className="font-bold text-slate-900">{pnrResult.source_station} → {pnrResult.dest_station}</div>
                      </div>
                      <div>
                        <span className="text-slate-400 block font-medium">Date of Journey</span>
                        <div className="font-bold text-slate-900">{pnrResult.journey_date}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: PLAN ROUTE (C++ DIJKSTRA) */}
            {activeTab === 'ROUTE' && (
              <div className="mt-5 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-11 gap-3 items-end">
                  <div className="sm:col-span-5 space-y-1.5">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Start Station</label>
                    <select
                      value={plannerSrc}
                      onChange={(e) => setPlannerSrc(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-orange-500/30 cursor-pointer"
                    >
                      {stations.map(s => (
                        <option key={s.id} value={s.id} disabled={s.id === Number(plannerDst)}>
                          {s.city} ({s.station_code}) - {s.station_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="sm:col-span-1 flex items-center justify-center pb-0.5">
                    <button
                      type="button"
                      onClick={() => {
                        const prev = plannerSrc;
                        setPlannerSrc(plannerDst);
                        setPlannerDst(prev);
                      }}
                      className="w-9 h-9 rounded-full bg-slate-100 hover:bg-orange-50 hover:text-orange-600 text-slate-600 border border-slate-200 flex items-center justify-center transition-all cursor-pointer"
                      title="Swap Start and Target"
                    >
                      <ArrowLeftRight size={14} />
                    </button>
                  </div>

                  <div className="sm:col-span-4 space-y-1.5">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Target Station</label>
                    <select
                      value={plannerDst}
                      onChange={(e) => setPlannerDst(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-orange-500/30 cursor-pointer"
                    >
                      {stations.map(s => (
                        <option key={s.id} value={s.id} disabled={s.id === Number(plannerSrc)}>
                          {s.city} ({s.station_code}) - {s.station_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="sm:col-span-1">
                    <button
                      type="button"
                      onClick={handleRunPlanner}
                      disabled={plannerLoading}
                      className="w-full saffron-gradient hover:brightness-110 text-white font-bold py-2.5 px-3 rounded-xl text-xs sm:text-sm transition-all flex items-center justify-center gap-1.5 shadow cursor-pointer disabled:opacity-50"
                    >
                      <Route size={15} />
                      <span>{plannerLoading ? 'Solving...' : 'Calculate'}</span>
                    </button>
                  </div>
                </div>

                {plannerResult && (
                  <div className="p-4 sm:p-5 rounded-2xl bg-slate-900 text-white border border-slate-800 space-y-3">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 border-b border-slate-800 gap-2">
                      <div className="text-xs sm:text-sm font-extrabold">
                        {plannerResult.source_station?.city} → {plannerResult.destination_station?.city}
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="px-2.5 py-1 rounded-lg bg-orange-500/20 text-orange-400 font-bold border border-orange-500/30">
                          Shortest Distance: {plannerResult.total_distance_km} km
                        </span>
                        <span className="px-2 py-1 rounded-lg bg-slate-800 text-slate-300 font-mono text-[11px]">
                          {plannerResult.hops} Hops
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 overflow-x-auto py-2">
                      {plannerResult.path?.map((st, idx) => (
                        <React.Fragment key={st.id}>
                          <div className="flex flex-col items-center p-2.5 rounded-xl bg-slate-950 border border-slate-800 min-w-[100px] shrink-0 text-center">
                            <span className="text-[10px] font-mono text-orange-400 font-bold">Node {idx + 1}</span>
                            <span className="text-xs font-bold text-white mt-0.5">{st.station_code}</span>
                            <span className="text-[10px] text-slate-400 truncate max-w-full">{st.city}</span>
                          </div>
                          {idx < plannerResult.path.length - 1 && (
                            <ArrowRight size={14} className="text-slate-600 shrink-0" />
                          )}
                        </React.Fragment>
                      ))}
                    </div>

                    <div className="flex items-center justify-between pt-1 text-[11px] text-slate-400">
                      <span>Engine: <strong className="text-slate-200">{plannerResult.engine}</strong></span>
                      <button
                        type="button"
                        onClick={() => navigate(`/search?source_id=${plannerSrc}&dest_id=${plannerDst}&date=${journeyDate}`)}
                        className="text-orange-400 hover:text-orange-300 font-bold flex items-center gap-1"
                      >
                        <span>Check available trains on this route</span>
                        <ArrowRight size={12} />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Error prompt if same origin & destination */}
            {isSameStation && activeTab === 'BOOK' && (
              <p className="text-xs text-rose-500 font-medium mt-3 flex items-center gap-1.5">
                <AlertCircle size={14} />
                Origin and destination cannot be identical. Please select different stations.
              </p>
            )}

          </div>

        </div>

      </section>

      {/* Popular Corridors Section with Authentic Destination Photography */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-orange-600 mb-1">
              <Zap size={14} />
              <span>High-Frequency Corridors</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">Popular Express Routes</h2>
            <p className="text-xs text-slate-500 mt-1">Book directly on high-demand seeded corridors across the Indian railway network.</p>
          </div>
          <button
            onClick={() => navigate('/search')}
            className="text-xs font-bold text-orange-600 hover:text-orange-700 flex items-center gap-1.5 cursor-pointer self-start sm:self-auto"
          >
            <span>Explore all trains</span>
            <ArrowRight size={14} />
          </button>
        </div>

        {loadingRoutes ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(n => (
              <div key={n} className="h-64 bg-slate-100 rounded-3xl animate-pulse"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {popularRoutes.map((r) => (
              <div
                key={r.route_id}
                onClick={() => handleRouteCardClick(r.source_id, r.dest_id)}
                className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-xl hover:border-orange-300 transition-all cursor-pointer group flex flex-col justify-between"
              >
                {/* Destination Image with Badge */}
                <div className="relative h-44 overflow-hidden bg-slate-900">
                  <img
                    src={getDestinationImage(r.dest_city)}
                    alt={`${r.dest_city} Railway Corridor`}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/30 to-transparent"></div>
                  
                  <div className="absolute top-3 left-3">
                    <span className="font-mono text-xs font-bold px-2.5 py-1 rounded-full bg-slate-950/80 backdrop-blur-md text-white border border-slate-700">
                      {r.source_code} → {r.dest_code}
                    </span>
                  </div>

                  <div className="absolute bottom-3 left-3 right-3 flex items-end justify-between text-white">
                    <div>
                      <h4 className="font-black text-lg text-white leading-tight">
                        {r.source_city} to {r.dest_city}
                      </h4>
                      <p className="text-[11px] text-slate-300 font-medium">{r.train_name}</p>
                    </div>
                  </div>
                </div>

                {/* Card Content & Metrics */}
                <div className="p-5 flex items-center justify-between text-xs">
                  <span className="text-slate-500 flex items-center gap-1.5 font-medium">
                    <Clock size={14} className="text-slate-400" />
                    {r.duration} • {r.distance_km} km
                  </span>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 block font-bold uppercase">From</span>
                    <span className="font-black text-slate-900 text-base">₹{r.base_fare?.toFixed(0)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Featured Flagship Express Trains */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-indigo-600 mb-1">
              <Train size={14} />
              <span>Flagship Fleet</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">Featured Express Trains</h2>
            <p className="text-xs text-slate-500 mt-1">Direct high-speed services with guaranteed coach allocations and modern amenities.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featuredTrains.slice(0, 6).map((train) => (
            <div
              key={train.id}
              className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm hover:shadow-md hover:border-orange-200 transition-all flex flex-col justify-between space-y-4"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-slate-900 text-white">
                    #{train.train_number}
                  </span>
                  <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                    {train.running_days}
                  </span>
                </div>
                <h3 className="font-extrabold text-slate-900 text-lg mt-3">{train.train_name}</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {train.source_name} ({train.source_code}) → {train.dest_name} ({train.dest_code})
                </p>
              </div>

              <div className="grid grid-cols-3 gap-2 py-3 px-3.5 bg-slate-50 rounded-2xl text-center text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 font-bold block">DEP</span>
                  <span className="font-extrabold text-slate-800">{train.departure_time}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-bold block">DURATION</span>
                  <span className="font-bold text-slate-600">{train.duration}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-bold block">ARR</span>
                  <span className="font-extrabold text-slate-800">{train.arrival_time}</span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <div>
                  <span className="text-[10px] text-slate-400 block font-bold">BASE FARE</span>
                  <span className="text-xl font-black text-slate-900">₹{train.base_fare?.toFixed(0)}</span>
                </div>
                <button
                  onClick={() => navigate(`/train/${train.id}`, { state: { train, journeyDate } })}
                  className="saffron-gradient text-white px-5 py-2.5 rounded-xl text-xs font-bold shadow hover:brightness-110 transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <span>Select Seats</span>
                  <ArrowRight size={13} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Scenic Photographic Travel Banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative rounded-3xl overflow-hidden bg-slate-950 text-white min-h-[360px] flex items-center p-8 sm:p-14 shadow-2xl">
          <img
            src="/scenic-banner.jpg"
            alt="Scenic Indian Railway journey through lush green tea hills"
            className="absolute inset-0 w-full h-full object-cover object-center"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/80 to-transparent"></div>

          <div className="relative z-10 max-w-xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/20 border border-orange-500/40 text-orange-400 text-xs font-bold">
              <Compass size={14} />
              <span>Discover India by Rail</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight leading-tight">
              Journeys That Inspire, Connected in Real Time.
            </h2>
            <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
              From majestic northern valleys to western coastal lines, reserve seats seamlessly with deterministic concurrency guarantees and verified route metrics.
            </p>
            <div className="pt-2">
              <button
                onClick={() => navigate('/search')}
                className="saffron-gradient hover:brightness-110 text-white font-bold px-6 py-3 rounded-xl text-xs sm:text-sm shadow-lg flex items-center gap-2 cursor-pointer active:scale-95 transition-all"
              >
                <span>Explore Railway Corridors</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* How RailSync Works — 4 Step Clean Flow */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-50 rounded-3xl p-8 sm:p-12 border border-slate-200 text-center space-y-10">
          <div className="max-w-xl mx-auto space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-orange-600">Step-by-Step Experience</span>
            <h2 className="text-3xl font-black text-slate-900 tracking-tight">How RailSync Works</h2>
            <p className="text-xs text-slate-500">From corridor discovery to confirmed electronic ticket in four simple steps.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 text-left">
            {[
              { step: '01', title: 'Search Trains', desc: 'Select origin and destination stations and your journey date across verified routes.' },
              { step: '02', title: 'Choose Seats', desc: 'Interactive coach seat map with real journey-specific date availability and berth types.' },
              { step: '03', title: 'Simulated Payment', desc: 'Instant gateway handshake simulation with transactional rollback safeguards.' },
              { step: '04', title: 'Receive Your Ticket', desc: 'Immediate transaction commit in MySQL, unique PNR, and downloadable vector PDF.' }
            ].map((item, idx) => (
              <div key={idx} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm relative hover:border-orange-300 transition-all">
                <span className="text-3xl font-black text-orange-500/20 font-mono absolute top-4 right-4">{item.step}</span>
                <h4 className="font-bold text-slate-900 text-base mt-2">{item.title}</h4>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why Choose RailSync — Engineering Architecture Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-orange-600">Core Architecture</span>
          <h2 className="text-3xl font-black text-slate-900 tracking-tight">Why Choose RailSync?</h2>
          <p className="text-xs text-slate-500">
            A real full-stack railway platform built on rigorous computer science primitives and database guarantees.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3 hover:border-slate-300 transition-all">
            <div className="w-11 h-11 rounded-2xl bg-orange-50 text-orange-600 flex items-center justify-center">
              <Database size={22} />
            </div>
            <h3 className="font-bold text-slate-900 text-base">3NF Relational Schema</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Normalized schema across 10 tables with strict foreign key constraints, indexes on search keys, and zero data redundancy.
            </p>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3 hover:border-slate-300 transition-all">
            <div className="w-11 h-11 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Lock size={22} />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Row-Level Locking</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Transactional <code className="text-indigo-600 font-semibold">SELECT ... FOR UPDATE</code> rechecks seat availability, preventing race conditions and double bookings.
            </p>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3 hover:border-slate-300 transition-all">
            <div className="w-11 h-11 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Cpu size={22} />
            </div>
            <h3 className="font-bold text-slate-900 text-base">C++ Mutex Engine</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              High-performance contiguous seat allocation heuristics compiled as a native shared library guarded by <code className="text-emerald-700 font-semibold">std::mutex</code>.
            </p>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3 hover:border-slate-300 transition-all">
            <div className="w-11 h-11 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <Ticket size={22} />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Instant E-Ticket PDFs</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Automated vector PDF reservation slips issued with unique PNRs, coach berth details, and downloadable electronic tickets.
            </p>
          </div>

        </div>
      </section>

    </div>
  );
};

export default Home;
