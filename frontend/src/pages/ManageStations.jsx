import React, { useState, useEffect } from 'react';
import { MapPin, Plus, AlertCircle } from 'lucide-react';
import api from '../api/axios';
import LoadingSpinner from '../components/LoadingSpinner';

const ManageStations = () => {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stationCode, setStationCode] = useState('');
  const [stationName, setStationName] = useState('');
  const [city, setCity] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchStations = async () => {
    setLoading(true);
    try {
      const res = await api.get('/admin/stations');
      setStations(res.data.stations || []);
    } catch (err) {
      setError('Failed to fetch station directory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStations();
  }, []);

  const handleToggleStation = async (id) => {
    setError('');
    setSuccess('');
    try {
      await api.delete(`/admin/stations/${id}`);
      await fetchStations();
    } catch (err) {
      setError(err.message || 'Failed to toggle station status.');
    }
  };

  const handleAddStation = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      await api.post('/admin/stations', {
        station_code: stationCode,
        station_name: stationName,
        city
      });
      setSuccess(`Station ${stationCode} created successfully!`);
      setStationCode('');
      setStationName('');
      setCity('');
      await fetchStations();
    } catch (err) {
      setError(err.message || 'Failed to add station.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner text="Retrieving railway stations from database..." />;

  return (
    <div className="space-y-6">
      
      <div>
        <h2 className="text-xl font-bold text-white">Railway Stations Network</h2>
        <p className="text-xs text-slate-400">View and add railway hubs across the national rail network.</p>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold flex items-center gap-2">
          <AlertCircle size={15} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
          {success}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Add Station Form */}
        <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
          <h3 className="font-bold text-sm text-white flex items-center gap-2">
            <Plus size={16} className="text-orange-500" />
            <span>Add New Station</span>
          </h3>

          <form onSubmit={handleAddStation} className="space-y-3 text-xs">
            <div className="space-y-1">
              <label className="text-slate-400 font-bold uppercase">Station Code (Unique)</label>
              <input
                type="text"
                required
                maxLength={8}
                placeholder="e.g. CNB"
                value={stationCode}
                onChange={(e) => setStationCode(e.target.value.toUpperCase())}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono uppercase"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-bold uppercase">Station Name</label>
              <input
                type="text"
                required
                placeholder="e.g. Kanpur Central"
                value={stationName}
                onChange={(e) => setStationName(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-bold uppercase">City</label>
              <input
                type="text"
                required
                placeholder="e.g. Kanpur"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full saffron-gradient text-white font-bold py-2.5 rounded-xl text-xs shadow mt-2 cursor-pointer disabled:opacity-50"
            >
              {submitting ? 'Saving...' : 'Add Station'}
            </button>
          </form>
        </div>

        {/* Stations Table */}
        <div className="lg:col-span-2 bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                <th className="py-3 px-4">Code</th>
                <th className="py-3 px-4">Station Name</th>
                <th className="py-3 px-4">City</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {stations.map((s) => (
                <tr key={s.id} className="hover:bg-slate-900/50">
                  <td className="py-3 px-4 font-mono font-bold text-orange-400">{s.station_code}</td>
                  <td className="py-3 px-4 font-bold text-white">{s.station_name}</td>
                  <td className="py-3 px-4 text-slate-400">{s.city}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      s.is_active ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {s.is_active ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => handleToggleStation(s.id)}
                      className="text-[11px] font-bold px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer"
                    >
                      {s.is_active ? 'Deactivate' : 'Activate'}
                    </button>
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

export default ManageStations;
