import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  CreditCard, CheckCircle2, XCircle, ShieldCheck, AlertCircle, 
  Train, Lock, Sparkles, RefreshCw, QrCode, Smartphone, Building2,
  ArrowRight, Shield
} from 'lucide-react';
import api from '../api/axios';
import { useToast } from '../context/ToastContext';

const Payment = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const train = location.state?.train;
  const journeyDate = location.state?.journeyDate;
  const travelClass = location.state?.travelClass || 'CC';
  const passengers = location.state?.passengers || [];
  const selectedSeatIds = location.state?.selectedSeatIds;
  const totalAmount = location.state?.totalAmount || 0;
  const fareQuote = location.state?.fareQuote;

  // Payment Method Tabs: 'UPI', 'CARD', 'NET_BANKING'
  const [activeMethod, setActiveMethod] = useState('UPI');

  // Form states
  const [upiId, setUpiId] = useState('passenger@okaxis');
  const [cardNumber, setCardNumber] = useState('4532 8921 4410 7823');
  const [cardHolder, setCardHolder] = useState(passengers[0]?.full_name || 'Rahul Sharma');
  const [cardExpiry, setCardExpiry] = useState('08/29');
  const [cardCvv, setCardCvv] = useState('821');
  const [selectedBank, setSelectedBank] = useState('SBI');

  // Simulation Outcome
  const [paymentOutcome, setPaymentOutcome] = useState('SUCCESS'); // 'SUCCESS' or 'FAILURE'
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');

  if (!train || passengers.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center bg-white rounded-3xl border border-slate-200 mt-8 space-y-4">
        <p className="text-slate-600">No active booking session found.</p>
        <button
          onClick={() => navigate('/search')}
          className="saffron-gradient text-white px-6 py-2.5 rounded-xl text-xs font-bold"
        >
          Search Trains
        </button>
      </div>
    );
  }

  const handleSimulatePayment = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      // 1. Call Payment Simulation API
      const payRes = await api.post('/payments/simulate', {
        amount: totalAmount,
        payment_method: activeMethod,
        outcome: paymentOutcome
      });

      if (payRes.data.status !== 'SUCCESS') {
        throw new Error(payRes.data.message || 'Payment simulation failed.');
      }

      // 2. Upon successful simulated payment, execute ACID Transactional Booking in MySQL
      const bookRes = await api.post('/bookings', {
        train_id: train.id,
        journey_date: journeyDate,
        travel_class: travelClass,
        passengers: passengers.map(p => ({
          full_name: p.full_name,
          age: p.age,
          gender: p.gender,
          berth_preference: p.berth_preference || 'NO_PREFERENCE'
        })),
        seat_ids: selectedSeatIds,
        payment_details: {
          transaction_id: payRes.data.transaction_id,
          payment_method: activeMethod,
          bank_ref_number: payRes.data.bank_ref_number
        }
      });

      if (!bookRes.data.success) {
        throw new Error(bookRes.data.error || 'Seat allocation failed.');
      }

      showToast("Payment captured & booking confirmed!", "success");

      // 3. Navigate to Booking Confirmation
      navigate('/booking-confirmation', {
        state: {
          bookingResult: bookRes.data,
          train,
          journeyDate,
          payment: payRes.data
        }
      });

    } catch (err) {
      const msg = err.data?.error || err.message || 'Payment or booking transaction failed.';
      setError(msg);
      showToast(msg, "error");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Step Header */}
      <div>
        <span className="text-xs font-bold uppercase tracking-wider text-orange-600">
          Step 3 of 4 • Simulated Payment & ACID Commit
        </span>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mt-1">
          Simulated Payment Gateway
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Educational Simulation Platform • No actual money or banking credentials are required.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Payment Methods & Simulator Form (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Method Selection Tabs */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-sm space-y-6">
            <div className="flex border-b border-slate-100 pb-3 gap-2">
              <button
                type="button"
                onClick={() => setActiveMethod('UPI')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeMethod === 'UPI' 
                    ? 'bg-slate-900 text-white shadow-xs' 
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <Smartphone size={15} />
                <span>UPI / QR</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveMethod('CARD')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeMethod === 'CARD' 
                    ? 'bg-slate-900 text-white shadow-xs' 
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <CreditCard size={15} />
                <span>Credit / Debit Card</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveMethod('NET_BANKING')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeMethod === 'NET_BANKING' 
                    ? 'bg-slate-900 text-white shadow-xs' 
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <Building2 size={15} />
                <span>Net Banking</span>
              </button>
            </div>

            {/* Tab 1: UPI */}
            {activeMethod === 'UPI' && (
              <div className="space-y-4">
                <div className="p-4 rounded-2xl bg-orange-50/70 border border-orange-200 text-xs text-orange-900 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-orange-500 text-white flex items-center justify-center font-bold">
                      <QrCode size={20} />
                    </div>
                    <div>
                      <p className="font-bold">Instant Simulated UPI Intent</p>
                      <p className="text-[11px] text-orange-800">GPay, PhonePe, Paytm, BHIM</p>
                    </div>
                  </div>
                  <span className="font-mono font-black text-sm text-orange-700">₹{totalAmount.toFixed(2)}</span>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                    Virtual Payment Address (VPA) / UPI ID
                  </label>
                  <input
                    type="text"
                    value={upiId}
                    onChange={(e) => setUpiId(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/30"
                    placeholder="user@upi"
                  />
                </div>
              </div>
            )}

            {/* Tab 2: Credit / Debit Card */}
            {activeMethod === 'CARD' && (
              <div className="space-y-4">
                <div className="space-y-1">
                  <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                    Card Number
                  </label>
                  <input
                    type="text"
                    value={cardNumber}
                    onChange={(e) => setCardNumber(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs font-mono font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/30"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                      Cardholder Name
                    </label>
                    <input
                      type="text"
                      value={cardHolder}
                      onChange={(e) => setCardHolder(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/30"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                        Expiry
                      </label>
                      <input
                        type="text"
                        value={cardExpiry}
                        onChange={(e) => setCardExpiry(e.target.value)}
                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-mono font-semibold text-slate-900"
                        placeholder="MM/YY"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                        CVV
                      </label>
                      <input
                        type="password"
                        maxLength={4}
                        value={cardCvv}
                        onChange={(e) => setCardCvv(e.target.value)}
                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-mono font-semibold text-slate-900"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Tab 3: Net Banking */}
            {activeMethod === 'NET_BANKING' && (
              <div className="space-y-3">
                <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                  Select Partner Bank
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
                  {[
                    { id: 'SBI', name: 'State Bank of India' },
                    { id: 'HDFC', name: 'HDFC Bank' },
                    { id: 'ICICI', name: 'ICICI Bank' },
                    { id: 'AXIS', name: 'Axis Bank' },
                    { id: 'PNB', name: 'Punjab National Bank' },
                    { id: 'KOTAK', name: 'Kotak Mahindra Bank' }
                  ].map(b => (
                    <button
                      key={b.id}
                      type="button"
                      onClick={() => setSelectedBank(b.id)}
                      className={`p-3 rounded-2xl border text-left font-bold transition-all cursor-pointer ${
                        selectedBank === b.id 
                          ? 'bg-orange-500/10 border-orange-500 text-orange-700 ring-1 ring-orange-500' 
                          : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      {b.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Simulation Outcome Switcher */}
            <div className="pt-4 border-t border-slate-100 space-y-3">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                Simulation Outcome Toggle:
              </span>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <button
                  type="button"
                  onClick={() => setPaymentOutcome('SUCCESS')}
                  className={`p-3 rounded-2xl border font-bold flex items-center justify-center gap-2 cursor-pointer transition-all ${
                    paymentOutcome === 'SUCCESS'
                      ? 'bg-emerald-500 text-white border-emerald-500 shadow-sm'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  <CheckCircle2 size={16} />
                  <span>Simulate Success (Commit)</span>
                </button>

                <button
                  type="button"
                  onClick={() => setPaymentOutcome('FAILURE')}
                  className={`p-3 rounded-2xl border font-bold flex items-center justify-center gap-2 cursor-pointer transition-all ${
                    paymentOutcome === 'FAILURE'
                      ? 'bg-rose-600 text-white border-rose-600 shadow-sm'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  <XCircle size={16} />
                  <span>Simulate Decline (Rollback)</span>
                </button>
              </div>
            </div>

            {error && (
              <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
                <AlertCircle size={16} className="shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="button"
              disabled={processing}
              onClick={handleSimulatePayment}
              className="w-full saffron-gradient hover:brightness-110 text-white font-bold py-3.5 rounded-2xl shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95 text-sm disabled:opacity-50"
            >
              {processing ? (
                <>
                  <RefreshCw size={16} className="animate-spin" />
                  <span>Executing ACID Seat Allocation...</span>
                </>
              ) : (
                <>
                  <Lock size={16} />
                  <span>Confirm & Authorize ₹{totalAmount.toFixed(2)}</span>
                </>
              )}
            </button>
          </div>

        </div>

        {/* Order Summary Sidebar */}
        <div className="space-y-6">
          <div className="bg-slate-950 text-white rounded-3xl p-6 border border-slate-800 shadow-md space-y-5">
            <div>
              <span className="text-[10px] text-orange-400 font-bold uppercase tracking-widest block">Journey Summary</span>
              <h3 className="font-black text-white text-base mt-1">{train.train_name}</h3>
              <p className="text-xs text-slate-400 font-mono">#{train.train_number} • Class {travelClass}</p>
            </div>

            <div className="space-y-2 text-xs border-y border-slate-800 py-4">
              <div className="flex justify-between text-slate-400">
                <span>Date:</span>
                <strong className="text-white">{journeyDate}</strong>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Route:</span>
                <strong className="text-white">{train.source_station_name} → {train.destination_station_name}</strong>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Departure:</span>
                <strong className="text-white">{train.departure_time}</strong>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Passengers:</span>
                <strong className="text-white">{passengers.length} travelers</strong>
              </div>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Base Class Fare:</span>
                <span className="font-mono text-white">₹{fareQuote?.total_base_amount?.toFixed(2) || (train.base_fare * passengers.length).toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Reservation & SF Fee:</span>
                <span className="font-mono text-white">₹{((fareQuote?.total_reservation_fee || 0) + (fareQuote?.total_superfast_charge || 0)).toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>GST (5% on AC):</span>
                <span className="font-mono text-white">₹{fareQuote?.total_gst?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="pt-3 border-t border-slate-800 flex justify-between items-center text-sm">
                <span className="font-black text-white">Total Amount</span>
                <span className="text-2xl font-black text-orange-400 font-mono">₹{totalAmount.toFixed(2)}</span>
              </div>
            </div>

            <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
              <Shield size={14} className="text-emerald-400 shrink-0" />
              <span>ACID Row-Lock Seat Allocation Protection active.</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};

export default Payment;
