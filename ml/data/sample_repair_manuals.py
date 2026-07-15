"""
Sample repair manual data for knowledge base
Based on Operation CHARM and common Tata vehicle issues
"""

REPAIR_MANUALS = [
    {
        "title": "Tata Nexon Brake System Maintenance Guide",
        "doc_type": "manual",
        "category": "brake",
        "applicable_makes": "Tata",
        "applicable_models": "Nexon,Nexon EV",
        "year_from": 2018,
        "year_to": 2024,
        "content": """
        BRAKE SYSTEM MAINTENANCE - TATA NEXON
        
        Overview:
        The Tata Nexon is equipped with disc brakes on all four wheels with ABS and EBD systems. 
        Regular maintenance ensures optimal braking performance and safety.
        
        Brake Pad Inspection:
        - Inspect brake pads every 10,000 km
        - Minimum brake pad thickness: 2.5mm
        - Replace pads when thickness reaches 3mm or below
        - Check for uneven wear patterns
        
        Common Issues:
        1. Brake Pad Wear - Normal wear after 40,000-50,000 km
           Symptoms: Squealing noise, reduced braking efficiency, brake warning light
           DTC Codes: C0035, C0040, C0045, C0050
           
        2. Brake Fluid Contamination - Replace every 2 years
           Symptoms: Spongy brake pedal, reduced braking force
           Check fluid level in reservoir, look for dark/dirty fluid
           
        3. Brake Rotor Issues - Inspect with pad replacement
           Symptoms: Vibration during braking, pulsating pedal
           Minimum rotor thickness: Front 22mm, Rear 9mm
        
        Replacement Procedure:
        1. Lift vehicle and secure with jack stands
        2. Remove wheel (19mm lug nuts, torque: 110 Nm)
        3. Remove caliper bolts (12mm hex)
        4. Remove old brake pads
        5. Compress caliper piston using C-clamp
        6. Install new pads with anti-squeal shims
        7. Reinstall caliper and torque bolts to 30 Nm
        8. Pump brake pedal until firm
        9. Test drive and bed in new pads
        
        Parts Required:
        - Front brake pad set: Part# 5801517959 (₹2,500)
        - Rear brake pad set: Part# 5801517960 (₹2,000)
        - Brake fluid DOT 4: 1L (₹400)
        - Anti-squeal compound (₹200)
        
        Labor Time: 1.5 hours for complete replacement
        
        Safety Notes:
        - Never compress caliper with bleeder valve closed on ABS systems
        - Clean brake components with brake cleaner only
        - Wear safety glasses and gloves
        - Dispose of old brake fluid properly
        """
    },
    {
        "title": "Tata Vehicle Engine Cooling System Diagnosis",
        "doc_type": "manual",
        "category": "engine",
        "applicable_makes": "Tata",
        "applicable_models": "Nexon,Harrier,Safari,Altroz",
        "year_from": 2018,
        "year_to": 2024,
        "content": """
        ENGINE COOLING SYSTEM - DIAGNOSTIC GUIDE
        
        Overview:
        Tata vehicles use a pressurized liquid cooling system with thermostat control.
        Proper cooling system maintenance prevents engine damage and ensures optimal performance.
        
        Normal Operating Temperature:
        - Idle: 85-95°C
        - Highway: 90-100°C
        - Maximum safe: 105°C
        - Overheating threshold: >108°C
        
        Common Cooling System Issues:
        
        1. Thermostat Failure
           Symptoms: Engine runs cold (<85°C) or overheats quickly
           DTC Codes: P0128 (coolant temp below threshold)
           Diagnosis: Check coolant temp at startup, thermostat should open at 82°C
           Solution: Replace thermostat (₹800-1,200)
           Labor: 1 hour
           
        2. Coolant Leaks
           Symptoms: Low coolant level, steam from engine bay, sweet smell
           Common leak points: Radiator, hoses, water pump, heater core
           Diagnosis: Pressure test cooling system (16 PSI for 10 minutes)
           Solution: Replace failed component
           
        3. Radiator Fan Issues
           Symptoms: Overheating in traffic, normal temp at highway speeds
           DTC Codes: P0480, P0481 (fan control circuit)
           Diagnosis: Fan should activate at 95°C, check fuse, relay, fan motor
           Solution: Replace fan motor (₹3,500-5,000) or relay (₹200)
           
        4. Water Pump Failure
           Symptoms: Overheating, coolant leak from pump, squealing noise
           DTC Codes: P0301-P0304 (misfire due to overheating)
           Diagnosis: Check for play in pump shaft, look for coolant weep hole leak
           Solution: Replace water pump (₹4,000-6,000)
           Labor: 3-4 hours
           
        5. Head Gasket Failure (Severe)
           Symptoms: White exhaust smoke, bubbles in coolant, oil in coolant
           DTC Codes: P0300 (random misfire), P0420 (catalyst efficiency)
           Diagnosis: Compression test, block test for exhaust gases in coolant
           Solution: Head gasket replacement (₹15,000-25,000)
           Labor: 8-10 hours
        
        Diagnostic Procedure:
        1. Check coolant level in overflow tank (cold)
        2. Inspect for external leaks
        3. Check radiator cap pressure rating (1.1 bar)
        4. Scan for DTC codes
        5. Monitor coolant temp with scan tool during test drive
        6. Check fan operation
        7. Pressure test if leak suspected
        
        Maintenance Schedule:
        - Check coolant level: Every 5,000 km
        - Coolant flush and replace: Every 40,000 km or 2 years
        - Inspect hoses and clamps: Every 20,000 km
        - Test radiator cap: Annually
        
        Coolant Specifications:
        - Type: Ethylene glycol-based, OAT (Organic Acid Technology)
        - Color: Typically orange/red for Tata vehicles
        - Mixture: 50% coolant, 50% distilled water
        - Capacity: Nexon 5.5L, Harrier/Safari 8.0L, Altroz 5.0L
        
        Parts and Pricing:
        - Coolant (1L concentrate): ₹400-600
        - Thermostat: ₹800-1,200
        - Radiator cap: ₹150-250
        - Water pump: ₹4,000-6,000
        - Radiator: ₹8,000-15,000
        """
    },
    {
        "title": "Tata Vehicles Fuel System Troubleshooting",
        "doc_type": "manual",
        "category": "fuel",
        "applicable_makes": "Tata",
        "applicable_models": "Nexon,Harrier,Safari,Punch,Altroz,Tiago,Tigor",
        "year_from": 2018,
        "year_to": 2024,
        "content": """
        FUEL SYSTEM TROUBLESHOOTING GUIDE
        
        Overview:
        Modern Tata vehicles use electronic fuel injection with oxygen sensors for emissions control.
        Fuel trim adjustments indicate how the engine compensates for air-fuel mixture variations.
        
        Fuel Trim Basics:
        - Short Term Fuel Trim (STFT): Immediate adjustments
        - Long Term Fuel Trim (LTFT): Learned adjustments over time
        - Normal range: -10% to +10%
        - Positive trim: Engine adding fuel (running lean)
        - Negative trim: Engine reducing fuel (running rich)
        
        Common Fuel System Issues:
        
        1. Running Lean (High Positive Fuel Trim >+10%)
           Symptoms: Rough idle, hesitation, poor acceleration, check engine light
           DTC Codes: P0171 (bank 1 lean), P0174 (bank 2 lean)
           
           Possible Causes:
           a) Vacuum leak - Inspect intake manifold, vacuum hoses, brake booster
              Diagnosis: Spray carb cleaner around suspected areas, RPM will change
              Solution: Replace vacuum hoses or gaskets (₹500-2,000)
           
           b) Weak fuel pump - Pressure should be 3.5-4.0 bar
              Diagnosis: Connect fuel pressure gauge, test under load
              Solution: Replace fuel pump (₹6,000-10,000)
              Labor: 2-3 hours
           
           c) Clogged fuel filter
              Solution: Replace fuel filter every 40,000 km (₹800-1,500)
           
           d) Faulty MAF sensor - Measures air intake
              Diagnosis: Monitor MAF readings (idle: 2-3 g/s, 2500 RPM: 8-12 g/s)
              Solution: Clean with MAF cleaner (₹300) or replace (₹4,000-7,000)
           
           e) Oxygen sensor failure
              DTC Codes: P0131, P0132, P0133 (O2 sensor circuit)
              Solution: Replace O2 sensor (₹3,500-6,000)
        
        2. Running Rich (High Negative Fuel Trim <-10%)
           Symptoms: Black exhaust smoke, poor fuel economy, rough idle, spark plug fouling
           DTC Codes: P0172 (bank 1 rich), P0175 (bank 2 rich)
           
           Possible Causes:
           a) Leaking fuel injector
              Diagnosis: Check injector balance test, look for fuel in intake
              Solution: Replace faulty injector (₹4,000-7,000 each)
           
           b) Faulty coolant temp sensor - Engine thinks it's cold
              Diagnosis: Monitor coolant temp sensor reading vs actual
              Solution: Replace sensor (₹800-1,500)
           
           c) High fuel pressure - Regulator failure
              Diagnosis: Measure fuel pressure at idle and under vacuum
              Solution: Replace fuel pressure regulator (₹2,500-4,000)
           
           d) Dirty air filter
              Solution: Replace air filter every 10,000 km (₹400-800)
        
        3. EVAP System Issues
           Symptoms: Check engine light, fuel smell, failed emissions test
           DTC Codes: P0440-P0459 (EVAP system codes)
           
           Common causes:
           - Loose or damaged fuel cap - Most common (₹200-400)
           - EVAP purge valve failure (₹1,500-3,000)
           - Charcoal canister saturation (₹4,000-6,000)
           - Leak in EVAP lines
           
           Diagnosis: Smoke test EVAP system for leaks
        
        4. Fuel Contamination
           Symptoms: Sudden loss of power, misfires, won't start
           
           Water in fuel:
           - Drain fuel tank
           - Replace fuel filter
           - Add fuel system cleaner
           
           Wrong fuel (petrol in diesel):
           - DO NOT START ENGINE
           - Drain tank completely
           - Flush fuel system
           - Replace fuel filter
           Cost: ₹8,000-15,000
        
        Diagnostic Procedure:
        1. Scan for DTC codes
        2. Monitor fuel trims at idle and 2500 RPM
        3. Check fuel pressure (static and running)
        4. Inspect for vacuum leaks
        5. Check MAF and O2 sensor readings
        6. Perform fuel injector balance test
        7. Check fuel cap and EVAP system
        
        Maintenance:
        - Use quality fuel from reputable stations
        - Replace fuel filter every 40,000 km
        - Clean fuel injectors every 60,000 km
        - Replace air filter every 10,000 km
        - Use fuel system cleaner every 10,000 km
        
        Parts and Pricing:
        - Fuel filter: ₹800-1,500
        - Fuel pump: ₹6,000-10,000
        - Fuel injector: ₹4,000-7,000 each
        - O2 sensor: ₹3,500-6,000
        - MAF sensor: ₹4,000-7,000
        - Fuel pressure regulator: ₹2,500-4,000
        """
    },
    {
        "title": "Electrical System Diagnosis - Tata Vehicles",
        "doc_type": "manual",
        "category": "electrical",
        "applicable_makes": "Tata",
        "applicable_models": "Nexon,Harrier,Safari,Punch,Altroz,Tiago,Tigor",
        "year_from": 2018,
        "year_to": 2024,
        "content": """
        ELECTRICAL SYSTEM DIAGNOSTIC GUIDE
        
        Overview:
        Tata vehicles use a 12V electrical system with alternator charging and battery management.
        Proper diagnosis prevents no-start conditions and electrical component failures.
        
        Battery and Charging System:
        
        Normal Voltage Readings:
        - Battery at rest (engine off): 12.6-12.8V
        - Healthy battery minimum: 12.4V
        - Replace battery below: 12.2V
        - Charging (engine running): 13.8-14.4V
        - Charging system issue: <13.5V or >14.8V
        
        Battery Specifications:
        - Type: Maintenance-free lead-acid
        - Capacity: 45-50 Ah (small cars), 60-65 Ah (SUVs)
        - Cold Cranking Amps: 400-500 CCA (small), 550-650 CCA (SUVs)
        - Life expectancy: 3-4 years in Indian climate
        
        Common Issues:
        
        1. Low Battery Voltage (<12.5V)
           Symptoms: Slow cranking, dim lights, electrical issues
           DTC Codes: B0001, U0100 (lost communication)
           
           Causes:
           a) Weak battery - Age >3 years
              Diagnosis: Load test (apply 50% CCA load, voltage should stay >9.6V)
              Solution: Replace battery (₹4,000-8,000)
           
           b) Parasitic drain
              Diagnosis: Check current draw with engine off (should be <50mA)
              Common culprits: Interior lights, aftermarket accessories, faulty modules
              Solution: Identify and fix drain source
           
           c) Corroded terminals
              Symptoms: Intermittent electrical issues
              Solution: Clean terminals with wire brush and apply anti-corrosion spray (₹200)
        
        2. Charging System Failure
           Symptoms: Battery light on, dim headlights, battery dies after driving
           DTC Codes: P0620, P0621 (alternator control circuit)
           
           Diagnosis:
           - Check voltage at battery with engine running
           - Should increase from 12.6V to 13.8-14.4V
           - Rev engine to 2000 RPM and observe voltage
           - Check alternator output (should be >13.5V)
           
           Causes:
           a) Failed alternator
              Signs: Grinding noise, battery light, smell of burning
              Solution: Replace alternator (₹6,000-12,000)
              Labor: 2-3 hours
           
           b) Bad voltage regulator
              Signs: Overcharging (>14.8V) or undercharging (<13.5V)
              Solution: Replace voltage regulator (₹1,500-3,000)
           
           c) Worn alternator belt
              Signs: Squealing noise, loose belt
              Solution: Replace drive belt (₹800-1,500)
           
           d) Bad battery connection
              Solution: Clean and tighten terminals
        
        3. Starter Motor Issues
           Symptoms: Click noise but no crank, grinding noise, slow cranking
           DTC Codes: P0615, P0617 (starter relay)
           
           Causes:
           a) Weak battery - Check first
              Diagnosis: Voltage drops below 10V during cranking
           
           b) Faulty starter solenoid
              Signs: Single click, no crank
              Solution: Replace starter or solenoid (₹5,000-10,000)
           
           c) Bad starter motor
              Signs: Grinding noise, intermittent starting
              Solution: Replace starter motor (₹5,000-10,000)
              Labor: 2 hours
           
           d) Poor ground connection
              Check battery negative to engine ground strap
        
        4. Electrical Module Communication Loss
           Symptoms: Warning lights, features not working, check engine light
           DTC Codes: U0100, U0121, U0155 (CAN communication)
           
           Causes:
           - Low battery voltage (<11V)
           - Faulty BCM (Body Control Module)
           - CAN bus wiring issues
           - Water damage to modules
           
           Diagnosis:
           - Check all module voltages
           - Scan for communication DTCs
           - Check CAN high/low signals (2.5V nominal)
           
           Solution: Address voltage issues first, then module replacement if needed
        
        5. Alternator Overcharging (>14.8V)
           Symptoms: Boiling battery, burning smell, blown bulbs
           DTC Codes: P0622 (generator field control)
           
           Danger: Can damage battery and electronic modules
           
           Solution:
           - Replace voltage regulator immediately
           - Check for battery damage
           - Inspect sensitive electronic modules
        
        Diagnostic Procedure:
        1. Check battery voltage at rest
        2. Perform load test on battery
        3. Start engine and check charging voltage
        4. Check for voltage drops in cables
        5. Test alternator output under load
        6. Check for parasitic drain
        7. Inspect all connections and grounds
        8. Scan for DTC codes
        
        Preventive Maintenance:
        - Clean battery terminals every 6 months
        - Check belt tension every 10,000 km
        - Test battery annually after 2 years
        - Check alternator output during service
        - Inspect ground connections
        - Avoid deep discharge of battery
        
        Parts and Pricing:
        - Battery (45Ah): ₹4,000-6,000
        - Battery (65Ah): ₹6,000-8,000
        - Alternator: ₹6,000-12,000
        - Starter motor: ₹5,000-10,000
        - Drive belt: ₹800-1,500
        - Battery cables: ₹500-1,000
        - Terminal cleaning kit: ₹200
        
        Tools Required:
        - Digital multimeter
        - Battery load tester
        - Ammeter (for parasitic drain testing)
        - Wire brush for terminal cleaning
        """
    },
    {
        "title": "General Maintenance Schedule - Tata Vehicles",
        "doc_type": "guide",
        "category": "maintenance",
        "applicable_makes": "Tata",
        "applicable_models": "Nexon,Harrier,Safari,Punch,Altroz,Tiago,Tigor",
        "year_from": 2018,
        "year_to": 2024,
        "content": """
        PERIODIC MAINTENANCE SCHEDULE
        
        Overview:
        Regular maintenance ensures reliability, performance, and resale value.
        Follow this schedule for optimal vehicle health.
        
        Every 5,000 km or 3 Months:
        - Engine oil and filter change (₹2,500-4,000)
        - Visual inspection of brakes, tires, lights
        - Check all fluid levels
        - Inspect drive belts
        - Clean air filter (replace if needed)
        - Tire rotation (₹400-800)
        
        Every 10,000 km or 6 Months:
        - Replace air filter (₹400-800)
        - Inspect brake pads and discs
        - Check battery voltage and terminals
        - Inspect suspension components
        - Check wheel alignment if uneven tire wear
        - Top up windshield washer fluid
        
        Every 20,000 km or 1 Year:
        - Replace cabin air filter (₹500-1,000)
        - Inspect brake fluid (replace if dark)
        - Check coolant level and condition
        - Inspect exhaust system
        - Check steering and suspension
        - Lubricate door hinges and locks
        
        Every 40,000 km or 2 Years:
        - Replace fuel filter (₹800-1,500)
        - Flush and replace coolant (₹1,500-3,000)
        - Replace brake fluid (₹800-1,500)
        - Inspect spark plugs (petrol engines)
        - Check transmission fluid level
        - Clean throttle body
        - Clean fuel injectors
        
        Every 60,000 km or 3 Years:
        - Replace spark plugs petrol (₹2,000-4,000)
        - Replace drive belts (₹1,500-3,000)
        - Flush power steering fluid
        - Inspect AC system and recharge if needed
        - Check wheel bearings
        
        Every 80,000 km or 4 Years:
        - Replace battery (₹4,000-8,000)
        - Major service inspection
        - Inspect clutch (manual transmission)
        - Check engine mounts
        
        Every 100,000 km or 5 Years:
        - Replace timing belt/chain (if applicable) (₹8,000-15,000)
        - Transmission fluid change (₹3,000-5,000)
        - Comprehensive inspection of all systems
        
        Diesel Engine Specific:
        - DPF regeneration check every 20,000 km
        - Diesel particulate filter cleaning at 80,000 km
        - Fuel injector cleaning every 60,000 km
        
        Consumables Pricing:
        - Engine oil (4L): ₹1,500-3,000
        - Oil filter: ₹300-600
        - Air filter: ₹400-800
        - Cabin filter: ₹500-1,000
        - Fuel filter: ₹800-1,500
        - Spark plugs (set of 4): ₹2,000-4,000
        
        Critical Inspections:
        - Check engine warning light - Address immediately
        - Brake warning light - Do not drive, inspect immediately
        - Oil pressure light - Stop engine immediately
        - Temperature warning - Stop and cool down
        - ABS warning light - Have checked within a week
        
        Seasonal Maintenance:
        
        Monsoon Preparation:
        - Check wiper blades (replace if streaking)
        - Test all lights and turn signals
        - Inspect tire tread depth (minimum 2mm)
        - Check door seals for water leaks
        - Apply anti-fog treatment to windows
        - Check brake performance
        
        Summer Preparation:
        - Check AC system performance
        - Inspect coolant level
        - Check battery (heat causes failure)
        - Verify tire pressure (adjust for heat)
        - Top up windshield washer with summer formula
        
        DIY Maintenance Tips:
        - Check tire pressure weekly (when cold)
        - Inspect tires for uneven wear
        - Check oil level monthly
        - Keep vehicle clean (wash every 2 weeks)
        - Check lights monthly
        - Listen for unusual noises
        - Monitor fuel economy changes
        
        Warning Signs to Address Immediately:
        - Unusual noises (grinding, squealing, knocking)
        - Vibrations or pulling while driving
        - Leaking fluids
        - Warning lights on dashboard
        - Smoke from exhaust or engine
        - Burning smells
        - Difficulty starting
        - Loss of power
        
        Service Records:
        - Keep all service receipts
        - Log maintenance in service book
        - Document unusual issues or repairs
        - Track fuel economy for trends
        - Increases resale value
        """
    }
]
