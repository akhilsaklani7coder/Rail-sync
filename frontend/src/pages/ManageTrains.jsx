import React, { useState, useEffect } from 'react';
import { Train, Plus, Check, X, AlertCircle, MapPin, Clock, Trash2, List } from 'lucide-react';
import api from '../api/axios';
import LoadingSpinner from '../components/LoadingSpinner';

const ManageTrains = () => {
  const [trains, setTrains] = useState([]);
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Form state
  const [trainNumber, setTrainNumber] = useState('');
  const [trainName, setTrainName] = useState('');
  const [trainType, setTrainType] = useState('SUPERFAST');
  const [sourceId, setSourceId] = useState('');
  const [destId, setDestId] = useState('');
  const [depTime, setDepTime] = useState('08:00');
  const [arrTime, setArrTime] = useState('14:00');
  const [fare, setFare] = useState(650);
  const [days, setDays] = useState('DAILY');

  // Stops Modal state
  const [stopsTrain, setStopsTrain] = useState(null);
  const [stopsList, setStopsList] = useState([]);
  const [loadingStops, setLoadingStops] = useState(false);
  const [newStopStationId, setNewStopStationId] = useState('');
  const [newStopSeq, setNewStopSeq] = useState(1);
  const [newStopArr, setNewStopArr] = useState('10:00');
  const [newStopDep, setNewStopDep] = useState('10:05');
  const [newStopDist, setNewStopDist] = useState(150);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [tRes, sRes] = await Promise.all([
        api.get('/admin/trains'),
        api.get('/trains/stations')
      ]);
      setTrains(tRes.data.trains || []);
      const stList = sRes.data.stations || [];
      setStations(stList);
      if (stList.length >= 2) {
        setSourceId(stList[0].id);
        setDestId(stList[1].id);
        setNewStopStationId(stList[0].id);
      }
    } catch (err) {
      setError('Failed to fetch train fleet.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggleActive = async (id) => {
    try {
      await api.delete(`/admin/trains/${id}`);
      await fetchData();
    } catch (err) {
      alert(err.message || 'Failed to update train status.');
    }
  };

  const handleCreateTrain = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      await api.post('/admin/trains', {
        train_number: trainNumber,
        train_name: trainName,
        train_type: trainType,
        source_station_id: Number(sourceId),
        destination_station_id: Number(destId),
        departure_time: `${depTime}:00`,
        arrival_time: `${arrTime}:00`,
        running_days: days,
        base_fare: Number(fare)
      });
      setShowAddModal(false);
      setTrainNumber('');
      setTrainName('');
      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to add train.');
    } finally {
      setSubmitting(false);
    }
  };

  // Stops modal helpers
  const handleOpenStops = async (train) => {
    setStopsTrain(train);
    setLoadingStops(true);
    try {
      const res = await api.get(`/admin/trains/${train.id}/stops`);
      setStopsList(res.data.stops || []);
      setNewStopSeq((res.data.stops?.length || 0) + 1);
    } catch (err) {
      alert("Failed to load stops.");
    } finally {
      setLoadingStops(false);
    }
  };

  const handleAddStop = async (e) => {
    e.preventDefault();
    if (!stopsTrain || !newStopStationId) return;

    try {
      await api.post(`/admin/trains/${stopsTrain.id}/stops`, {
        station_id: Number(newStopStationId),
        stop_sequence: Number(newStopSeq),
        arrival_time: `${newStopArr}:00`,
        departure_time: `${newStopDep}:00`,
        halt_minutes: 3,
        distance_from_origin_km: Number(newStopDist)
      });
      const res = await api.get(`/admin/trains/${stopsTrain.id}/stops`);
      setStopsList(res.data.stops || []);
      setNewStopSeq((res.data.stops?.length || 0) + 1);
    } catch (err) {
      alert(err.message || "Failed to add timetable stop.");
    }
  };

  const handleDeleteStop = async (stopId) => {
    if (!stopsTrain) return;
    try {
      await api.delete(`/admin/stops/${stopId}`);
      const res = await api.get(`/admin/trains/${stopsTrain.id}/stops`);
      setStopsList(res.data.stops || []);
    } catch (err) {
      alert("Failed to delete stop.");
    }
  };

  if (loading) return <LoadingSpinner text="Loading train fleet from database..." />;

  return (
    <div className="space-y-6">
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Train Fleet & Timetable Control</h2>
          <p className="text-xs text-slate-400">Configure express trains, categories, intermediate stops, and base fares.</p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="saffron-gradient text-white font-bold px-4 py-2 rounded-xl text-xs shadow flex items-center gap-1.5 cursor-pointer"
        >
          <Plus size={16} />
          <span>Add New Train</span>
        </button>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold flex items-center gap-2">
          <AlertCircle size={15} />
          <span>{error}</span>
        </div>
      )}

      {/* Trains Table */}
      <div className="bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
              <th className="py-3 px-4">Train #</th>
              <th className="py-3 px-4">Train Name</th>
              <th className="py-3 px-4">Category</th>
              <th className="py-3 px-4">Route</th>
              <th className="py-3 px-4">Timings</th>
              <th className="py-3 px-4">Base Fare</th>
              <th className="py-3 px-4">Stops</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-300">
            {trains.map((t) => (
              <tr key={t.id} className="hover:bg-slate-900/50">
                <td className="py-3 px-4 font-mono font-bold text-orange-400">#{t.train_number}</td>
                <td className="py-3 px-4 font-bold text-white">{t.train_name}</td>
                <td className="py-3 px-4">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-orange-300">
                    {t.train_type || 'EXPRESS'}
                  </span>
                </td>
                <td className="py-3 px-4 font-mono text-xs">{t.source_code} → {t.dest_code}</td>
                <td className="py-3 px-4">{t.departure_time} - {t.arrival_time}</td>
                <td className="py-3 px-4 font-bold text-emerald-400">₹{t.base_fare?.toFixed(2)}</td>
                <td className="py-3 px-4">
                  <button
                    onClick={() => handleOpenStops(t)}
                    className="text-orange-400 hover:text-orange-300 font-bold inline-flex items-center gap-1 hover:underline cursor-pointer"
                  >
                    <List size={13} /> {t.stop_count || 0} Stops
                  </button>
                </td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    t.is_active ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {t.is_active ? 'ACTIVE' : 'INACTIVE'}
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <button
                    onClick={() => handleToggleActive(t.id)}
                    className="text-[11px] font-bold px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                  >
                    {t.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add Train Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-lg w-full text-white shadow-2xl space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="font-bold text-base text-white">Add New Railway Train</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateTrain} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-400 font-bold uppercase">Train Number</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 12020"
                    value={trainNumber}
                    onChange={(e) => setTrainNumber(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-slate-400 font-bold uppercase">Train Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Garib Rath Express"
                    value={trainName}
                    onChange={(e) => setTrainName(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-slate-400 font-bold uppercase">Train Category</label>
                <select
                  value={trainType}
                  onChange={(e) => setTrainType(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                >
                  <option value="VANDE_BHARAT">Vande Bharat Express</option>
                  <option value="RAJDHANI">Rajdhani Express</option>
                  <option value="SHATABDI">Shatabdi Express</option>
                  <option value="SUPERFAST">Superfast Express</option>
                  <option value="EXPRESS">Express</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-400 font-bold uppercase">Origin Station</label>
                  <select
                    value={sourceId}
                    onChange={(e) => setSourceId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                  >
                    {stations.map(s => <option key={s.id} value={s.id}>{s.city} ({s.station_code})</option>)}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-slate-400 font-bold uppercase">Destination Station</label>
                  <select
                    value={destId}
                    onChange={(e) => setDestId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                  >
                    {stations.map(s => <option key={s.id} value={s.id} disabled={s.id === Number(sourceId)}>{s.city} ({s.station_code})</option>)}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-400 font-bold uppercase">Departure</label>
                  <input
                    type="time"
                    required
                    value={depTime}
                    onChange={(e) => setDepTime(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-slate-400 font-bold uppercase">Arrival</label>
                  <input
                    type="time"
                    required
                    value={arrTime}
                    onChange={(e) => setArrTime(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-slate-400 font-bold uppercase">Base Fare (₹)</label>
                  <input
                    type="number"
                    min="50"
                    required
                    value={fare}
                    onChange={(e) => setFare(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="saffron-gradient text-white font-bold px-5 py-2 rounded-xl shadow"
                >
                  {submitting ? 'Creating...' : 'Save Train'}
                </button>
              </div>

            </form>
          </div>
        </div>
      )}

      {/* Manage Stops Timetable Modal */}
      {stopsTrain && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-2xl w-full text-white shadow-2xl space-y-5 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <span className="font-mono text-xs font-bold text-orange-400">#{stopsTrain.train_number}</span>
                <h3 className="font-bold text-base text-white">{stopsTrain.train_name} • Timetable Stops</h3>
              </div>
              <button onClick={() => setStopsTrain(null)} className="text-slate-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            {loadingStops ? (
              <LoadingSpinner text="Retrieving timetable..." />
            ) : (
              <div className="space-y-4 text-xs">
                {stopsList.length > 0 ? (
                  <div className="rounded-2xl border border-slate-800 overflow-hidden">
                    <table className="w-full text-left">
                      <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                        <tr>
                          <th className="py-2.5 px-3">#</th>
                          <th className="py-2.5 px-3">Station</th>
                          <th className="py-2.5 px-3">Arr</th>
                          <th className="py-2.5 px-3">Dep</th>
                          <th className="py-2.5 px-3">Dist (km)</th>
                          <th className="py-2.5 px-3 text-right">Delete</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {stopsList.map((st) => (
                          <tr key={st.id} className="hover:bg-slate-800/40">
                            <td className="py-2 px-3 font-mono text-orange-400">{st.stop_sequence}</td>
                            <td className="py-2 px-3 font-bold">{st.station_name} ({st.station_code})</td>
                            <td className="py-2 px-3 font-mono">{st.arrival_time}</td>
                            <td className="py-2 px-3 font-mono">{st.departure_time}</td>
                            <td className="py-2 px-3 font-mono">{st.distance_from_origin_km}</td>
                            <td className="py-2 px-3 text-right">
                              <button
                                onClick={() => handleDeleteStop(st.id)}
                                className="text-rose-400 hover:text-rose-300 p-1"
                              >
                                <Trash2 size={14} />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-slate-400 text-center py-4">No intermediate stops recorded.</p>
                )}

                {/* Add Intermediate Stop Form */}
                <form onSubmit={handleAddStop} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                  <h4 className="font-bold text-white text-xs">Add Intermediate Timetable Stop</h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    <div>
                      <label className="text-[10px] text-slate-400 block uppercase font-bold">Station</label>
                      <select
                        value={newStopStationId}
                        onChange={(e) => setNewStopStationId(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white"
                      >
                        {stations.map(s => <option key={s.id} value={s.id}>{s.station_code}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="text-[10px] text-slate-400 block uppercase font-bold">Sequence</label>
                      <input
                        type="number"
                        min="1"
                        value={newStopSeq}
                        onChange={(e) => setNewStopSeq(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] text-slate-400 block uppercase font-bold">Arr Time</label>
                      <input
                        type="time"
                        value={newStopArr}
                        onChange={(e) => setNewStopArr(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] text-slate-400 block uppercase font-bold">Dep Time</label>
                      <input
                        type="time"
                        value={newStopDep}
                        onChange={(e) => setNewStopDep(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="w-full saffron-gradient text-white font-bold py-2 rounded-xl text-xs"
                  >
                    Add Timetable Stop
                  </button>
                </form>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
};

export default ManageTrains;
