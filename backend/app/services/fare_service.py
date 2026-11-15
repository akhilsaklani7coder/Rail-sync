import math

class FareService:
    """
    Centralized, rules-based dynamic fare calculation engine for RailSync.
    Computes accurate passenger fares based on train base fare, travel class multipliers,
    reservation fees, superfast surcharges, and statutory GST.
    """

    CLASS_MULTIPLIERS = {
        '1A': 2.60,  # AC First Class
        '2A': 1.80,  # AC 2-Tier
        '3A': 1.35,  # AC 3-Tier
        'CC': 1.00,  # AC Chair Car (Baseline)
        'SL': 0.55   # Sleeper Class
    }

    RESERVATION_FEES = {
        '1A': 60.00,
        '2A': 50.00,
        '3A': 40.00,
        'CC': 40.00,
        'SL': 20.00
    }

    SUPERFAST_CHARGES = {
        '1A': 45.00,
        '2A': 45.00,
        '3A': 45.00,
        'CC': 45.00,
        'SL': 30.00
    }

    GST_RATE = 0.05  # 5% GST on AC classes; 0% on Sleeper

    @classmethod
    def calculate_fare(cls, train_base_fare, travel_class='CC', train_type='EXPRESS', num_passengers=1):
        """
        Calculates a full fare breakdown. Returns a dictionary with all components.
        """
        travel_class = str(travel_class).upper()
        if travel_class not in cls.CLASS_MULTIPLIERS:
            travel_class = 'CC'

        num_passengers = max(1, int(num_passengers))
        train_base_fare = float(train_base_fare)

        # 1. Base Class Fare
        multiplier = cls.CLASS_MULTIPLIERS.get(travel_class, 1.0)
        class_fare = round(train_base_fare * multiplier, 2)

        # 2. Reservation Fee
        res_fee = cls.RESERVATION_FEES.get(travel_class, 40.00)

        # 3. Superfast / Flagship Surcharge
        is_superfast = train_type in ['VANDE_BHARAT', 'RAJDHANI', 'SHATABDI', 'SUPERFAST', 'DURONTO', 'GARIB_RATH']
        superfast_charge = cls.SUPERFAST_CHARGES.get(travel_class, 45.00) if is_superfast else 0.00

        # Subtotal per passenger before GST
        subtotal_per_passenger = class_fare + res_fee + superfast_charge

        # 4. GST (applicable only on AC classes: 1A, 2A, 3A, CC)
        is_ac = travel_class in ['1A', '2A', '3A', 'CC']
        gst_per_passenger = round(subtotal_per_passenger * cls.GST_RATE, 2) if is_ac else 0.00

        fare_per_passenger = round(subtotal_per_passenger + gst_per_passenger, 2)
        total_fare = round(fare_per_passenger * num_passengers, 2)

        return {
            "travel_class": travel_class,
            "train_type": train_type,
            "num_passengers": num_passengers,
            "class_fare_per_passenger": class_fare,
            "reservation_fee_per_passenger": res_fee,
            "superfast_charge_per_passenger": superfast_charge,
            "gst_per_passenger": gst_per_passenger,
            "fare_per_passenger": fare_per_passenger,
            "total_base_amount": round(class_fare * num_passengers, 2),
            "total_reservation_fee": round(res_fee * num_passengers, 2),
            "total_superfast_charge": round(superfast_charge * num_passengers, 2),
            "total_gst": round(gst_per_passenger * num_passengers, 2),
            "total_amount": total_fare
        }

    @classmethod
    def calculate_cancellation_refund(cls, total_amount, booking_status='CONFIRMED', travel_class='CC', num_passengers=1):
        """
        Calculates cancellation fee and net simulated refund.
        """
        travel_class = str(travel_class).upper()
        num_passengers = max(1, int(num_passengers))
        total_amount = float(total_amount)

        if booking_status in ['WAITLISTED', 'RAC']:
            # Flat clerkage fee for waitlisted/RAC tickets: ₹60 per passenger
            cancellation_fee = round(60.00 * num_passengers, 2)
        else:
            # Confirmed cancellation fee rules
            fee_per_passenger = 120.00 if travel_class in ['1A', '2A', '3A', 'CC'] else 60.00
            cancellation_fee = round(fee_per_passenger * num_passengers, 2)

        cancellation_fee = min(cancellation_fee, total_amount)
        refund_amount = round(max(0.00, total_amount - cancellation_fee), 2)

        return {
            "gross_amount": total_amount,
            "cancellation_fee": cancellation_fee,
            "refund_amount": refund_amount,
            "booking_status": booking_status,
            "travel_class": travel_class
        }

