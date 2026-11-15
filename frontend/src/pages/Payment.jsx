import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  CreditCard, CheckCircle2, XCircle, ShieldCheck, AlertCircle, 
  Train, Lock, Sparkles, RefreshCw, QrCode, Smartphone, Building2,
  ArrowRight, ArrowLeft, Shield, AlertTriangle, RotateCcw
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
  const autoAllocation = location.state?.autoAllocation ?? true;

  // Payment Method Tabs: 'UPI', 'CARD', 'NET_BANKING'
  const [activeMethod, setActiveMethod] = useState('UPI');

  // Form states
  const [upiId, setUpiId] = useState('passenger@okaxis');
  const [cardNumber, setCardNumber] = useState('4532 8921 4410 7823');
  const [cardHolder, setCardHolder] = useState(passengers[0]?.full_name || 'Rahul Sharma');
  const [cardExpiry, setCardExpiry] = useState('08/29');
  const [cardCvv, setCardCvv] = useState('821');
  const [selectedBank, setSelectedBank] = useState('SBI');

  // State Machine: 'IDLE' | 'PROCESSING' | 'SUCCESS' | 'FAILED'
  const [paymentState, setPaymentState] = useState('IDLE');
  const [processingStage, setProcessingStage] = useState('');
  const [paymentOutcome, setPaymentOutcome] = useState('SUCCESS'); // 'SUCCESS' or 'FAILURE'
  const [failureDetails, setFailureDetails] = useState(null);
  const [error, setError] = useState('');

  // Client-side idempotency tracking token
  const [idempotencyKey, setIdempotencyKey] = useState(() => 
    `IDEMP-${Date.now()}-${Math.random().toString(36).substring(2, 9).toUpperCase()}`
  );

  if (!train || passengers.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center bg-white rounded-3xl border border-slate-200 mt-8 space-y-4">
        <p className="text-slate-600 font-medium">No active booking session found.</p>
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
    if (paymentState === 'PROCESSING') return;

    setError('');
    setPaymentState('PROCESSING');
    setProcessingStage('Connecting to Indian RailPay Payment Gateway...');

    try {
      // Step 1: Realistic payment gateway handshake latency (1.0s)
      await new Promise(resolve => setTimeout(resolve, 600));
      setProcessingStage('Authorizing credentials with partner issuing bank...');
      await new Promise(resolve => setTimeout(resolve, 600));

      // Step 2: Call Payment Simulation API
      let payData;
      try {
        const payRes = await api.post('/payments/simulate', {
          amount: totalAmount,
          payment_method: activeMethod,
          outcome: paymentOutcome
        });
        payData = payRes.data;
      } catch (simErr) {
        // If simulation explicitly declined (HTTP 400 from test decline toggle)
        const simData = simErr.response?.data || {};
        throw {
          isDecline: true,
          message: simData.message || 'Payment simulation was declined by the simulated bank.',
          transactionId: simData.transaction_id || `TXN-DEC-${Date.now()}`,
          bankRef: simData.bank_ref_number || `REF-DEC-${Math.floor(10000000 + Math.random() * 90000000)}`
        };
      }

      if (payData.status !== 'SUCCESS') {
        throw {
          isDecline: true,
          message: payData.message || 'Payment authorization unsuccessful.',
          transactionId: payData.transaction_id,
          bankRef: payData.bank_ref_number
        };
      }

      // Step 3: ACID Transactional Booking in MySQL
      setProcessingStage('Acquiring InnoDB Seat Locks & Issuing Electronic PNR...');
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
          transaction_id: payData.transaction_id,
          payment_method: activeMethod,
          bank_ref_number: payData.bank_ref_number,
          idempotency_key: idempotencyKey
        }
      });

      if (!bookRes.data.success) {
        throw new Error(bookRes.data.error || 'Seat allocation conflict encountered.');
      }

      setPaymentState('SUCCESS');
      showToast("Payment captured & booking confirmed!", "success");

      // Smooth transition to confirmation page
      setTimeout(() => {
        navigate('/booking-confirmation', {
          state: {
            bookingResult: bookRes.data,
            train,
            journeyDate,
            payment: payData
          }
        });
      }, 700);

    } catch (err) {
      setPaymentState('FAILED');
      const declineMsg = err.message || err.data?.error || 'Payment authorization was rejected.';
      const txnId = err.transactionId || `TXN-FL-${Date.now()}`;
      const bankRef = err.bankRef || `REF-FL-${Math.floor(10000000 + Math.random() * 90000000)}`;

      setFailureDetails({
        message: declineMsg,
        transactionId: txnId,
        bankRef: bankRef,
        method: activeMethod,
        timestamp: new Date().toLocaleTimeString()
      });

      setError(declineMsg);
      showToast(declineMsg, "error");
    }
  };

  const handleRetryPayment = () => {
    // Reset to IDLE state while preserving all train, passenger, and seat context
    setPaymentState('IDLE');
    setPaymentOutcome('SUCCESS');
    setError('');
    setFailureDetails(null);
    // Refresh idempotency key for new attempt
    setIdempotencyKey(`IDEMP-${Date.now()}-${Math.random().toString(36).substring(2, 9).toUpperCase()}`);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Step Header */}
      <div>
        <span className="text-xs font-bold uppercase tracking-wider text-orange-600">
          Step 3 of 4 • Simulated Payment & Authoritative ACID Commit
        </span>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mt-1">
          Payment Authorization
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          RailSync Simulation Gateway • Academic Demonstration Platform
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Action Area (2 Cols) */}
        <div className="lg:col-span-2 space-y-6">

          {/* STATE 1: PROCESSING OVERLAY */}
          {paymentState === 'PROCESSING' && (
            <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm text-center space-y-6">
              <div className="w-16 h-16 mx-auto rounded-3xl saffron-gradient flex items-center justify-center text-white shadow-lg animate-pulse">
                <RefreshCw size={28} className="animate-spin" />
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-black text-slate-900">Authorizing Simulated Payment</h3>
                <p className="text-xs text-orange-600 font-semibold">{processingStage}</p>
                <p className="text-[11px] text-slate-400">
                  Please do not refresh the page or click back while seat locks are being acquired.
                </p>
              </div>

              {/* Progress step dots */}
              <div className="flex items-center justify-center gap-3 pt-4">
                <div className="w-2.5 h-2.5 rounded-full bg-orange-500 animate-ping" />
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold">
                  Gateway Handshake Active
                </span>
              </div>
            </div>
          )}

          {/* STATE 2: SUCCESS VIEW */}
          {paymentState === 'SUCCESS' && (
            <div className="bg-white rounded-3xl p-8 border border-emerald-200 shadow-sm text-center space-y-5">
              <div className="w-16 h-16 mx-auto rounded-3xl bg-emerald-500 text-white flex items-center justify-center shadow-lg">
                <CheckCircle2 size={32} />
              </div>
              <div className="space-y-1">
                <h3 className="text-xl font-black text-slate-900">Payment Authorized!</h3>
                <p className="text-xs text-emerald-600 font-semibold">
                  ACID transaction committed. Redirecting to your Electronic Ticket...
                </p>
              </div>
            </div>
          )}

          {/* STATE 3: DEDICATED PAYMENT FAILED VIEW */}
          {paymentState === 'FAILED' && (
            <div className="bg-white rounded-3xl p-6 sm:p-8 border border-rose-200 shadow-sm space-y-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-2xl bg-rose-50 border border-rose-200 text-rose-600 flex items-center justify-center shrink-0">
                  <XCircle size={28} />
                </div>
                <div className="space-y-1 flex-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-rose-600 bg-rose-50 border border-rose-200 px-2.5 py-0.5 rounded-full">
                    Transaction Declined / Failed
                  </span>
                  <h3 className="text-xl font-black text-slate-900 mt-1">
                    Payment Authorization Failed
                  </h3>
                  <p className="text-xs text-slate-600">
                    {failureDetails?.message || error || 'The simulated transaction was rejected.'}
                  </p>
                </div>
              </div>

              {/* Audit Details */}
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs space-y-2">
                <div className="flex justify-between text-slate-500">
                  <span>Simulation Status:</span>
                  <strong className="text-rose-600 font-bold">Declined (Rollback Verified)</strong>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>Transaction Attempt ID:</span>
                  <span className="font-mono text-slate-900 font-semibold">{failureDetails?.transactionId}</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>Bank Reference:</span>
                  <span className="font-mono text-slate-900 font-semibold">{failureDetails?.bankRef}</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>Payment Method:</span>
                  <span className="text-slate-900 font-semibold">{failureDetails?.method}</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>Seats State:</span>
                  <span className="text-slate-700 font-semibold">Inventory safely preserved; no seats allocated</span>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-center gap-2">
                <AlertTriangle size={16} className="shrink-0 text-amber-600" />
                <span>Your passenger details and train selection are safely preserved. You can retry with another method immediately.</span>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleRetryPayment}
                  className="saffron-gradient hover:brightness-110 text-white font-bold py-3 px-5 rounded-2xl shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95 text-xs sm:text-sm"
                >
                  <RotateCcw size={15} />
                  <span>Retry Payment</span>
                </button>

                <button
                  type="button"
                  onClick={() => navigate(-1)}
                  className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold py-3 px-5 rounded-2xl transition-all flex items-center justify-center gap-2 cursor-pointer text-xs sm:text-sm"
                >
                  <ArrowLeft size={15} />
                  <span>Modify Passenger Details</span>
                </button>
              </div>
            </div>
          )}

          {/* STATE 4: STANDARD IDLE PAYMENT FORM */}
          {paymentState === 'IDLE' && (
            <div className="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-sm space-y-6">
              
              {/* Method Selection Tabs */}
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

              {/* Simulation Mode Toggle */}
              <div className="pt-4 border-t border-slate-100 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                    Payment Gateway Test Simulation Mode:
                  </span>
                  <span className="text-[10px] text-slate-400">
                    Test Mode Toggle
                  </span>
                </div>
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
                    <span>Pass (Simulate Success)</span>
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
                    <span>Decline (Simulate Failure)</span>
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
                onClick={handleSimulatePayment}
                className="w-full saffron-gradient hover:brightness-110 text-white font-bold py-3.5 rounded-2xl shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95 text-sm"
              >
                <Lock size={16} />
                <span>Confirm & Authorize Payment ₹{totalAmount.toFixed(2)}</span>
              </button>
            </div>
          )}

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
