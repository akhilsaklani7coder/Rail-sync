import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  Search, MapPin, Calendar, Train, AlertCircle, ArrowLeftRight, 
  Route, ArrowRight, Clock, SlidersHorizontal, CheckCircle2, Cpu,
  RefreshCw, Armchair, X, CheckSquare, Square, Eye, Sparkles, Filter
} from 'lucide-react';
import api from '../api/axios';
import TrainCard from '../components/TrainCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { useToast } from '../context/ToastContext';

const SearchTrains = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [stations, setStations] = useState([]);
  const [sourceId, setSourceId] = useState(searchParams.get('source_id') || '');
  const [destId, setDestId] = useState(searchParams.get('dest_id') || '');
  const [journeyDate, setJourneyDate] = useState(() => {
    return searchParams.get('date') || (() => {
      const d = new Date();
      d.setDate(d.getDate() + 1);
      return d.toISOString().split('T')[0];
    })();
  });

  const [trains, setTrains] = useState([]);
  const [dijkstraPath, setDijkstraPath] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('DEPARTURE'); // 'DEPARTURE', 'DEPARTURE_DESC', 'ARRIVAL', 'DURATION', 'FARE', 'FARE_DESC'

  // Faceted Filters & Quick Search State
  const [trainSearchKeyword, setTrainSearchKeyword] = useState('');
  const [selectedSlot, setSelectedSlot] = useState('ALL'); // 'ALL', 'early_morning', 'morning', 'midday', 'night'
  const [selectedArrivalSlot, setSelectedArrivalSlot] = useState('ALL');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedClassFilter, setSelectedClassFilter] = useState('ALL');
  const [maxFareLimit, setMaxFareLimit] = useState(3500);
  const [onlyAvailable, setOnlyAvailable] = useState(false);

  // Train Comparison Modal State
  const [comparedTrainIds, setComparedTrainIds] = useState([]);
  const [showCompareModal, setShowCompareModal] = useState(false);

  // Timetable / Intermediate Stops Modal State
  const [timetableTrain, setTimetableTrain] = useState(null);
  const [timetableStops, setTimetableStops] = useState([]);
  const [loadingStops, setLoadingStops] = useState(false);

  const [loadingStations, setLoadingStations] = useState(true);
  const minDate = new Date().toISOString().split('T')[0];
  const isSameStation = sourceId && destId && Number(sourceId) === Number(destId);

  // Fetch stations for dropdowns with retry support
  const fetchStations = useCallback(async () => {
    setLoadingStations(true);
    try {
      const res = await api.get('/trains/stations');
      const list = res.data.stations || [];
      setStations(list);
      if (!sourceId && list.length >= 2) {
        setSourceId(list[0].id);
        setDestId(list[1].id);
      }
    } catch (err) {
      console.error("Failed to load stations", err);
      showToast("Failed to load stations from database.", "error");
    } finally {
      setLoadingStations(false);
    }
  }, [showToast, sourceId]);

  useEffect(() => {
    fetchStations();
  }, [fetchStations]);

  // Trigger search if params are present in URL
  useEffect(() => {
    const sId = searchParams.get('source_id');
    const dId = searchParams.get('dest_id');
    const dt = searchParams.get('date');
    if (sId && dId && Number(sId) !== Number(dId)) {
      setSourceId(sId);
      setDestId(dId);
      if (dt) setJourneyDate(dt);
      executeSearch(sId, dId, dt || journeyDate);
    }
  }, [searchParams]);

  const executeSearch = async (sId, dId, dt) => {
    if (Number(sId) === Number(dId)) {
      setError("Origin and destination cannot be the same station.");
      return;
    }
    setLoading(true);
    setError('');
    setSearched(true);
    setDijkstraPath(null);

    try {
      const res = await api.get(`/trains/search?source_id=${sId}&dest_id=${dId}&date=${dt}`);
      setTrains(res.data.trains || []);
      setDijkstraPath(res.data.dijkstra_path || null);
    } catch (err) {
      setError(err.message || 'Error searching trains.');
      setTrains([]);
      showToast(err.message || "Failed to retrieve train schedules", "error");
    } finally {
      setLoading(false);
    }
  };

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
    if (isSameStation) {
      showToast("Origin and destination cannot be identical.", "error");
      return;
    }
    setSearchParams({ source_id: sourceId, dest_id: destId, date: journeyDate });
    executeSearch(sourceId, destId, journeyDate);
  };

  // Timetable Viewer
  const handleOpenTimetable = async (train) => {
    setTimetableTrain(train);
    setLoadingStops(true);
    setTimetableStops([]);
    try {
      const res = await api.get(`/trains/${train.id}/stops`);
      setTimetableStops(res.data.stops || []);
    } catch (err) {
      showToast("Failed to load intermediate stops.", "error");
    } finally {
      setLoadingStops(false);
    }
  };

  // Compare Handler
  const handleToggleCompare = (trainId) => {
    if (comparedTrainIds.includes(trainId)) {
      setComparedTrainIds(prev => prev.filter(id => id !== trainId));
    } else {
      if (comparedTrainIds.length >= 3) {
        showToast("You can compare up to 3 trains simultaneously.", "warning");
        return;
      }
      setComparedTrainIds(prev => [...prev, trainId]);
    }
  };

  // Filtered & Sorted Trains
  const processedTrains = useMemo(() => {
    return trains.filter(t => {
      // 0. Keyword filter
      if (trainSearchKeyword.trim()) {
        const kw = trainSearchKeyword.toLowerCase();
        if (!t.train_number.toLowerCase().includes(kw) && !t.train_name.toLowerCase().includes(kw)) {
          return false;
        }
      }

      // 1. Departure slot filter
      if (selectedSlot !== 'ALL') {
        const hour = parseInt(t.departure_time.split(':')[0], 10);
        if (selectedSlot === 'early_morning' && !(hour >= 0 && hour < 6)) return false;
        if (selectedSlot === 'morning' && !(hour >= 6 && hour < 12)) return false;
        if (selectedSlot === 'midday' && !(hour >= 12 && hour < 18)) return false;
        if (selectedSlot === 'night' && !(hour >= 18 && hour < 24)) return false;
      }

      // 2. Arrival slot filter
      if (selectedArrivalSlot !== 'ALL') {
        const hour = parseInt(t.arrival_time.split(':')[0], 10);
        if (selectedArrivalSlot === 'early_morning' && !(hour >= 0 && hour < 6)) return false;
        if (selectedArrivalSlot === 'morning' && !(hour >= 6 && hour < 12)) return false;
        if (selectedArrivalSlot === 'midday' && !(hour >= 12 && hour < 18)) return false;
        if (selectedArrivalSlot === 'night' && !(hour >= 18 && hour < 24)) return false;
      }

      // 3. Train category filter
      if (selectedCategory !== 'ALL' && t.train_type !== selectedCategory) {
        return false;
      }

      // 4. Class filter
      if (selectedClassFilter !== 'ALL') {
        const hasClass = (t.classes || []).some(c => c.coach_type === selectedClassFilter);
        if (!hasClass) return false;
      }

      // 5. Availability filter
      if (onlyAvailable && t.total_available_seats <= 0) {
        return false;
      }

      // 6. Max fare filter
      if (maxFareLimit < 3500) {
        const minTrainFare = Math.min(...(t.classes || []).map(c => c.fare), t.base_fare);
        if (minTrainFare > maxFareLimit) return false;
      }

      return true;
    }).sort((a, b) => {
      if (sortBy === 'FARE') {
        return a.base_fare - b.base_fare;
      } else if (sortBy === 'FARE_DESC') {
        return b.base_fare - a.base_fare;
      } else if (sortBy === 'DURATION') {
        const durA = parseInt(a.duration) || 0;
        const durB = parseInt(b.duration) || 0;
        return durA - durB;
      } else if (sortBy === 'ARRIVAL') {
        return a.arrival_time.localeCompare(b.arrival_time);
      } else if (sortBy === 'DEPARTURE_DESC') {
        return b.departure_time.localeCompare(a.departure_time);
      }
      return a.departure_time.localeCompare(b.departure_time);
    });
  }, [trains, trainSearchKeyword, selectedSlot, selectedArrivalSlot, selectedCategory, selectedClassFilter, onlyAvailable, maxFareLimit, sortBy]);

  const comparedTrainsList = useMemo(() => {
    return trains.filter(t => comparedTrainIds.includes(t.id));
  }, [trains, comparedTrainIds]);

  const selectedSource = stations.find(s => s.id === Number(sourceId));
  const selectedDest = stations.find(s => s.id === Number(destId));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Search Modifier Bar */}
      <div className="bg-slate-950 text-white rounded-3xl p-6 sm:p-8 shadow-xl border border-slate-800 relative overflow-hidden">
        <div className="relative z-10">
          <div className="mb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-orange-400">
                Indian Railway Portal • Search Services
              </span>
              <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight mt-1">
                Find & Reserve Train Tickets
              </h1>
            </div>

            {/* Quick Train # or Name Search Input */}
            <div className="relative min-w-[280px]">
              <input
                type="text"
                placeholder="Search train name or # (e.g. 12017, Duronto)..."
                value={trainSearchKeyword}
                onChange={(e) => setTrainSearchKeyword(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-2xl pl-10 pr-9 py-2.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/50 font-medium"
              />
              <Search size={16} className="absolute left-3.5 top-3 text-slate-400" />
              {trainSearchKeyword && (
                <button
                  type="button"
                  onClick={() => setTrainSearchKeyword('')}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-white cursor-pointer"
                >
                  <X size={14} />
                </button>
              )}
            </div>
          </div>

          <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 md:grid-cols-12 gap-3 items-end">
            
            {/* Origin Station */}
            <div className="md:col-span-4 space-y-1">
              <label className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                <MapPin size={12} className="text-orange-400" />
                From Station
              </label>
              <select
                value={sourceId}
                onChange={(e) => setSourceId(e.target.value)}
                disabled={loadingStations}
                className="w-full bg-slate-900 border border-slate-700 rounded-2xl px-4 py-3 text-sm font-semibold text-white focus:outline-none focus:ring-2 focus:ring-orange-500/50"
              >
                {stations.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.station_name} ({s.station_code}) - {s.city}
                  </option>
                ))}
              </select>
            </div>

            {/* Swap Button */}
            <div className="hidden md:flex md:col-span-1 justify-center pb-2">
              <button
                type="button"
                onClick={handleSwapStations}
                className="w-10 h-10 rounded-full bg-slate-800 hover:bg-orange-600 text-white flex items-center justify-center transition-all cursor-pointer active:scale-90 border border-slate-700"
                title="Swap origin and destination stations"
              >
                <ArrowLeftRight size={16} />
              </button>
            </div>

            {/* Destination Station */}
            <div className="md:col-span-4 space-y-1">
              <label className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                <MapPin size={12} className="text-orange-400" />
                To Station
              </label>
              <select
                value={destId}
                onChange={(e) => setDestId(e.target.value)}
                disabled={loadingStations}
                className="w-full bg-slate-900 border border-slate-700 rounded-2xl px-4 py-3 text-sm font-semibold text-white focus:outline-none focus:ring-2 focus:ring-orange-500/50"
              >
                {stations.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.station_name} ({s.station_code}) - {s.city}
                  </option>
                ))}
              </select>
            </div>

            {/* Date */}
            <div className="md:col-span-2 space-y-1">
              <label className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                <Calendar size={12} className="text-orange-400" />
                Journey Date
              </label>
              <input
                type="date"
                min={minDate}
                value={journeyDate}
                onChange={(e) => setJourneyDate(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-2xl px-4 py-3 text-sm font-semibold text-white focus:outline-none focus:ring-2 focus:ring-orange-500/50"
              />
            </div>

            {/* Submit */}
            <div className="md:col-span-1 pb-0.5">
              <button
                type="submit"
                disabled={loading || isSameStation}
                className="w-full saffron-gradient hover:brightness-110 text-white font-bold p-3 rounded-2xl shadow-lg transition-all flex items-center justify-center cursor-pointer active:scale-95 disabled:opacity-50"
                title="Search Trains"
              >
                <Search size={20} />
              </button>
            </div>
          </form>

          {isSameStation && (
            <p className="text-xs text-rose-400 font-semibold mt-3">
              Origin and destination cannot be identical.
            </p>
          )}
        </div>
      </div>

      {/* C++ Dijkstra Optimal Path Banner */}
      {dijkstraPath && dijkstraPath.path && (
        <div className="bg-gradient-to-r from-indigo-950 via-slate-900 to-indigo-950 text-white rounded-3xl p-6 border border-indigo-800 shadow-md">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-orange-500/20 text-orange-400 border border-orange-500/30">
                <Cpu size={18} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">C++17 Dijkstra Shortest-Path Topology</h3>
                <p className="text-xs text-slate-300">
                  Optimal corridor: <b className="text-orange-400">{dijkstraPath.total_distance_km} km</b> physical rail distance across {dijkstraPath.hops} network hops.
                </p>
              </div>
            </div>
            <span className="text-xs font-mono px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30 self-start sm:self-auto">
              Engine: {dijkstraPath.engine || 'C++17 Min-Heap Priority Queue'}
            </span>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
            {dijkstraPath.path.map((st, i) => (
              <React.Fragment key={st.id || i}>
                <div className="shrink-0 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs font-bold text-white">
                  {st.station_name} <span className="font-mono text-orange-400">({st.station_code})</span>
                </div>
                {i < dijkstraPath.path.length - 1 && (
                  <ArrowRight size={14} className="text-orange-400 shrink-0" />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

      {/* Main Content Area: Faceted Filters + Results */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Faceted Filter Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-black text-slate-900 text-sm flex items-center gap-2">
                <SlidersHorizontal size={16} className="text-orange-500" />
                Filter Journeys
              </h3>
              {(selectedSlot !== 'ALL' || selectedArrivalSlot !== 'ALL' || selectedCategory !== 'ALL' || selectedClassFilter !== 'ALL' || onlyAvailable || maxFareLimit < 3500 || trainSearchKeyword) && (
                <button
                  type="button"
                  onClick={() => {
                    setSelectedSlot('ALL');
                    setSelectedArrivalSlot('ALL');
                    setSelectedCategory('ALL');
                    setSelectedClassFilter('ALL');
                    setOnlyAvailable(false);
                    setMaxFareLimit(3500);
                    setTrainSearchKeyword('');
                  }}
                  className="text-[11px] font-bold text-orange-600 hover:underline cursor-pointer"
                >
                  Reset All
                </button>
              )}
            </div>

            {/* Departure Time Slots */}
            <div className="space-y-2">
              <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                Departure Time
              </label>
              <div className="space-y-1.5 text-xs">
                {[
                  { id: 'ALL', label: 'Any Departure Time' },
                  { id: 'early_morning', label: 'Early Morning (00:00 - 06:00)' },
                  { id: 'morning', label: 'Morning (06:00 - 12:00)' },
                  { id: 'midday', label: 'Mid-day (12:00 - 18:00)' },
                  { id: 'night', label: 'Night (18:00 - 24:00)' }
                ].map(slot => (
                  <label key={slot.id} className="flex items-center gap-2.5 p-2 rounded-xl hover:bg-slate-50 cursor-pointer">
                    <input
                      type="radio"
                      name="slot"
                      checked={selectedSlot === slot.id}
                      onChange={() => setSelectedSlot(slot.id)}
                      className="text-orange-500 focus:ring-orange-400"
                    />
                    <span className={selectedSlot === slot.id ? 'font-bold text-slate-900' : 'text-slate-600'}>
                      {slot.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Arrival Time Slots */}
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                Arrival Time
              </label>
              <div className="space-y-1.5 text-xs">
                {[
                  { id: 'ALL', label: 'Any Arrival Time' },
                  { id: 'early_morning', label: 'Early Morning (00:00 - 06:00)' },
                  { id: 'morning', label: 'Morning (06:00 - 12:00)' },
                  { id: 'midday', label: 'Mid-day (12:00 - 18:00)' },
                  { id: 'night', label: 'Night (18:00 - 24:00)' }
                ].map(slot => (
                  <label key={slot.id} className="flex items-center gap-2.5 p-2 rounded-xl hover:bg-slate-50 cursor-pointer">
                    <input
                      type="radio"
                      name="arrivalSlot"
                      checked={selectedArrivalSlot === slot.id}
                      onChange={() => setSelectedArrivalSlot(slot.id)}
                      className="text-orange-500 focus:ring-orange-400"
                    />
                    <span className={selectedArrivalSlot === slot.id ? 'font-bold text-slate-900' : 'text-slate-600'}>
                      {slot.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Train Category */}
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                Train Category
              </label>
              <div className="space-y-1.5 text-xs">
                {[
                  { id: 'ALL', label: 'All Train Categories' },
                  { id: 'VANDE_BHARAT', label: 'Vande Bharat Express' },
                  { id: 'RAJDHANI', label: 'Rajdhani Express' },
                  { id: 'SHATABDI', label: 'Shatabdi Express' },
                  { id: 'DURONTO', label: 'Duronto Express' },
                  { id: 'GARIB_RATH', label: 'Garib Rath Express' },
                  { id: 'SUPERFAST', label: 'Superfast Trains' },
                  { id: 'MAIL_EXPRESS', label: 'Mail / Express' },
                  { id: 'INTERCITY', label: 'Intercity Express' },
                  { id: 'EXPRESS', label: 'Express' }
                ].map(cat => (
                  <label key={cat.id} className="flex items-center gap-2.5 p-2 rounded-xl hover:bg-slate-50 cursor-pointer">
                    <input
                      type="radio"
                      name="category"
                      checked={selectedCategory === cat.id}
                      onChange={() => setSelectedCategory(cat.id)}
                      className="text-orange-500 focus:ring-orange-400"
                    />
                    <span className={selectedCategory === cat.id ? 'font-bold text-slate-900' : 'text-slate-600'}>
                      {cat.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Travel Class */}
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                Travel Class
              </label>
              <div className="grid grid-cols-3 gap-1.5 text-xs">
                {['ALL', '1A', '2A', '3A', 'CC', 'SL'].map(cls => (
                  <button
                    key={cls}
                    type="button"
                    onClick={() => setSelectedClassFilter(cls)}
                    className={`py-2 rounded-xl font-bold border transition-all cursor-pointer ${
                      selectedClassFilter === cls 
                        ? 'bg-slate-900 text-white border-slate-900 shadow-xs' 
                        : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {cls}
                  </button>
                ))}
              </div>
            </div>

            {/* Max Fare Range Slider */}
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <div className="flex justify-between items-center text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <span>Max Fare</span>
                <span className="text-orange-600 font-mono font-bold">₹{maxFareLimit}</span>
              </div>
              <input
                type="range"
                min="200"
                max="3500"
                step="50"
                value={maxFareLimit}
                onChange={(e) => setMaxFareLimit(Number(e.target.value))}
                className="w-full accent-orange-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>₹200</span>
                <span>₹3500+</span>
              </div>
            </div>

            {/* Availability Only Toggle */}
            <div className="pt-2 border-t border-slate-100">
              <label className="flex items-center gap-2.5 p-2 rounded-xl hover:bg-slate-50 cursor-pointer text-xs">
                <input
                  type="checkbox"
                  checked={onlyAvailable}
                  onChange={(e) => setOnlyAvailable(e.target.checked)}
                  className="w-4 h-4 text-orange-500 rounded focus:ring-orange-400"
                />
                <span className="font-bold text-slate-800">Only Available Trains</span>
              </label>
            </div>

          </div>

          {/* Floating Compare CTA Bar if trains selected */}
          {comparedTrainIds.length > 0 && (
            <div className="bg-orange-500 text-white rounded-3xl p-5 shadow-lg space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider">Comparison Queue</span>
                <span className="px-2 py-0.5 rounded-full bg-white/20 text-xs font-extrabold">{comparedTrainIds.length}/3</span>
              </div>
              <p className="text-xs text-orange-100">
                Compare timings, class fares, and seat availability side-by-side.
              </p>
              <button
                type="button"
                onClick={() => setShowCompareModal(true)}
                className="w-full bg-white text-orange-600 hover:bg-orange-50 font-bold py-2.5 rounded-xl text-xs shadow transition-all cursor-pointer"
              >
                Launch Train Comparison
              </button>
            </div>
          )}
        </div>

        {/* Results Stream */}
        <div className="lg:col-span-3 space-y-5">
          
          {/* Results Header with Sorting */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 sm:px-6 rounded-2xl border border-slate-200/90 shadow-xs">
            <div>
              <span className="text-xs text-slate-500">
                Found <b className="text-slate-900">{processedTrains.length}</b> trains matching your criteria
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Sort:</span>
              <div className="inline-flex rounded-xl bg-slate-100 p-1 text-xs">
                <button
                  type="button"
                  onClick={() => setSortBy(sortBy === 'DEPARTURE' ? 'DEPARTURE_DESC' : 'DEPARTURE')}
                  className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                    sortBy.startsWith('DEPARTURE') ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Departure {sortBy === 'DEPARTURE_DESC' ? '↓' : '↑'}
                </button>
                <button
                  type="button"
                  onClick={() => setSortBy('ARRIVAL')}
                  className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                    sortBy === 'ARRIVAL' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Arrival
                </button>
                <button
                  type="button"
                  onClick={() => setSortBy('DURATION')}
                  className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                    sortBy === 'DURATION' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Duration
                </button>
                <button
                  type="button"
                  onClick={() => setSortBy(sortBy === 'FARE' ? 'FARE_DESC' : 'FARE')}
                  className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                    sortBy.startsWith('FARE') ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Price {sortBy === 'FARE_DESC' ? '↓' : '↑'}
                </button>
              </div>
            </div>
          </div>

          {/* Cards Stream */}
          {loading ? (
            <div className="py-16">
              <LoadingSpinner text="Searching active railway database and checking live availability..." />
            </div>
          ) : processedTrains.length === 0 ? (
            <div className="bg-white rounded-3xl p-12 text-center border border-slate-200/90 shadow-sm space-y-3">
              <div className="w-14 h-14 rounded-2xl bg-orange-50 text-orange-500 mx-auto flex items-center justify-center">
                <Train size={28} />
              </div>
              <h3 className="font-bold text-slate-900 text-base">No trains found</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                No active trains matched your selected route, date, and filters. Try adjusting your departure slot or selecting all categories.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {processedTrains.map(t => (
                <TrainCard
                  key={t.id}
                  train={t}
                  journeyDate={journeyDate}
                  onToggleCompare={handleToggleCompare}
                  isCompared={comparedTrainIds.includes(t.id)}
                  onViewTimetable={handleOpenTimetable}
                />
              ))}
            </div>
          )}

        </div>

      </div>

      {/* Train Comparison Modal */}
      {showCompareModal && (
        <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-4xl w-full shadow-2xl max-h-[90vh] overflow-y-auto space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-lg font-black text-slate-900">Side-by-Side Train Comparison</h3>
                <p className="text-xs text-slate-500">Comparing timings, travel duration, fares, and class capacities</p>
              </div>
              <button
                type="button"
                onClick={() => setShowCompareModal(false)}
                className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X size={20} />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {comparedTrainsList.map(t => (
                <div key={t.id} className="p-5 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-4">
                  <div>
                    <span className="font-mono text-xs font-bold text-orange-600">#{t.train_number}</span>
                    <h4 className="font-black text-slate-900 text-base">{t.train_name}</h4>
                    <span className="text-[10px] uppercase font-bold text-slate-500">{t.train_type || 'EXPRESS'}</span>
                  </div>

                  <div className="space-y-1 text-xs border-t border-slate-200 pt-3">
                    <div className="flex justify-between text-slate-600">
                      <span>Departure:</span>
                      <strong className="text-slate-900">{t.departure_time} ({t.source_station_code})</strong>
                    </div>
                    <div className="flex justify-between text-slate-600">
                      <span>Arrival:</span>
                      <strong className="text-slate-900">{t.arrival_time} ({t.destination_station_code})</strong>
                    </div>
                    <div className="flex justify-between text-slate-600">
                      <span>Duration:</span>
                      <strong className="text-slate-900">{t.duration}</strong>
                    </div>
                    <div className="flex justify-between text-slate-600">
                      <span>Distance:</span>
                      <strong className="text-slate-900">{t.distance_km} km</strong>
                    </div>
                  </div>

                  <div className="border-t border-slate-200 pt-3 space-y-2">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Class Fares:</span>
                    <div className="space-y-1 text-xs">
                      {(t.classes || []).map((c, i) => (
                        <div key={i} className="flex justify-between items-center">
                          <span className="font-bold text-slate-700">{c.coach_type}</span>
                          <span className="font-mono font-bold text-slate-900">₹{Math.round(c.fare)} ({c.status_label || `${c.available} AVL`})</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setShowCompareModal(false);
                      navigate(`/passenger-details`, {
                        state: {
                          train: t,
                          journeyDate,
                          travelClass: (t.classes && t.classes[0]?.coach_type) || 'CC',
                          passengerCount: 1,
                          autoAllocation: true
                        }
                      });
                    }}
                    className="w-full saffron-gradient text-white font-bold py-2.5 rounded-xl text-xs shadow-md transition-all"
                  >
                    Select & Book This Train
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Intermediate Stops Timetable Modal */}
      {timetableTrain && (
        <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-2xl w-full shadow-2xl max-h-[85vh] overflow-y-auto space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <span className="font-mono text-xs font-bold text-orange-600">#{timetableTrain.train_number}</span>
                <h3 className="text-lg font-black text-slate-900">{timetableTrain.train_name} • Route Timetable</h3>
                <p className="text-xs text-slate-500">
                  {timetableTrain.source_station_name} → {timetableTrain.destination_station_name}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setTimetableTrain(null)}
                className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X size={20} />
              </button>
            </div>

            {loadingStops ? (
              <LoadingSpinner text="Retrieving intermediate stops timetable..." />
            ) : timetableStops.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500">
                No intermediate stops registered for this train in timetable. Direct express service.
              </div>
            ) : (
              <div className="overflow-x-auto rounded-2xl border border-slate-200">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px]">
                    <tr>
                      <th className="py-3 px-4">#</th>
                      <th className="py-3 px-4">Station</th>
                      <th className="py-3 px-4">Arr</th>
                      <th className="py-3 px-4">Dep</th>
                      <th className="py-3 px-4">Halt</th>
                      <th className="py-3 px-4 text-right">Distance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {timetableStops.map((st, i) => (
                      <tr key={i} className="hover:bg-slate-50/50">
                        <td className="py-2.5 px-4 font-mono font-bold text-slate-400">{st.stop_sequence}</td>
                        <td className="py-2.5 px-4">
                          <span className="font-bold text-slate-900">{st.station_name}</span>{' '}
                          <span className="font-mono text-orange-600 font-semibold">({st.station_code})</span>
                        </td>
                        <td className="py-2.5 px-4 font-mono text-slate-700">{st.arrival_time}</td>
                        <td className="py-2.5 px-4 font-mono text-slate-700">{st.departure_time}</td>
                        <td className="py-2.5 px-4 text-slate-600">{st.halt_minutes} min</td>
                        <td className="py-2.5 px-4 text-right font-mono text-slate-500">{st.distance_from_origin_km} km</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
};

export default SearchTrains;
