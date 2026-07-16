# 🎨 AutoSense AI - Visual Tour Guide

## 🌟 Welcome Screen

When you open **http://localhost:3000**, you'll see:

### Login Page
```
┌─────────────────────────────────────────┐
│                                         │
│         AutoSense AI                    │
│   Intelligent Vehicle Diagnosis         │
│                                         │
│  ┌───────────────────────────────┐     │
│  │        Sign In                │     │
│  │                               │     │
│  │  Email: [________________]    │     │
│  │  Password: [____________]     │     │
│  │                               │     │
│  │     [  Sign In Button  ]      │     │
│  │                               │     │
│  │  Quick Login (Demo):          │     │
│  │  [Admin] [Manager] [Mechanic] │     │
│  │          [Owner]              │     │
│  └───────────────────────────────┘     │
└─────────────────────────────────────────┘
```

**What to Do:**
1. Click any **Quick Login** button
2. You'll be automatically logged in and redirected

---

## 👨‍🔧 Mechanic Dashboard

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  AutoSense AI    |   Mechanic Name     [Logout]        │
├─────────────────────────────────────────────────────────┤
│  Mechanic Dashboard                                     │
│  AI-powered vehicle diagnostics                         │
│                                                         │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐              │
│  │  50  │  │  23  │  │   5  │  │   2  │              │
│  │Vehicl│  │Diagno│  │Pendin│  │Critic│              │
│  └──────┘  └──────┘  └──────┘  └──────┘              │
│                                                         │
│  Run AI Diagnosis                                       │
│  ┌─────────────────────┐  ┌──────────────┐            │
│  │Select Vehicle    ▼  │  │Run Diagnosis │            │
│  └─────────────────────┘  └──────────────┘            │
│                                                         │
│  Recent Diagnoses                                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │Vehicle│Type│Severity│Confidence│Status│Actions│   │
│  ├───────┴────┴────────┴──────────┴──────┴───────┤   │
│  │MH12AB1234 Engine CRITICAL 89% Pending [View]  │   │
│  │DL05CD5678 Brake  HIGH     92% Complete [View] │   │
│  │KA03EF9012 Normal LOW      96% Complete [View] │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Key Features to Try:
1. **Stats Cards**: See totals at top
2. **Vehicle Selector**: Click dropdown to pick a vehicle
3. **Run Diagnosis**: Click button to start AI analysis
4. **View Details**: Click to see full AI report

### Diagnosis Details Modal
```
┌──────────────────────────────────────────────┐
│  Diagnosis Details                      [X]  │
├──────────────────────────────────────────────┤
│  Overview                                    │
│  Vehicle: MH12AB1234                         │
│  Severity: [CRITICAL]  Confidence: 89%       │
│  Cost: ₹5,000 - ₹8,000  Time: 3 hours       │
│                                              │
│  ML Prediction                               │
│  Predicted Issue: Engine Failure             │
│  Explanation: High coolant temp + low oil... │
│  Top Features:                               │
│    • Coolant Temp: 105°C (impact: +0.45)   │
│    • Oil Pressure: 15 PSI (impact: +0.38)  │
│                                              │
│  RAG Context                                 │
│  Relevant Articles:                          │
│    • "Engine Overheating Guide" (95%)      │
│    • "Oil System Maintenance" (87%)        │
│                                              │
│  AI Repair Guide                             │
│  1. Check coolant level                      │
│  2. Inspect oil pump                         │
│  3. Replace thermostat                       │
│  Required Parts: Thermostat (₹1,200)       │
│                                              │
│  [Close]                                     │
└──────────────────────────────────────────────┘
```

---

## 👨‍💼 Admin Dashboard

### Layout with Tabs
```
┌─────────────────────────────────────────────────┐
│  AutoSense AI    |   Admin Name   [Logout]     │
├─────────────────────────────────────────────────┤
│  Admin Dashboard                                │
│  System overview and management                 │
│                                                 │
│  [Overview] [Users] [Showrooms] [Analytics]    │
│  ────────                                       │
│                                                 │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐      │
│  │  45  │  │   8  │  │ 125  │  │  234 │      │
│  │Users │  │Showrm│  │Vehicl│  │Diagno│      │
│  └──────┘  └──────┘  └──────┘  └──────┘      │
│                                                 │
│  Users by Role              Diagnoses          │
│  ┌──────────────────┐  ┌──────────────────┐   │
│  │Admin    ██ 5    │  │Critical ████ 12  │   │
│  │Manager  ███ 8   │  │High     ███  8   │   │
│  │Mechanic █████ 15│  │Medium   ██   4   │   │
│  │Owner    ███████ │  │Low      █    2   │   │
│  └──────────────────┘  └──────────────────┘   │
│                                                 │
│  System Status                                  │
│  ● API Status: Operational                     │
│  ● ML Model: Active                            │
│  ● Database: Connected                         │
└─────────────────────────────────────────────────┘
```

### Users Tab
```
┌─────────────────────────────────────────────────┐
│  [Overview] [Users] [Showrooms] [Analytics]    │
│           ───────                               │
│                                                 │
│  User Management              [+ Add User]      │
│  ┌──────────────────────────────────────────┐  │
│  │Avatar│Name      │Role    │Status│Actions│  │
│  ├──────┼──────────┼────────┼──────┼───────┤  │
│  │ [A] │Admin User│ADMIN   │●Activ│[Edit] │  │
│  │ [R] │Raj Kumar │MECHANIC│●Activ│[Edit] │  │
│  │ [S] │Sara Khan │MANAGER │●Activ│[Edit] │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 🏢 Showroom Dashboard

### Layout
```
┌─────────────────────────────────────────────────┐
│  AutoSense AI    |   Manager Name [Logout]     │
├─────────────────────────────────────────────────┤
│  Showroom Dashboard                             │
│  Manage your showroom operations                │
│                                                 │
│  [Overview] [Vehicles] [Mechanics] [Diagnoses] │
│  ─────────                                      │
│                                                 │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌───┐│
│  │ 42  │ │  8  │ │  5  │ │ 12  │ │  3  │ │₹45K││
│  │Vehic│ │Mecha│ │Pendi│ │Compl│ │Criti│ │Rev ││
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └───┘│
│                                                 │
│  Recent Diagnoses          Mechanic Performance │
│  ┌────────────────┐      ┌────────────────┐    │
│  │MH12 Engine  ●  │      │ [R] Raj  ●Activ│    │
│  │DL05 Brake   ●  │      │ [A] Amit ●Activ│    │
│  │KA03 Normal  ●  │      │ [P] Priya●Activ│    │
│  └────────────────┘      └────────────────┘    │
└─────────────────────────────────────────────────┘
```

### Vehicles Tab
```
┌─────────────────────────────────────────────────┐
│  [Overview] [Vehicles] [Mechanics] [Diagnoses] │
│            ──────────                           │
│                                                 │
│  Vehicles                     [+ Add Vehicle]   │
│  ┌─────────────────────────────────────────┐   │
│  │Reg No    │Make/Model│Year│Owner │Actions│   │
│  ├──────────┼──────────┼────┼──────┼───────┤   │
│  │MH12AB1234│Tata Nexon│2022│Rahul │[View] │   │
│  │DL05CD5678│Tata Harr.│2021│Sarah │[View] │   │
│  │KA03EF9012│Tata Punch│2023│Amit  │[View] │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## 🚗 Car Owner Dashboard

### Vehicle Cards
```
┌─────────────────────────────────────────────────┐
│  AutoSense AI    |   Owner Name   [Logout]     │
├─────────────────────────────────────────────────┤
│  My Vehicles                                    │
│  Monitor your vehicle health                    │
│                                                 │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  │
│  │MH12AB1234│  │DL05CD5678│  │KA03EF9012│  │
│  │Tata Nexon│  │Tata Harri│  │Tata Punch│  │
│  │2022 Petrol│  │2021 Diesel│ │2023 Petrol│ │
│  │          │  │          │  │          │  │
│  │   ┌──┐  │  │   ┌──┐  │  │   ┌──┐  │  │
│  │   │85│  │  │   │72│  │  │   │95│  │  │
│  │   └──┘  │  │   └──┘  │  │   └──┘  │  │
│  │ Excellent│  │   Good  │  │ Excellent│  │
│  │          │  │          │  │          │  │
│  │Total: 5  │  │Total: 8  │  │Total: 2  │  │
│  │Pending: 0│  │Pending: 1│  │Pending: 0│  │
│  │          │  │          │  │          │  │
│  │[Details] │  │[Details] │  │[Details] │  │
│  └───────────┘  └───────────┘  └───────────┘  │
└─────────────────────────────────────────────────┘
```

### Service History (after clicking vehicle)
```
┌─────────────────────────────────────────────────┐
│  Service History - MH12AB1234                   │
│  ┌─────────────────────────────────────────┐   │
│  │Date  │Type  │Severity│Status│Cost│Actions│   │
│  ├──────┼──────┼────────┼──────┼────┼───────┤   │
│  │Jan 15│Engine│CRITICAL│Done  │₹7K │[View] │   │
│  │Dec 20│Brake │HIGH    │Done  │₹3K │[View] │   │
│  │Nov 10│Normal│LOW     │Done  │₹1K │[View] │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## 🎨 Color Legend

### Status Badges
- 🟢 **Green**: Active, Completed, Excellent, Low severity
- 🟡 **Yellow**: Pending, Fair, Medium severity
- 🟠 **Orange**: In Progress, High severity
- 🔴 **Red**: Inactive, Critical, Poor

### Health Scores
- **80-100**: 🟢 Excellent (Green circle)
- **60-79**: 🔵 Good (Blue circle)
- **40-59**: 🟡 Fair (Yellow circle)
- **0-39**: 🔴 Poor (Red circle)

---

## 🖱️ Interactive Elements

### Clickable Items
- **Cards**: Click to select/view details
- **Table Rows**: Hover for highlight effect
- **Badges**: Visual indicators (not clickable)
- **Buttons**: 
  - Primary (blue): Main actions
  - Outline (white): Secondary actions
  - Danger (red): Delete actions

### Hover Effects
- **Cards**: Border color changes, shadow appears
- **Table Rows**: Background lightens
- **Buttons**: Background color darkens slightly

---

## 📱 Responsive Design

### Desktop (1920x1080)
- Full multi-column layout
- 6 stats cards in Overview
- Tables show all columns

### Tablet (768x1024)
- 3-column grid for cards
- Tables scroll horizontally
- Compact spacing

### Mobile (375x667)
- Single column layout
- Cards stack vertically
- Tables scroll horizontally
- Mobile menu (hamburger)

---

## ⌨️ Keyboard Shortcuts

- **Tab**: Navigate between elements
- **Enter**: Click buttons/links
- **Esc**: Close modals
- **Ctrl/Cmd + R**: Refresh page

---

## 🎯 Testing Checklist

### ✅ Things to Try

**Navigation:**
- [ ] Login with different roles
- [ ] Switch between tabs
- [ ] Click vehicle cards to select
- [ ] Open/close modals

**Visual Elements:**
- [ ] Check color-coded badges
- [ ] View health score circles
- [ ] Inspect progress bars
- [ ] Read tooltips (hover over elements)

**Responsive:**
- [ ] Resize browser window
- [ ] Test on mobile device
- [ ] Check horizontal scrolling on tables

**Interactions:**
- [ ] Hover over table rows
- [ ] Click buttons (see states)
- [ ] Select dropdown options
- [ ] Read empty state messages

---

## 💡 Pro Tips

1. **Use Chrome DevTools** (F12): Inspect elements, check console
2. **Check Network Tab**: See API calls (when backend runs)
3. **Use "Quick Login"**: Fastest way to test different roles
4. **Try Mobile View**: Chrome DevTools → Toggle device toolbar (Ctrl+Shift+M)
5. **Read Empty States**: They guide what data is needed

---

## 🎬 Demo Script

**5-Minute Demo Flow:**

1. **Open**: http://localhost:3000
2. **Login**: Click "Mechanic" quick login
3. **View**: Dashboard stats and metrics
4. **Explore**: Scroll through diagnoses table
5. **Click**: "View Details" on a diagnosis
6. **Read**: ML prediction, RAG context, repair guide
7. **Close**: Modal
8. **Logout**: Top-right corner
9. **Login**: As "Admin"
10. **Navigate**: Through all 4 tabs
11. **Logout & Login**: As "Manager"
12. **Explore**: Showroom tabs
13. **Logout & Login**: As "Owner"
14. **View**: Vehicle health cards
15. **Done**: You've seen everything!

---

**Enjoy the visual tour of AutoSense AI!** 🚀

Frontend is running at: **http://localhost:3000**
