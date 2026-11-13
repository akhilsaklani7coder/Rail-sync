import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  User, Mail, Phone, MapPin, Calendar, Shield, Ticket, 
  CheckCircle, XCircle, CreditCard, Save, Edit3, ArrowRight, Sparkles
} from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import LoadingSpinner from '../components/LoadingSpinner';

const Profile = () => {
  const { user, setUser } = useAuth();
  const { addToast } = useToast();
  
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    address: ''
  });

  useEffect(() => {
    fetchProfileAndStats();
  }, []);

  const fetchProfileAndStats = async () => {
    try {
      setLoading(true);
      const [profileRes, statsRes] = await Promise.all([
        api.get('/auth/profile'),
        api.get('/auth/stats')
      ]);

      const prof = profileRes.data.profile;
      setProfile(prof);
      setFormData({
        full_name: prof.full_name || '',
        phone: prof.phone || '',
        address: prof.address || ''
      });
      setStats(statsRes.data.stats);
    } catch (err) {
      addToast(err.response?.data?.error || 'Failed to load profile details.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    if (!formData.full_name.trim()) {
      addToast('Full name is required.', 'error');
      return;
    }

    try {
      setSaving(true);
      const res = await api.put('/auth/profile', formData);
      setProfile(res.data.profile);
      if (setUser) {
        setUser(prev => ({
          ...prev,
          full_name: res.data.profile.full_name,
          phone: res.data.profile.phone,
          address: res.data.profile.address
        }));
      }
      setIsEditing(false);
      addToast('Profile updated successfully!', 'success');
    } catch (err) {
      addToast(err.response?.data?.error || 'Failed to update profile.', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <LoadingSpinner text="Loading your account profile..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Header Hero Banner */}
        <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
          <div className="absolute right-0 top-0 translate-x-10 -translate-y-10 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl pointer-events-none" />
          
          <div className="relative flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="flex items-center gap-5">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center text-3xl font-black text-white shadow-lg shadow-orange-500/20">
                {profile?.full_name ? profile.full_name[0].toUpperCase() : 'U'}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
                    {profile?.full_name}
                  </h1>
                  <span className="px-3 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    {profile?.role === 'ADMIN' ? 'Administrator' : 'Verified Passenger'}
                  </span>
                </div>
                <p className="text-slate-300 text-sm mt-1 flex items-center gap-2">
                  <Mail className="w-4 h-4 text-orange-400" /> {profile?.email}
                </p>
                <p className="text-slate-400 text-xs mt-1 flex items-center gap-2">
                  <Calendar className="w-3.5 h-3.5 text-slate-400" /> Member since {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Link
                to="/my-bookings"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-orange-500 hover:bg-orange-600 text-white text-sm font-semibold transition-all shadow-md shadow-orange-500/20"
              >
                <Ticket className="w-4 h-4" /> My Bookings
              </Link>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Bookings</span>
              <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-600">
                <Ticket className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-black text-slate-800 mt-2">{stats?.total_bookings || 0}</p>
            <p className="text-xs text-slate-400 mt-1">All reservation attempts</p>
          </div>

          <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Confirmed</span>
              <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-600">
                <CheckCircle className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-black text-emerald-600 mt-2">{stats?.confirmed_bookings || 0}</p>
            <p className="text-xs text-slate-400 mt-1">Active confirmed journeys</p>
          </div>

          <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Cancelled</span>
              <div className="p-2.5 rounded-xl bg-rose-50 text-rose-600">
                <XCircle className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-black text-rose-600 mt-2">{stats?.cancelled_bookings || 0}</p>
            <p className="text-xs text-slate-400 mt-1">Refunded reservations</p>
          </div>

          <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Travel Fare</span>
              <div className="p-2.5 rounded-xl bg-amber-50 text-amber-600">
                <CreditCard className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-black text-slate-800 mt-2">₹{(stats?.total_spent || 0).toLocaleString()}</p>
            <p className="text-xs text-slate-400 mt-1">Confirmed journey expenditure</p>
          </div>
        </div>

        {/* Profile Details & Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Profile Form */}
          <div className="lg:col-span-2 bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 pb-5 mb-6">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Personal Information</h2>
                <p className="text-xs text-slate-500 mt-0.5">Manage your personal contact details for ticket notifications</p>
              </div>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  isEditing 
                    ? 'bg-slate-100 text-slate-700 hover:bg-slate-200' 
                    : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100'
                }`}
              >
                <Edit3 className="w-3.5 h-3.5" />
                {isEditing ? 'Cancel Edit' : 'Edit Profile'}
              </button>
            </div>

            <form onSubmit={handleSaveProfile} className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                    Full Legal Name
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50/50 text-slate-800 text-sm focus:bg-white focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all disabled:opacity-75 disabled:cursor-not-allowed"
                      placeholder="e.g. Rahul Sharma"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                    Email Address <span className="text-slate-400 font-normal lowercase">(Read-only)</span>
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="email"
                      value={profile?.email || ''}
                      disabled
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-100 text-slate-500 text-sm cursor-not-allowed"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                    Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50/50 text-slate-800 text-sm focus:bg-white focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all disabled:opacity-75 disabled:cursor-not-allowed"
                      placeholder="+91 98765 43210"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                    Account Role
                  </label>
                  <div className="relative">
                    <Shield className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      value={profile?.role || 'USER'}
                      disabled
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-100 text-slate-500 text-sm cursor-not-allowed"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                  Residential Address
                </label>
                <div className="relative">
                  <MapPin className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                  <textarea
                    name="address"
                    rows="3"
                    value={formData.address}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50/50 text-slate-800 text-sm focus:bg-white focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all disabled:opacity-75 disabled:cursor-not-allowed"
                    placeholder="Enter full postal address..."
                  />
                </div>
              </div>

              {isEditing && (
                <div className="flex justify-end pt-2">
                  <button
                    type="submit"
                    disabled={saving}
                    className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-orange-500 hover:bg-orange-600 text-white text-sm font-semibold transition-all shadow-md shadow-orange-500/20 disabled:opacity-50"
                  >
                    <Save className="w-4 h-4" />
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              )}
            </form>
          </div>

          {/* Side Shortcuts & IRCTC Simulation Notes */}
          <div className="space-y-6">
            <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-orange-500" /> Quick Travel Actions
              </h3>
              <div className="space-y-3">
                <Link
                  to="/search"
                  className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 hover:bg-orange-50/60 border border-slate-200/60 text-slate-700 hover:text-orange-600 transition-all group"
                >
                  <span className="text-sm font-medium">Search & Book Trains</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>

                <Link
                  to="/pnr-status"
                  className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 hover:bg-orange-50/60 border border-slate-200/60 text-slate-700 hover:text-orange-600 transition-all group"
                >
                  <span className="text-sm font-medium">Check PNR Enquiry</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>

                <Link
                  to="/my-bookings"
                  className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 hover:bg-orange-50/60 border border-slate-200/60 text-slate-700 hover:text-orange-600 transition-all group"
                >
                  <span className="text-sm font-medium">Ticket Cancellation & Refund</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
            </div>

            <div className="bg-gradient-to-br from-indigo-50 to-orange-50/40 rounded-3xl p-6 border border-indigo-100">
              <h3 className="text-sm font-bold text-slate-900 mb-2">Simulation Architecture</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                RailSync is powered by a high-throughput C++17 route engine for Dijkstra graph resolution, combined with MySQL InnoDB ACID transactions and row-level locking for concurrent seat allocations.
              </p>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

export default Profile;
