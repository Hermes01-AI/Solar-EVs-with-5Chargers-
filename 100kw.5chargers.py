
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SOLAR-POWERED EV CHARGING STATION  ·  5-CHARGER UPGRADED SYSTEM           ║
║  Engineer : Hermes MUGISHA  ·  Energy Engineer                               ║
║  Project  : Solar Powered EVs Charging Station — Rwanda E-Mobility 2026     ║
║─────────────────────────────────────────────────────────────────────────────║
║  ENERGY FLOW (LEFT → RIGHT):                                                 ║
║  SUN → PV ARRAY (182×550W=100kWp) → COMBINER → MPPT → INVERTER (100kW)    ║
║                         ↕ BATTERY (LFP 800V/300Ah = 240kWh)                ║
║  INVERTER → SMART METER → DISTRIBUTION BOARD → 5 CHARGERS → 5 EVs          ║
║─────────────────────────────────────────────────────────────────────────────║
║  PV Array  : 182× Jinko Tiger Neo 550W = 100.1 kWp                          ║
║              11 strings × 16 modules  Vmpp=663.2V  Impp=145.97A             ║
║  Battery   : LFP 800V/300Ah=240kWh  Buffer: 08-10h & 17-20h                ║
║  MPPT      : 100 kW  ·  3-channel  ·  Eff=98.5%                             ║
║  Inverter  : On-Grid 3-Phase 100kW  400V/50Hz  Eff=97.5%                   ║
║  DB Panel  : MCCB 350A + MCB 40A×2 + MCB 63A×2 + MCB 120A×1               ║
║  CH-1 & 2  : 1-Phase  7kW   32A  230V  IEC 62196 Type 2                    ║
║  CH-3 & 4  : 3-Phase  22kW  63A  400V  IEC 62196 Type 2                    ║
║  CH-5      : 3-Phase  40kW  100A 400V  IEC 62196 Type 2                    ║
║  Peak Load : 98 kW  (all 5 chargers active)                                  ║
║─────────────────────────────────────────────────────────────────────────────║
║  HOW TO RUN:                                                                 ║
║    pip install matplotlib numpy                                               ║
║    python solar_ev_5charger_system.py                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ── Backend selection: TkAgg for interactive; fall back to Agg if no display ──
import matplotlib
try:
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    plt.figure()
    plt.close()
except Exception:
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

import matplotlib.patches   as mpatches
import matplotlib.patheffects as pe
import numpy                as np
from matplotlib.patches    import FancyBboxPatch, Arc
from matplotlib.animation  import FuncAnimation
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  SYSTEM CONSTANTS
# ══════════════════════════════════════════════════════════════
NUM_MODULES   = 182
MOD_POWER_W   = 550
PV_KWP        = NUM_MODULES * MOD_POWER_W / 1000    # 100.1 kWp
PV_VMPP_MOD   = 41.45                               # V per module
PV_IMPP_MOD   = 13.27                               # A per string
MODS_PER_STR  = 16
NUM_STRINGS   = 11
STR_VMPP      = PV_VMPP_MOD * MODS_PER_STR          # 663.2 V
STR_IMPP      = PV_IMPP_MOD                         # 13.27 A per string
ARR_VMPP      = STR_VMPP                             # 663.2 V
ARR_IMPP      = STR_IMPP * NUM_STRINGS               # 145.97 A
ARR_KW        = PV_KWP                               # 100.1 kW

BAT_V         = 800
BAT_AH        = 300
BAT_KWH       = BAT_V * BAT_AH / 1000               # 240 kWh
BAT_SOC       = 78

MPPT_EFF      = 0.985
INV_KW        = 100
INV_EFF       = 0.975
AC_V3         = 400
AC_V1         = 230
AC_HZ         = 50
INV_IOUT      = INV_KW * 1000 / (np.sqrt(3) * AC_V3)  # 144.3 A

MCCB_A        = 350
MCB_A         = [40, 40, 63, 63, 120]

# 5 Chargers
CHARGERS = [
    {"id":1,"phase":"1-Phase","kw": 7,"V":230,"A": 32,"mcb": 40,
     "status":"Charging","soc":65.0,"ev":"EV-A","col":"#0d3b7a"},
    {"id":2,"phase":"1-Phase","kw": 7,"V":230,"A": 32,"mcb": 40,
     "status":"Charging","soc":65.0,"ev":"EV-B","col":"#4a1080"},
    {"id":3,"phase":"3-Phase","kw":22,"V":400,"A": 63,"mcb": 63,
     "status":"Charging","soc":85.0,"ev":"EV-C","col":"#14451a"},
    {"id":4,"phase":"3-Phase","kw":22,"V":400,"A": 63,"mcb": 63,
     "status":"Charging","soc":85.0,"ev":"EV-D","col":"#7a1a05"},
    {"id":5,"phase":"3-Phase","kw":40,"V":400,"A":100,"mcb":120,
     "status":"Charging","soc":90.0,"ev":"EV-E","col":"#5a0a3a"},
]
TOTAL_LOAD = sum(c["kw"] for c in CHARGERS if c["status"] == "Charging")
PEAK_LOAD  = sum(c["kw"] for c in CHARGERS)

# ══════════════════════════════════════════════════════════════
#  CANVAS
# ══════════════════════════════════════════════════════════════
W, H = 46, 18
fig  = plt.figure(figsize=(W, H), facecolor='#060d1a')
fig.patch.set_facecolor('#060d1a')
ax   = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_facecolor('#060d1a')
ax.axis('off')
try:
    fig.canvas.manager.set_window_title(
        "Solar EV Station — 5 Chargers — 100.1kWp — Rwanda E-Mobility 2026 — Eng. Hermes MUGISHA")
except Exception:
    pass

# Sky gradient
for i in range(180):
    t = i / 180
    r = int(6  + t * 16)
    g = int(13 + t * 22)
    b = int(26 + t * 50)
    ax.axhspan(i * H / 180, (i + 1) * H / 180,
               color=(r/255, g/255, b/255), zorder=0, alpha=0.72)

# Ground strip
ax.add_patch(mpatches.Rectangle((0, 0),   W, 1.55, color='#0d1f0d', zorder=1))
ax.add_patch(mpatches.Rectangle((0, 1.4), W, 0.40, color='#1a3a1a', zorder=1))

# Subtle grid
for gx in np.arange(0, W, 1.4):
    ax.plot([gx, gx], [0, H], color='#0e2040', lw=0.16, alpha=0.18, zorder=1)
for gy in np.arange(0, H, 1.4):
    ax.plot([0, W], [gy, gy], color='#0e2040', lw=0.16, alpha=0.18, zorder=1)

# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
def box(x, y, w, h, fc='#0d1f33', ec='#29b6f6', lw=2.0,
        r=0.15, z=8, a=1.0):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f'round,pad={r}',
                       facecolor=fc, edgecolor=ec,
                       linewidth=lw, zorder=z, alpha=a)
    ax.add_patch(p)
    return p

def txt(x, y, s, sz=7.0, c='#cfd8dc', ha='center', va='center',
        bold=False, mono=False, z=11, a=1.0):
    ax.text(x, y, s, ha=ha, va=va, fontsize=sz, color=c, alpha=a,
            fontweight='bold' if bold else 'normal', zorder=z,
            fontfamily='monospace' if mono else 'sans-serif')

def sbar(x, y, w, h, pct, z=12):
    ax.add_patch(mpatches.Rectangle((x, y), w, h, color='#1a1a2a', zorder=z))
    fc = '#00e676' if pct < 80 else ('#ffeb3b' if pct < 95 else '#f44336')
    ax.add_patch(mpatches.Rectangle((x, y), w * pct / 100, h, color=fc, zorder=z+1))
    ax.text(x + w/2, y + h/2, f'{pct:.0f}%', ha='center', va='center',
            fontsize=6.2, color='white', fontweight='bold',
            fontfamily='monospace', zorder=z+2)

def arrow(x0, y0, x1, y1, c='#ff9800', lw=2.5, z=8):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=c, lw=lw), zorder=z)

def biarrow(x0, y0, x1, y1, c='#4caf50', lw=2.5, z=8):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='<->', color=c, lw=lw), zorder=z)

def tag(x, y, s, fc='#1a0d00', c='#ffb74d', sz=6.2, z=9):
    ax.text(x, y, s, ha='center', va='center', fontsize=sz, color=c,
            fontweight='bold', zorder=z,
            bbox=dict(boxstyle='round,pad=0.18', facecolor=fc,
                      alpha=0.90, edgecolor='none'))

# ══════════════════════════════════════════════════════════════
#  1.  SUN
# ══════════════════════════════════════════════════════════════
SX, SY = 1.20, 12.80
ax.add_patch(plt.Circle((SX, SY), 0.70, color='#FFD700', zorder=6))
ax.add_patch(plt.Circle((SX, SY), 0.92, color='#FFD700', alpha=0.20, zorder=5))
ax.add_patch(plt.Circle((SX, SY), 1.15, color='#FFD700', alpha=0.07, zorder=4))
sun_glow = plt.Circle((SX, SY), 0.92, color='#FFD700', alpha=0.18, zorder=5)
ax.add_patch(sun_glow)
for ang in np.linspace(0, 360, 18, endpoint=False):
    r = np.radians(ang)
    ax.plot([SX + 1.00*np.cos(r), SX + 1.42*np.cos(r)],
            [SY + 1.00*np.sin(r), SY + 1.42*np.sin(r)],
            color='#FFD700', lw=2.2, zorder=6, alpha=0.82)
ax.text(SX, SY, '☀', ha='center', va='center',
        fontsize=14, color='#FF6F00', fontweight='bold', zorder=7)
for dy, s, c, bold in [
    (-1.55, 'SOLAR IRRADIANCE',       '#FFD700', True ),
    (-1.88, '1000 W/m²  |  AM1.5',   '#FFA000', False),
    (-2.16, 'Temp: 25°C (STC)',       '#FFB300', False),
    (-2.44, f'Peak: {PV_KWP:.1f} kWp','#ffcc02', True ),
]:
    ax.text(SX, SY + dy, s, ha='center',
            fontsize=6.8 if bold else 6.0, color=c,
            fontweight='bold' if bold else 'normal', zorder=7)

# ══════════════════════════════════════════════════════════════
#  2.  PV ARRAY
# ══════════════════════════════════════════════════════════════
PV_X, PV_Y  = 2.60, 5.60
PMW, PMH    = 0.84, 0.58
GAPC, GAPR  = 0.06, 0.06
COLS, ROWS  = 8, 11

pv_patches = []
for row in range(ROWS):
    for col in range(COLS):
        px = PV_X + col * (PMW + GAPC)
        py = PV_Y + row * (PMH + GAPR)
        p  = ax.add_patch(mpatches.Rectangle(
               (px, py), PMW, PMH,
               facecolor='#1a237e', edgecolor='#42a5f5',
               linewidth=1.0, zorder=8))
        pv_patches.append(p)
        for ci in range(3):
            for ri in range(2):
                ax.add_patch(mpatches.Rectangle(
                    (px + 0.04 + ci*0.255, py + 0.05 + ri*0.22),
                    0.21, 0.17,
                    facecolor='#283593', edgecolor='#5c6bc0',
                    linewidth=0.22, zorder=9))
        ax.text(px + PMW/2, py + PMH - 0.10, 'JINKO',
                ha='center', fontsize=3.8, color='#90caf9',
                fontweight='bold', zorder=10)
        ax.text(px + PMW/2, py + 0.08, '550W',
                ha='center', fontsize=3.6, color='#64b5f6', zorder=10)
    py_r = PV_Y + row * (PMH + GAPR)
    ax.text(PV_X - 0.32, py_r + PMH/2, f'S{row+1}',
            ha='center', va='center', fontsize=6.0,
            color='#ff9800', fontweight='bold', zorder=11)

# Mounting poles
for col in range(COLS):
    px = PV_X + col * (PMW + GAPC) + PMW/2
    ax.plot([px, px - 0.10], [PV_Y, PV_Y - 0.50], color='#757575', lw=1.8, zorder=7)
    ax.plot([px - 0.10, px - 0.10], [PV_Y - 0.50, 1.65], color='#616161', lw=1.4, zorder=7)

# Irradiance arrows
for col in [1, 4, 6]:
    for row in [2, 6, 9]:
        if row < ROWS:
            sx = PV_X + col * (PMW + GAPC) + PMW/2
            sy = PV_Y + row * (PMH + GAPR) + PMH
            ax.annotate('', xy=(sx - 0.05, sy + 0.10),
                        xytext=(sx - 0.52, sy + 0.72),
                        arrowprops=dict(arrowstyle='->', color='#FFD700',
                                        lw=1.4, alpha=0.68), zorder=8)

# PV title box
PV_RIGHT  = PV_X + COLS * (PMW + GAPC)
PV_TOP_Y  = PV_Y + ROWS * (PMH + GAPR) + 0.10
PV_TITLE_W = COLS * (PMW + GAPC) + 0.28
box(PV_X - 0.38, PV_TOP_Y, PV_TITLE_W, 1.00,
    fc='#0d1f33', ec='#42a5f5', lw=1.5, z=10)
txt(PV_X + COLS*(PMW+GAPC)/2 - 0.05, PV_TOP_Y + 0.68,
    f'JINKO TIGER NEO  ·  {PV_KWP:.1f} kWp  SOLAR PV ARRAY',
    sz=9.5, c='#42a5f5', bold=True, z=11)
txt(PV_X + COLS*(PMW+GAPC)/2 - 0.05, PV_TOP_Y + 0.30,
    f'{NUM_MODULES} Mods  ·  {NUM_STRINGS} Strings×{MODS_PER_STR}  ·  '
    f'Vmpp={ARR_VMPP:.1f}V  ·  Impp={ARR_IMPP:.1f}A  ·  Pmpp={ARR_KW:.1f}kW',
    sz=7.0, c='#90caf9', mono=True, z=11)

# ══════════════════════════════════════════════════════════════
#  3.  STRING COMBINER / DC DISCONNECT
# ══════════════════════════════════════════════════════════════
CB_X, CB_Y = PV_RIGHT + 1.20, 6.10
CB_W, CB_H = 2.10, 5.60

box(CB_X, CB_Y, CB_W, CB_H, fc='#111f11', ec='#4caf50', lw=2.2, z=9)
txt(CB_X + CB_W/2, CB_Y + CB_H + 0.22, 'STRING COMBINER',
    sz=8.5, c='#4caf50', bold=True, z=10)
txt(CB_X + CB_W/2, CB_Y + CB_H - 0.20, '+ DC DISCONNECT',
    sz=7.2, c='#81c784', z=10)

FSTEP = (CB_H - 0.50) / NUM_STRINGS
for si in range(NUM_STRINGS):
    fy = CB_Y + 0.26 + si * FSTEP
    ax.add_patch(mpatches.Rectangle((CB_X + 0.14, fy), 0.54, 0.24,
                 facecolor='#1b5e20', edgecolor='#4caf50', lw=0.7, zorder=11))
    ax.text(CB_X + 0.41, fy + 0.12, f'F{si+1}  15A',
            ha='center', va='center', fontsize=4.6,
            color='#a5d6a7', fontfamily='monospace', zorder=12)
    ax.add_patch(plt.Circle((CB_X + 1.84, fy + 0.12), 0.066,
                 color='#00e676', zorder=12))
txt(CB_X + CB_W/2, CB_Y + 0.14,
    f'DC  {ARR_VMPP:.1f}V  /  {ARR_IMPP:.1f}A',
    sz=6.5, c='#c8e6c9', mono=True, z=11)

arrow(PV_RIGHT, PV_Y + ROWS*(PMH+GAPR)/2, CB_X, CB_Y + CB_H*0.55,
      c='#ff9800', lw=2.8)
tag((PV_RIGHT + CB_X)/2, PV_Y + ROWS*(PMH+GAPR)/2 + 0.30,
    f'DC  {ARR_VMPP:.0f}V / {ARR_IMPP:.0f}A  =  {ARR_KW:.0f}kW')

# ══════════════════════════════════════════════════════════════
#  4.  MPPT CHARGE CONTROLLER  100kW · 3-channel
# ══════════════════════════════════════════════════════════════
MX, MY = CB_X + CB_W + 1.10, 6.10
MW, MH = 2.20, 5.60

box(MX, MY, MW, MH, fc='#0d2233', ec='#29b6f6', lw=2.2, z=9)
txt(MX + MW/2, MY + MH + 0.22, 'MPPT SOLAR',
    sz=8.5, c='#29b6f6', bold=True, z=10)
txt(MX + MW/2, MY + MH - 0.20, 'CHARGE CONTROLLER  100 kW',
    sz=7.0, c='#81d4fa', z=10)

# LCD screen
ax.add_patch(mpatches.Rectangle((MX + 0.12, MY + 3.10), MW - 0.24, 2.18,
             facecolor='#001400', edgecolor='#2e7d32', lw=0.9, zorder=11))
mppt_lcd = []
for li, ln in enumerate([
    f'Vin : {ARR_VMPP:.1f} V',
    f'Iin : {ARR_IMPP:.1f} A',
    f'Pin : {ARR_KW:.1f} kW',
    f'Vout: {BAT_V} V  DC',
    f'Eff : {MPPT_EFF*100:.1f} %',
    f'IEC 62109 Cert.',
]):
    t = ax.text(MX + MW/2, MY + 5.02 - li*0.32, ln,
                ha='center', va='center', fontsize=5.8,
                color='#00ff41', fontfamily='monospace', zorder=12)
    mppt_lcd.append(t)

# 3 channel LEDs
for chi, (mc, ml) in enumerate([('#00e676','CH-1'),
                                  ('#00bcd4','CH-2'),
                                  ('#ffea00','CH-3')]):
    ax.add_patch(plt.Circle((MX + 0.34 + chi*0.66, MY + 2.80), 0.10,
                 color=mc, zorder=12))
    ax.text(MX + 0.34 + chi*0.66, MY + 2.62, ml,
            ha='center', fontsize=5.0, color=mc, zorder=12)

for li, ln in enumerate([
    f'3 MPPT × 33 kW  each',
    f'Max Input: 800V / 80A',
    f'Output: {BAT_V}V DC → Inverter',
    f'Eff: {MPPT_EFF*100:.1f}%  |  IEC 62109',
]):
    txt(MX + MW/2, MY + 2.26 - li*0.36, ln, sz=5.8, c='#80deea', mono=True, z=11)

arrow(CB_X + CB_W, CB_Y + CB_H/2, MX, MY + MH/2, c='#ff9800', lw=2.8)
tag((CB_X + CB_W + MX)/2, CB_Y + CB_H/2 + 0.28,
    f'DC  {ARR_VMPP:.0f}V / {ARR_IMPP:.0f}A')

# ══════════════════════════════════════════════════════════════
#  5.  BATTERY  LFP 800V/300Ah = 240kWh
# ══════════════════════════════════════════════════════════════
BX, BY = MX - 0.10, 1.82
BW, BH = MW + 0.20, 3.72

box(BX, BY, BW, BH, fc='#091a09', ec='#66bb6a', lw=2.2, z=9)
txt(BX + BW/2, BY + BH + 0.22, 'BATTERY ENERGY STORAGE',
    sz=8.5, c='#66bb6a', bold=True, z=10)
txt(BX + BW/2, BY + BH - 0.20,
    f'LFP  {BAT_V}V / {BAT_AH}Ah  =  {BAT_KWH:.0f} kWh',
    sz=7.0, c='#a5d6a7', z=10)

# 8 battery modules (2×4 grid)
BKW, BKH = 0.88, 0.58
bat_fills = []
for bi in range(8):
    bkc = bi % 2
    bkr = bi // 2
    bkx = BX + 0.18 + bkc * (BKW + 0.14)
    bky = BY + 0.24 + bkr * (BKH + 0.12)
    ax.add_patch(mpatches.Rectangle((bkx, bky), BKW, BKH,
                 facecolor='#1b5e20', edgecolor='#4caf50', lw=0.8, zorder=11))
    fill = ax.add_patch(mpatches.Rectangle((bkx + 0.03, bky + 0.03),
                        (BKW - 0.06) * BAT_SOC / 100, BKH - 0.06,
                        color='#43a047', zorder=12))
    bat_fills.append(fill)
    ax.text(bkx + BKW/2, bky + BKH/2, f'M{bi+1}  {BAT_V//8}V',
            ha='center', va='center', fontsize=5.0,
            color='white', fontweight='bold', zorder=13)
    ax.add_patch(mpatches.Rectangle((bkx + BKW - 0.09, bky + 0.16),
                 0.07, 0.27, color='#9e9e9e', zorder=13))

sbar(BX + 0.16, BY + BH - 0.52, BW - 0.32, 0.30, BAT_SOC, z=12)
bat_src_txt = ax.text(BX + BW/2, BY + 0.14,
                      '⏱  Buffer: 08:00–10:00h  &  17:00–20:00h',
                      ha='center', fontsize=6.5, color='#fff176',
                      fontweight='bold', zorder=11)

biarrow(MX + MW/2, MY, BX + BW/2, BY + BH, c='#66bb6a', lw=2.5)
tag(MX + MW/2 - 0.88, (MY + BY + BH)/2,
    f'{BAT_V}V DC\nCharge / Discharge',
    fc='#0a1f0a', c='#a5d6a7', sz=6.0)

# ══════════════════════════════════════════════════════════════
#  6.  ON-GRID 3-PHASE 100kW INVERTER
# ══════════════════════════════════════════════════════════════
IX, IY = MX + MW + 1.10, 3.90
IW, IH = 2.90, 7.60

box(IX, IY, IW, IH, fc='#150a2e', ec='#ce93d8', lw=2.5, z=9)
txt(IX + IW/2, IY + IH + 0.22, 'ON-GRID  INVERTER',
    sz=9.0, c='#ce93d8', bold=True, z=10)
txt(IX + IW/2, IY + IH - 0.20, '3-PHASE  ·  100 kW',
    sz=8.0, c='#e1bee7', bold=True, z=10)

# Display screen
ax.add_patch(mpatches.Rectangle((IX + 0.12, IY + 5.25), IW - 0.24, 2.10,
             facecolor='#0a0018', edgecolor='#7b1fa2', lw=1.0, zorder=11))
inv_lcd = []
for li, ln in enumerate([
    f'DC IN : {ARR_VMPP:.0f}V / {ARR_IMPP:.0f}A',
    f'P_in  : {ARR_KW:.1f} kW',
    f'AC OUT: {AC_V3}V / {AC_HZ}Hz',
    f'P_out : {ARR_KW*INV_EFF:.1f} kW',
    f'I_out : {INV_IOUT:.1f} A (3-Ph)',
    f'Eff   : {INV_EFF*100:.1f}%  THD<3%',
]):
    t = ax.text(IX + IW/2, IY + 7.08 - li*0.30, ln,
                ha='center', va='center', fontsize=5.8,
                color='#ce93d8', fontfamily='monospace', zorder=12)
    inv_lcd.append(t)

# 3-phase sine waves
t_s = np.linspace(0, 4*np.pi, 120)
xs  = IX + 0.18 + (IW - 0.36) * t_s / (4*np.pi)
for ph, clr in [(0, '#f44336'), (2*np.pi/3, '#ffeb3b'), (4*np.pi/3, '#2196f3')]:
    ax.plot(xs, IY + 4.88 + 0.36*np.sin(t_s + ph),
            color=clr, lw=1.3, zorder=12, alpha=0.92)
txt(IX + IW/2, IY + 4.38, '3-Phase AC  L1 / L2 / L3',
    sz=6.0, c='#b39ddb', z=12)

for si, ss in enumerate([
    f'Rated: {INV_KW}kW / {INV_KW/0.8:.0f}kVA',
    f'Input: DC 200–900 V',
    f'Output: 3Ph {AC_V3}V + 1Ph {AC_V1}V',
    f'MPPT: 3-ch  800V/80A',
    f'Prot.: IP65  |  IEC 62109',
    f'Cert.: CE / IEC 61727',
]):
    txt(IX + IW/2, IY + 3.90 - si*0.32, ss,
        sz=5.8, c='#d1c4e9', mono=True, z=11)

# Cooling fins
for fi in range(11):
    ax.add_patch(mpatches.Rectangle((IX - 0.26, IY + 0.28 + fi*0.62),
                 0.20, 0.50,
                 facecolor='#37474f', edgecolor='#546e7a', lw=0.4, zorder=10))

arrow(MX + MW, MY + MH/2, IX, IY + IH*0.60, c='#ff9800', lw=2.8)
tag((MX + MW + IX)/2, MY + MH/2 + 0.28,
    f'DC  {ARR_VMPP:.0f}V / {ARR_IMPP:.0f}A  =  {ARR_KW:.0f}kW')

biarrow(BX + BW, BY + BH*0.65, IX, IY + 0.88, c='#66bb6a', lw=2.5)
tag((BX + BW + IX)/2, BY + BH*0.65 + 0.28,
    f'{BAT_V}V  Backup / Grid-Charge',
    fc='#0a1f0a', c='#a5d6a7', sz=6.2)

# ══════════════════════════════════════════════════════════════
#  7.  SMART METER
# ══════════════════════════════════════════════════════════════
SMX, SMY = IX + IW + 1.00, 5.30
SMW, SMH = 2.50, 5.92

box(SMX, SMY, SMW, SMH, fc='#070f20', ec='#00e5ff', lw=2.5, r=0.18, z=12)

ax.add_patch(FancyBboxPatch((SMX, SMY + SMH - 0.82), SMW, 0.82,
             boxstyle='round,pad=0.12',
             facecolor='#005f6e', edgecolor='none', zorder=13))
txt(SMX + SMW/2, SMY + SMH - 0.40,
    '⚡  SMART METER  3Ph 100A',
    sz=8.5, c='white', bold=True, z=14)

SM_ROWS = [
    ('Solar PV',   '#FFD700', f'{ARR_KW:.1f} kW'),
    ('Batt. SoC',  '#00e676', f'{BAT_SOC} %'),
    ('Load',       '#ff7043', f'{TOTAL_LOAD} kW'),
    ('Volt 3Ph',   '#4fc3f7', f'{AC_V3} V'),
    ('Current',    '#80cbc4', f'{INV_IOUT:.1f} A'),
    ('Frequency',  '#ce93d8', '50.00 Hz'),
    ('Energy/Day', '#ffeb3b', '—— kWh'),
    ('Grid Status','#69f0ae', 'ON-GRID ✓'),
]
sm_texts = []
RH = 0.50
for ri, (lbl, lc, val) in enumerate(SM_ROWS):
    ry = SMY + SMH - 0.92 - (ri + 1) * RH
    if ry < SMY + 0.95:
        break
    rc = '#0d1a30' if ri % 2 == 0 else '#0a1424'
    ax.add_patch(mpatches.Rectangle((SMX + 0.08, ry + 0.04),
                 SMW - 0.16, RH - 0.07, facecolor=rc, zorder=13))
    ax.add_patch(mpatches.Rectangle((SMX + 0.08, ry + 0.04),
                 0.12, RH - 0.07, facecolor=lc, zorder=14))
    txt(SMX + 0.26, ry + RH/2, lbl, sz=6.8, c='#cfd8dc', ha='left', mono=True, z=14)
    t = ax.text(SMX + SMW - 0.14, ry + RH/2, val,
                ha='right', va='center', fontsize=7.8,
                color=lc, fontweight='bold',
                fontfamily='monospace', zorder=14)
    sm_texts.append(t)

# IoT strip
box(SMX + 0.10, SMY + 0.10, SMW - 0.20, 0.80,
    fc='#040c1e', ec='#29b6f6', lw=1.2, r=0.10, z=13)
wc2, wy2 = SMX + 0.96, SMY + 0.52
for ri2, r2 in enumerate([0.13, 0.23, 0.34]):
    ax.add_patch(Arc((wc2, wy2 - 0.04), r2*2, r2*2,
                 angle=0, theta1=22, theta2=158,
                 color='#29b6f6', lw=1.4 - ri2*0.3, zorder=14))
ax.add_patch(plt.Circle((wc2, wy2 - 0.04), 0.050, color='#29b6f6', zorder=15))
txt(SMX + 1.40, SMY + 0.52, 'IoT Connected', sz=7.0,
    c='#29b6f6', bold=True, ha='left', z=14)
txt(SMX + 2.16, SMY + 0.70, '☁ MQTT',
    sz=5.8, c='#80deea', bold=True, z=14)
txt(SMX + 2.16, SMY + 0.34, 'Modbus TCP',
    sz=5.6, c='#80deea', z=14)
iot_led = ax.add_patch(plt.Circle((SMX + SMW - 0.20, SMY + 0.52), 0.090,
                        color='#00e676', zorder=15))

arrow(IX + IW, IY + IH*0.58, SMX, SMY + SMH*0.54, c='#ce93d8', lw=3.0)
tag((IX + IW + SMX)/2, IY + IH*0.58 + 0.30,
    f'3Ph {AC_V3}V/{AC_HZ}Hz  ·  {ARR_KW*INV_EFF:.0f}kW',
    fc='#1a0033', c='#ce93d8', sz=6.5)

# ══════════════════════════════════════════════════════════════
#  8.  DISTRIBUTION BOARD
# ══════════════════════════════════════════════════════════════
MCB_ROW_H = 1.02
DBX, DBY  = SMX + SMW + 1.00, 4.50
DBW       = 2.64
DBH       = 1.30 + 5 * MCB_ROW_H + 0.32   # ≈ 6.72

box(DBX, DBY, DBW, DBH, fc='#141208', ec='#ffd600', lw=2.5, z=9)
txt(DBX + DBW/2, DBY + DBH + 0.22, 'DISTRIBUTION  BOARD',
    sz=9.0, c='#ffd600', bold=True, z=10)
txt(DBX + DBW/2, DBY + DBH - 0.20, 'AC BUS  ·  MCCB + MCB Breakers',
    sz=7.2, c='#fff176', z=10)

# MCCB main breaker
box(DBX + 0.14, DBY + DBH - 1.22, DBW - 0.28, 0.92,
    fc='#1a0000', ec='#f44336', lw=1.6, r=0.07, z=11)
txt(DBX + DBW/2, DBY + DBH - 0.80,
    f'MCCB  {MCCB_A}A  —  MAIN  (3Ph)',
    sz=7.5, c='#ef9a9a', bold=True, z=12)
txt(DBX + DBW/2, DBY + DBH - 1.06,
    'IEC 60947  |  Breaking Cap.: 36 kA',
    sz=5.8, c='#ef9a9a', mono=True, z=12)
ax.add_patch(FancyBboxPatch((DBX + DBW - 0.62, DBY + DBH - 1.06),
             0.42, 0.38, boxstyle='round,pad=0.03',
             facecolor='#1b5e20', edgecolor='#4caf50', lw=1.0, zorder=13))
txt(DBX + DBW - 0.41, DBY + DBH - 0.88, 'ON',
    sz=6.5, c='white', bold=True, z=14)

# AC Bus bar strip
ax.add_patch(mpatches.Rectangle((DBX + 0.12, DBY + 0.10), DBW - 0.24, 0.28,
             facecolor='#1a1a00', edgecolor='#ffd600', lw=0.8, zorder=11))
for bi, (bc, bl) in enumerate([('#f44336','L1'), ('#ffeb3b','L2'),
                                ('#2196f3','L3'), ('#78909c','N')]):
    bx2 = DBX + 0.18 + bi * 0.58
    ax.add_patch(mpatches.Rectangle((bx2, DBY + 0.12), 0.48, 0.18,
                 facecolor=bc, edgecolor='none', zorder=12, alpha=0.7))
    txt(bx2 + 0.24, DBY + 0.21, bl, sz=5.0, c='white', bold=True, z=13)

# 5 MCB rows
MCB_INFO = [
    ('MCB-1','CH-1  1Ph   7kW', '40A', '#4fc3f7', True,  '230V · 32A'),
    ('MCB-2','CH-2  1Ph   7kW', '40A', '#4fc3f7', True,  '230V · 32A'),
    ('MCB-3','CH-3  3Ph  22kW', '63A', '#ff7043', True,  '400V · 63A'),
    ('MCB-4','CH-4  3Ph  22kW', '63A', '#ff7043', True,  '400V · 63A'),
    ('MCB-5','CH-5  3Ph  40kW','120A', '#e040fb', True,  '400V · 100A'),
]
mcb_toggles = []
for mi, (mnm, mds, ma, mc, mon, mvl) in enumerate(MCB_INFO):
    my2 = DBY + DBH - 2.28 - mi * MCB_ROW_H
    box(DBX + 0.14, my2, DBW - 0.28, MCB_ROW_H - 0.08,
        fc='#141414', ec=mc, lw=1.2, r=0.07, z=11)
    txt(DBX + 0.32, my2 + MCB_ROW_H*0.72, mnm,
        sz=8.0, c=mc, bold=True, ha='left', z=12)
    txt(DBX + 0.32, my2 + MCB_ROW_H*0.46, mds,
        sz=6.2, c='#cfd8dc', ha='left', mono=True, z=12)
    txt(DBX + 0.32, my2 + MCB_ROW_H*0.20, mvl,
        sz=5.8, c='#90a4ae', ha='left', mono=True, z=12)
    txt(DBX + DBW - 0.42, my2 + MCB_ROW_H*0.46, ma,
        sz=6.5, c='white', bold=True, z=12)
    tog = ax.add_patch(FancyBboxPatch((DBX + DBW - 0.62, my2 + 0.26),
                       0.42, 0.42, boxstyle='round,pad=0.03',
                       facecolor='#1b5e20', edgecolor='#4caf50', lw=0.9, zorder=13))
    ton = ax.text(DBX + DBW - 0.41, my2 + 0.47, 'ON',
                  ha='center', va='center', fontsize=5.8,
                  color='white', fontweight='bold', zorder=14)
    mcb_toggles.append((tog, ton))

arrow(SMX + SMW, SMY + SMH*0.52, DBX, DBY + DBH*0.52, c='#ce93d8', lw=3.0)
tag((SMX + SMW + DBX)/2, SMY + SMH*0.52 + 0.30,
    f'AC  {AC_V3}V / {AC_HZ}Hz',
    fc='#1a0033', c='#ce93d8', sz=6.5)

# ══════════════════════════════════════════════════════════════
#  9.  FIVE EV CHARGERS + CONNECTED EVs
# ══════════════════════════════════════════════════════════════
CH_X0  = DBX + DBW + 0.58
CH_GAP = 2.08
CH_Y   = 4.72
CH_W   = 1.80
CH_H   = 6.38
EV_Y   = 1.64
EV_H   = 1.00

CH_XS = [CH_X0 + ci * CH_GAP for ci in range(5)]

WIRE_COLS = ['#4fc3f7','#4fc3f7','#ff7043','#ff7043','#e040fb']
EV_COLS   = ['#0d3b7a','#4a1080','#14451a','#7a1a05','#5a0a3a']

ch_patches = []
ev_patches = []
ev_wheels  = []

for ci, ch in enumerate(CHARGERS):
    cx     = CH_XS[ci]
    is3ph  = ch["phase"] == "3-Phase"
    ec_col = '#e040fb' if ch["kw"] == 40 else ('#ff7043' if is3ph else '#29b6f6')
    on     = ch["status"] == "Charging"
    scr_c  = '#00ff88' if on else '#ff5252'

    # Charger body
    box(cx, CH_Y, CH_W, CH_H, fc='#080e1c', ec=ec_col, lw=2.2, z=9)

    # Phase / power badge
    ax.add_patch(FancyBboxPatch((cx + 0.06, CH_Y + CH_H - 0.58),
                 CH_W - 0.12, 0.46, boxstyle='round,pad=0.03',
                 facecolor='#bf360c' if is3ph else '#1a237e',
                 edgecolor=ec_col, lw=0.9, zorder=11))
    txt(cx + CH_W/2, CH_Y + CH_H - 0.36, ch["phase"],
        sz=7.0, c=ec_col, bold=True, z=12)

    # Screen
    scr = ax.add_patch(mpatches.Rectangle(
            (cx + 0.08, CH_Y + 3.48), CH_W - 0.16, 2.44,
            facecolor='#0a2a0a' if on else '#1a0000',
            edgecolor='#2e7d32' if on else '#7f0000',
            lw=0.9, zorder=11))
    s_stat = ax.text(cx + CH_W/2, CH_Y + 5.54,
                     'CHARGING' if on else 'STANDBY',
                     ha='center', fontsize=6.2, color=scr_c,
                     fontweight='bold', fontfamily='monospace', zorder=12)
    s_pwr = ax.text(cx + CH_W/2, CH_Y + 5.12,
                    f'P = {ch["kw"]:>2d} kW',
                    ha='center', fontsize=9.0,
                    color='#69f0ae' if on else '#ff8a80',
                    fontweight='bold', zorder=12)
    ax.text(cx + CH_W/2, CH_Y + 4.74, f'V = {ch["V"]} V',
            ha='center', fontsize=7.0, color=scr_c,
            fontfamily='monospace', zorder=12)
    ax.text(cx + CH_W/2, CH_Y + 4.42, f'I = {ch["A"]} A',
            ha='center', fontsize=7.0, color=scr_c,
            fontfamily='monospace', zorder=12)
    ax.text(cx + CH_W/2, CH_Y + 4.12, f'f = {AC_HZ} Hz',
            ha='center', fontsize=6.2, color=scr_c,
            fontfamily='monospace', zorder=12)
    ax.text(cx + CH_W/2, CH_Y + 3.78, ch["ev"],
            ha='center', fontsize=6.2, color='#b2dfdb',
            fontfamily='monospace', zorder=12)

    # SoC bar
    ax.add_patch(mpatches.Rectangle((cx + 0.10, CH_Y + 3.20),
                 CH_W - 0.20, 0.26, color='#1a1a2a', zorder=12))
    s_soc = ax.add_patch(mpatches.Rectangle(
                (cx + 0.10, CH_Y + 3.20),
                (CH_W - 0.20) * ch["soc"] / 100, 0.26,
                color='#00e676', zorder=13))
    s_slbl = ax.text(cx + CH_W/2, CH_Y + 3.33, f'{ch["soc"]:.0f}%  SoC',
                     ha='center', va='center', fontsize=5.8,
                     color='white', fontweight='bold', zorder=14)

    # IEC 62196 Type 2 connector
    ax.add_patch(plt.Circle((cx + CH_W/2, CH_Y + 2.66), 0.36,
                 facecolor='#1a1a1a', edgecolor=ec_col, lw=1.8, zorder=11))
    ax.add_patch(plt.Circle((cx + CH_W/2, CH_Y + 2.66), 0.24,
                 facecolor='#212121', zorder=12))
    for pox, poy in [(-0.11, 0.09),(0.11, 0.09),(0, -0.10),
                     (-0.15,-0.02),(0.15,-0.02),(0, 0.00)]:
        ax.add_patch(plt.Circle((cx + CH_W/2 + pox, CH_Y + 2.66 + poy),
                     0.038, color='#bdbdbd', zorder=13))
    txt(cx + CH_W/2, CH_Y + 2.18, 'IEC 62196', sz=5.2, c='#78909c', z=12)
    txt(cx + CH_W/2, CH_Y + 1.94, 'Type  2',   sz=5.2, c='#78909c', z=12)

    # RFID / NFC pad
    ax.add_patch(FancyBboxPatch((cx + 0.10, CH_Y + 0.38),
                 CH_W - 0.20, 0.86, boxstyle='round,pad=0.04',
                 facecolor='#1a237e', edgecolor='#5c6bc0', lw=0.8, zorder=11))
    txt(cx + CH_W/2, CH_Y + 0.90, 'RFID / NFC',    sz=5.8, c='#9fa8da', z=12)
    txt(cx + CH_W/2, CH_Y + 0.62, 'TAP  TO  START', sz=5.0, c='#7986cb', z=12)

    # Labels below/above charger
    txt(cx + CH_W/2, CH_Y - 0.28,
        f'CH-{ch["id"]}  ·  {ch["kw"]} kW',
        sz=8.5, c=ec_col, bold=True, z=10)
    txt(cx + CH_W/2, CH_Y - 0.54,
        f'{ch["phase"]}  ·  {ch["V"]}V  ·  {ch["A"]}A',
        sz=6.5, c='#b0bec5', z=10)
    txt(cx + CH_W/2, CH_Y + CH_H + 0.16,
        f'{ch["V"]}V · {ch["A"]}A · MCB {ch["mcb"]}A',
        sz=6.0, c=WIRE_COLS[ci], z=9)

    # EV Car body
    ecol  = EV_COLS[ci]
    ev_b  = ax.add_patch(FancyBboxPatch(
              (cx - 0.06, EV_Y + 0.42), CH_W + 0.12, EV_H,
              boxstyle='round,pad=0.08',
              facecolor=ecol, edgecolor='#b0bec5', lw=1.2, zorder=9))
    ev_r  = ax.add_patch(FancyBboxPatch(
              (cx + 0.14, EV_Y + 0.84), CH_W - 0.28, 0.52,
              boxstyle='round,pad=0.06',
              facecolor=ecol, edgecolor='#b0bec5', lw=0.9, zorder=10))
    ev_patches.append((ev_b, ev_r))

    # Windshields
    for wx_off in [0.16, 0.82]:
        ax.add_patch(FancyBboxPatch((cx + wx_off, EV_Y + 0.88),
                     0.44, 0.36, boxstyle='round,pad=0.03',
                     facecolor='#b3e5fc', edgecolor='#0288d1',
                     lw=0.5, zorder=11))

    # Headlights
    for hx_off in [-0.04, 1.46]:
        ax.add_patch(FancyBboxPatch((cx + hx_off, EV_Y + 0.62),
                     0.12, 0.30, boxstyle='round,pad=0.02',
                     facecolor='#fff9c4', edgecolor='#fdd835', lw=0.5, zorder=11))

    # Wheels (animated)
    whl_row = []
    for wx_off in [0.20, 1.26]:
        out_c = ax.add_patch(plt.Circle((cx + wx_off, EV_Y + 0.38), 0.24,
                             facecolor='#212121', edgecolor='#616161',
                             lw=0.9, zorder=11))
        inn_c = ax.add_patch(plt.Circle((cx + wx_off, EV_Y + 0.38), 0.10,
                             facecolor='#424242', zorder=12))
        spokes = []
        for sang in [0, 60, 120]:
            sr = np.radians(sang)
            sp = ax.plot([cx + wx_off, cx + wx_off + 0.10*np.cos(sr)],
                         [EV_Y + 0.38,  EV_Y + 0.38 + 0.10*np.sin(sr)],
                         color='#757575', lw=0.7, zorder=12)[0]
            spokes.append(sp)
        whl_row.append((out_c, inn_c, spokes, cx + wx_off, EV_Y + 0.38))
    ev_wheels.append(whl_row)

    # Charge port LED
    led = ax.add_patch(plt.Circle((cx + CH_W/2, EV_Y + 0.66), 0.11,
                       color='#00e5ff' if on else '#37474f', zorder=12))
    ax.text(cx + CH_W/2, EV_Y + 0.66, ch["ev"],
            ha='center', va='center', fontsize=4.8,
            color='white', fontweight='bold', zorder=13)

    # EV SoC bar
    ax.add_patch(mpatches.Rectangle((cx + 0.02, EV_Y + 0.04),
                 CH_W - 0.04, 0.20, color='#1a1a2a', zorder=9))
    ev_soc_f = ax.add_patch(mpatches.Rectangle(
                   (cx + 0.02, EV_Y + 0.04),
                   (CH_W - 0.04) * ch["soc"] / 100, 0.20,
                   color='#22c55e', zorder=10))

    # Charging cable
    ax.plot([cx + CH_W/2, cx + CH_W/2], [CH_Y, EV_Y + EV_H + 0.44],
            color=ec_col, lw=1.6, ls='--', zorder=8, alpha=0.75)

    ch_patches.append((scr, s_stat, s_pwr, s_soc, s_slbl, led, ev_soc_f))

# DB → Charger wiring
for ci, ch in enumerate(CHARGERS):
    cx = CH_XS[ci]
    wc = WIRE_COLS[ci]
    db_y = DBY + DBH
    ax.plot([DBX + DBW*0.35 + (5 - ci)*0.26,
             DBX + DBW*0.35 + (5 - ci)*0.26,
             cx + CH_W/2,
             cx + CH_W/2],
            [db_y,
             db_y + (ci + 3)*0.26,
             db_y + (ci + 3)*0.26,
             db_y + 0.02],
            color=wc, lw=2.4, zorder=8,
            path_effects=[pe.Stroke(linewidth=3.8,
                          foreground='#000000', alpha=0.38),
                          pe.Normal()])

# ══════════════════════════════════════════════════════════════
#  10.  ENERGY FLOW PARTICLES
# ══════════════════════════════════════════════════════════════
FLOW_PATHS = [
    (PV_RIGHT,   PV_Y + ROWS*(PMH+GAPR)/2,
     CB_X,        CB_Y + CB_H*0.55,          '#ff9800', 0.013, 22),
    (CB_X + CB_W, CB_Y + CB_H/2,
     MX,           MY + MH/2,                '#e43232', 0.013, 12),
    (MX + MW,     MY + MH/2,
     IX,           IY + IH*0.58,             '#2f00ff', 0.016, 30),
    (BX + BW,     BY + BH*0.65,
     IX,           IY + 0.85,                '#d7d011', 0.011, 15),
    (MX + MW/2,   MY,
     BX + BW/2,   BY + BH,                   '#66bb6a', 0.012, 12),
    (IX + IW,     IY + IH*0.58,
     SMX,          SMY + SMH*0.54,           '#ce93d8', 0.017, 40),
    (SMX + SMW,   SMY + SMH*0.52,
     DBX,          DBY + DBH*0.52,           '#ffd600', 0.016, 35),
    (DBX + DBW,   DBY + DBH - 2.28 - 0*MCB_ROW_H + (MCB_ROW_H-0.08)/2,
     CH_XS[0] + CH_W/2, CH_Y + CH_H,        '#4fc3f7', 0.016, 16),
    (DBX + DBW,   DBY + DBH - 2.28 - 1*MCB_ROW_H + (MCB_ROW_H-0.08)/2,
     CH_XS[1] + CH_W/2, CH_Y + CH_H,        '#4fc3f7', 0.016, 16),
    (DBX + DBW,   DBY + DBH - 2.28 - 2*MCB_ROW_H + (MCB_ROW_H-0.08)/2,
     CH_XS[2] + CH_W/2, CH_Y + CH_H,        '#ff7043', 0.016, 30),
    (DBX + DBW,   DBY + DBH - 2.28 - 3*MCB_ROW_H + (MCB_ROW_H-0.08)/2,
     CH_XS[3] + CH_W/2, CH_Y + CH_H,        '#ff7043', 0.016, 15),
    (DBX + DBW,   DBY + DBH - 2.28 - 4*MCB_ROW_H + (MCB_ROW_H-0.08)/2,
     CH_XS[4] + CH_W/2, CH_Y + CH_H,        '#e040fb', 0.018, 40),
    (SMX + SMW*0.5, SMY + SMH,
     SMX + SMW*0.5, SMY + SMH + 0.90,        '#00e5ff', 0.020, 20),
]

N_PART         = 9
particles      = []
particle_state = []
for pi, (x0, y0, x1, y1, col, spd, sz) in enumerate(FLOW_PATHS):
    for ni in range(N_PART):
        sc = ax.scatter([], [], s=sz, color=col, zorder=20,
                        alpha=0.92, edgecolors='white', linewidths=0.26)
        particles.append(sc)
        particle_state.append({'t': ni / N_PART, 'path': pi})

# ══════════════════════════════════════════════════════════════
#  REAL-TIME ENERGY MANAGEMENT SYSTEM MODE
# ══════════════════════════════════════════════════════════════
def get_system_mode():
    now  = datetime.now()
    hour = now.hour + now.minute / 60
    t    = (hour - 8) % 24
    if   0  <= t < 2:  return "BATTERY_DISCHARGE"
    elif 2  <= t < 9:  return "SOLAR_DIRECT"
    elif 9  <= t < 12: return "BATTERY_DISCHARGE"
    elif 12 <= t < 15: return "GRID_STANDBY"
    elif 15 <= t < 20: return "GRID_CHARGING"
    else:              return "END"

# ══════════════════════════════════════════════════════════════
#  TIME INDICATOR  — defined BEFORE draw_daily_operational_schedule
# ══════════════════════════════════════════════════════════════
def draw_time_indicator(y, x0, total_w):
    now  = datetime.now()
    hour = now.hour + now.minute / 60
    t    = (hour - 8) % 24
    xt   = x0 + (t / 24) * total_w

    ax.plot([xt, xt], [y - 0.2, y + 0.8],
            color='#00e5ff', lw=2.5, zorder=50)
    txt(xt, y + 1.0,
        f'NOW: {now.strftime("%H:%M")}',
        sz=7, c='#00e5ff', bold=True, z=51)

# ══════════════════════════════════════════════════════════════
#  DAILY OPERATIONAL SCHEDULE
# ══════════════════════════════════════════════════════════════
def draw_daily_operational_schedule():
    y       = H - 5.2
    h       = 0.5
    x0      = 3.0
    total_w = W - 8.0

    txt(W/2, y + 1.2,
        'DAILY OPERATIONAL SCHEDULE — REAL-TIME CONTROL',
        sz=8, c='#ffd600', bold=True, z=60)

    def tx(t):
        return x0 + (t / 24.0) * total_w

    segments = [
        (8,   10,  '#1565c0', 'BAT'),
        (10,   15,  '#1b5e20', 'PV'),
        (15,  17,  '#311b92', 'BAT'),
        (17, 20,  '#263238', 'GRID'),
        (20, 22,  "#531705", 'GRID & CH BAT'),
        (22, 24,  '#212121', 'GRID'),
    ]
    for s, e, col, label in segments:
        xs = tx(s)
        xe = tx(e)
        box(xs, y, xe - xs, h,
            fc=col, ec='#90a4ae', lw=1.5, r=0.12, z=35)
        txt((xs + xe) / 2, y + h/2, label,
            sz=7, c='white', bold=True, z=36)

    # Timeline ticks
    times  = [0,  2,  9,  12, 15, 20, 24]
    labels = ['08:00','10:00','17:00','20:00','23:00','04:00','08:00']
    for t_val, lab in zip(times, labels):
        xt = tx(t_val)
        ax.plot([xt, xt], [y - 0.15, y],
                color='#ffd600', lw=1.2, zorder=36)
        txt(xt, y - 0.4, lab, sz=6.5, c='#ffd600', z=36)

    # Moving NOW indicator — safe to call because it's defined above
    draw_time_indicator(y, x0, total_w)

draw_daily_operational_schedule()

# ══════════════════════════════════════════════════════════════
#  11.  TITLE BANNER
# ══════════════════════════════════════════════════════════════
box(0.18, H - 1.88, W - 0.36, 1.72, fc='#060d1a', ec='#f59e0b', lw=2.4, z=20, a=0.97)
ax.plot([0.18, W - 0.18], [H - 0.18, H - 0.18],
        color='#f59e0b', lw=3.2, alpha=0.85, zorder=21)
for xi, ci in zip(np.linspace(0.18, W - 0.18, 300),
                  [plt.cm.plasma(x) for x in np.linspace(0, 1, 300)]):
    ax.plot([xi, xi + (W - 0.36)/300], [H - 0.20, H - 0.20],
            color=ci, lw=2.5, alpha=0.7, zorder=22)

ax.text(W/2, H - 0.68,
        'SOLAR-POWERED EVs CHARGING STATION  ·  100.1 kWp  ·  100 kW ON-GRID  ·  '
        'IoT SMART METER  ·  5 CHARGERS  ·  ANIMATED ENERGY FLOW',
        ha='center', fontsize=13.5, color='white',
        fontweight='bold', zorder=21)
ax.text(W/2, H - 1.14,
        f'Jinko Tiger Neo 550W · {NUM_MODULES}Mod / {PV_KWP:.0f}kWp  ·  '
        f'LFP {BAT_KWH:.0f}kWh  ·  100kW On-Grid Inverter  ·  '
        f'2×7kW(1Ph) + 2×22kW(3Ph) + 1×40kW(3Ph)  ·  '
        f'Peak={PEAK_LOAD}kW  ·  Rwanda E-Mobility 2026',
        ha='center', fontsize=9.0, color='#4fc3f7', zorder=21)
ax.text(W/2, H - 1.55,
        f'📍 Nyamagabe District, Rwanda  ·  GHI=1752kWh/m²/yr  ·  PSH=4.8h/day  '
        f'·  Engineer: Hermes MUGISHA  ·  Energy Engineer',
        ha='center', fontsize=7.8, color='#ffd600', zorder=21)

# ══════════════════════════════════════════════════════════════
#  12.  LIVE DATA PANEL
# ══════════════════════════════════════════════════════════════
box(0.20, H - 4.40, 3.40, 2.28, fc='#060d1a', ec='#4caf50', lw=1.8, z=20, a=0.95)
txt(1.90, H - 2.32, 'LIVE  DATA', sz=8.5, c='#4caf50', bold=True, z=21)
LD_LABELS = ['Irrad.','PV Out','Battery','Load','Efficiency']
LD_VALS   = ['1000W/m²', f'{ARR_KW:.1f}kW', f'{BAT_SOC}%',
             f'{TOTAL_LOAD}kW', '97.5%']
LD_COLS   = ['#FFD700','#ff9800','#66bb6a','#ce93d8','#80deea']
live_texts = []
for li, (ll, lv, lc) in enumerate(zip(LD_LABELS, LD_VALS, LD_COLS)):
    row  = li % 3
    col_ = li // 3
    lx   = 0.32 + col_*1.70
    ly   = H - 2.90 - row*0.48
    ax.text(lx, ly, ll + ':', fontsize=6.0, color='#90a4ae', va='center', zorder=21)
    t = ax.text(lx + 1.60, ly, lv, fontsize=7.0, color=lc,
                fontweight='bold', va='center', ha='right',
                fontfamily='monospace', zorder=21)
    live_texts.append(t)

# ══════════════════════════════════════════════════════════════
#  13.  LEGEND + SPECS FOOTER
# ══════════════════════════════════════════════════════════════
box(0.18, 0.04, W*0.54, 1.46, fc='#060d1a', ec='#37474f', lw=1, z=20, a=0.92)
LEG = [
    ('#ff9800','DC Flow  (PV → Combiner → MPPT → Inverter)'),
    ('#66bb6a','Battery  Charge / Discharge  (LFP 240 kWh)'),
    ('#ce93d8','AC Bus  (Inverter → Smart Meter → DB)'),
    ('#4fc3f7','1-Phase  230V / 32A / 7 kW  Charger (×2)'),
    ('#ff7043','3-Phase  400V / 63A / 22 kW  Charger (×2)'),
    ('#e040fb','3-Phase  400V / 100A / 40 kW  Charger (×1)'),
    ('#00e5ff','IoT  MQTT / Modbus TCP  Data Link'),
]
for li, (lc, lt) in enumerate(LEG):
    col_ = li % 4
    row  = li // 4
    lx   = 0.36 + col_*6.20
    ly   = 1.12 - row*0.56
    ax.plot([lx, lx + 0.50], [ly, ly], color=lc, lw=3.2, zorder=21)
    ax.add_patch(plt.Circle((lx + 0.25, ly), 0.08, color=lc, zorder=22))
    ax.text(lx + 0.68, ly, lt, fontsize=7.0, color='#cfd8dc', va='center', zorder=21)

box(W*0.54 + 0.28, 0.04, W*0.46 - 0.46, 1.46, fc='#060d1a', ec='#37474f', lw=1, z=20, a=0.92)
SPECS = [
    ('PV Array', f'{NUM_MODULES}×550W={PV_KWP:.0f}kWp  {NUM_STRINGS}str×{MODS_PER_STR}mod  '
                 f'Vmpp={ARR_VMPP:.0f}V  Impp={ARR_IMPP:.0f}A'),
    ('Battery',  f'LFP {BAT_V}V/{BAT_AH}Ah={BAT_KWH:.0f}kWh  SoC={BAT_SOC}%  '
                 f'Buffer: 08–10h & 17–20h'),
    ('MPPT',     f'100kW  3-ch×33kW  Eff={MPPT_EFF*100:.1f}%  Max 800V/80A  Out:{BAT_V}V DC'),
    ('Inverter', f'{INV_KW}kW On-Grid 3Ph  Eff={INV_EFF*100:.1f}%  '
                 f'{AC_V3}V/{AC_HZ}Hz  Iout={INV_IOUT:.0f}A'),
    ('DB Panel', f'MCCB {MCCB_A}A + MCB 40A×2 + 63A×2 + 120A×1  IEC 60947  36kA'),
    ('IoT/Meter',f'3Ph 100A  Modbus TCP+MQTT  IEC 62056  IEC 61851/62196'),
]
sx0 = W*0.54 + 0.48
for si, (sl, sv) in enumerate(SPECS):
    row  = si // 2
    col_ = si % 2
    sx   = sx0 + col_*9.8
    sy   = 1.18 - row*0.42
    ax.text(sx, sy, sl + ':', fontsize=6.2, color='#ffd600',
            fontweight='bold', va='center', zorder=21)
    ax.text(sx + 1.62, sy, sv, fontsize=5.8, color='#b0bec5',
            va='center', zorder=21)

# ══════════════════════════════════════════════════════════════
#  14.  ANIMATION
# ══════════════════════════════════════════════════════════════
def animate(frame):
    tg    = frame * 0.018
    noise = np.sin(tg * 0.70)
    n2    = np.sin(tg * 1.40 + 0.80)
    blink = 0.5 + 0.5 * np.sin(tg * 5.0)

    # Energy particles
    for scat, pst in zip(particles, particle_state):
        pi             = pst['path']
        x0,y0,x1,y1,col,spd,sz = FLOW_PATHS[pi]
        pst['t']       = (pst['t'] + spd) % 1.0
        t              = pst['t']
        wob            = 0.038 * np.sin(t * 6 * np.pi)
        dx             = x1 - x0
        dy             = y1 - y0
        dn             = max(abs(dx) + 0.001, 0.001)
        px             = x0 + t*dx + wob*(-dy/dn)
        py             = y0 + t*dy + wob*( dx/dn)
        scat.set_offsets([[px, py]])
        scat.set_alpha(float(0.5 + 0.5*np.sin(t*np.pi)) * 0.92)

    # Sun glow
    sun_glow.set_radius(0.90 + 0.18 * np.sin(tg * 2.5))
    sun_glow.set_alpha (0.14 + 0.09 * np.sin(tg * 2.5))

    # PV shimmer
    for i, pp in enumerate(pv_patches):
        sh = 0.90 + 0.10 * np.sin(tg*1.8 + i*0.28)
        pp.set_facecolor((26/255*sh, 35/255*sh, 126/255*sh))

    # Battery module fill
    soc_now = BAT_SOC + int(noise * 3)
    for bf in bat_fills:
        bf.set_width((BKW - 0.06) * soc_now / 100)
        bf.set_facecolor('#43a047' if soc_now > 30 else '#f44336')

    # Live data panel
    irr_live = int(1000 + noise * 18)
    pv_live  = ARR_KW  + noise * 0.8
    bat_live = BAT_SOC + int(noise * 3)
    ld_live  = TOTAL_LOAD + noise * 1.2
    live_texts[0].set_text(f'{irr_live} W/m²')
    live_texts[1].set_text(f'{pv_live:.1f} kW')
    live_texts[2].set_text(f'{bat_live} %')
    live_texts[3].set_text(f'{ld_live:.1f} kW')
    live_texts[4].set_text(f'{INV_EFF*100:.1f} %')

    # Smart Meter rows
    v_l  = AC_V3    + noise * 1.8
    i_l  = INV_IOUT + noise * 1.2
    f_l  = 50.0     + noise * 0.04
    e_l  = 520.0    + n2 * 5.0
    upd  = [f'{pv_live:.1f} kW',  f'{bat_live} %',
            f'{ld_live:.1f} kW',  f'{v_l:.0f} V',
            f'{i_l:.1f} A',        f'{f_l:.2f} Hz',
            f'{e_l:.0f} kWh',      'ON-GRID ✓']
    for ti, txt_ in enumerate(upd):
        if ti < len(sm_texts):
            sm_texts[ti].set_text(txt_)

    # MPPT LCD
    if mppt_lcd:
        mppt_lcd[1].set_text(f'Iin : {ARR_IMPP + noise*0.5:.1f} A')
        mppt_lcd[2].set_text(f'Pin : {pv_live:.1f} kW')

    # Inverter LCD
    if inv_lcd:
        inv_lcd[1].set_text(f'P_in  : {pv_live:.1f} kW')
        inv_lcd[3].set_text(f'P_out : {pv_live*INV_EFF:.1f} kW')
        inv_lcd[4].set_text(f'I_out : {i_l:.1f} A (3-Ph)')

    # IoT LED blink
    iot_led.set_alpha(0.35 + 0.65 * blink)

    # EV chargers + cars
    for ci, ch in enumerate(CHARGERS):
        cx     = CH_XS[ci]
        on     = ch["status"] == "Charging"
        scr_c  = '#00ff88' if on else '#ff5252'
        scr, s_stat, s_pwr, s_soc, s_slbl, led, ev_soc_f = ch_patches[ci]

        scr.set_facecolor('#0a2a0a' if on else '#1a0000')
        s_stat.set_text('CHARGING' if on else 'STANDBY')
        s_stat.set_color(scr_c)
        s_pwr.set_text(f'P = {ch["kw"]:>2d} kW' if on else 'P =  0 kW')
        s_pwr.set_color('#69f0ae' if on else '#ff8a80')

        if on and ch["soc"] < 100:
            ch["soc"] = min(100, ch["soc"] + 0.004)
        sc     = ch["soc"]
        soc_fc = '#00e676' if sc < 80 else ('#ffeb3b' if sc < 95 else '#f44336')
        s_soc.set_width((CH_W - 0.20) * sc / 100)
        s_soc.set_facecolor(soc_fc)
        s_slbl.set_text(f'{sc:.0f}%  SoC')
        ev_soc_f.set_width((CH_W - 0.04) * sc / 100)
        ev_soc_f.set_facecolor(soc_fc)

        tog, ton = mcb_toggles[ci]
        tog.set_facecolor('#1b5e20' if on else '#b71c1c')
        tog.set_edgecolor('#4caf50' if on else '#f44336')
        ton.set_text('ON' if on else 'OFF')

        if on:
            led.set_color('#00e5ff')
            led.set_alpha(0.50 + 0.50 * np.sin(tg*4.0 + ci*1.0))
        else:
            led.set_color('#37474f')
            led.set_alpha(0.50)

        bounce = 0.016 * np.sin(tg*3.0 + ci*0.9) if on else 0.0
        ev_b, ev_r = ev_patches[ci]
        ev_b.set_y(EV_Y + 0.42 + bounce)
        ev_r.set_y(EV_Y + 0.84 + bounce)

        for out_c, inn_c, spokes, wx_, wy_ in ev_wheels[ci]:
            if on:
                out_c.center = (wx_, wy_ + bounce)
                inn_c.center = (wx_, wy_ + bounce)
                for si2, sp in enumerate(spokes):
                    ang2 = tg*2.2 + si2*2.094 + ci*0.5
                    sp.set_xdata([wx_, wx_ + 0.10*np.cos(ang2)])
                    sp.set_ydata([wy_ + bounce, wy_ + bounce + 0.10*np.sin(ang2)])
            else:
                out_c.center = (wx_, wy_)
                inn_c.center = (wx_, wy_)

    return (particles + [sun_glow] + pv_patches + bat_fills +
            live_texts + sm_texts + [iot_led])

# Keep reference to prevent garbage collection
anim = FuncAnimation(fig, animate, frames=None, interval=40, blit=False)

plt.tight_layout(pad=0)

# ══════════════════════════════════════════════════════════════
#  CONSOLE SUMMARY
# ══════════════════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════╗")
print("║  SOLAR-POWERED EV CHARGING STATION  —  5-CHARGER SYSTEM         ║")
print("║  Engineer  : Hermes MUGISHA  ·  Energy Engineer                 ║")
print("║  Project   : Rwanda E-Mobility 2026  ·  Nyamagabe District      ║")
print("╠══════════════════════════════════════════════════════════════════╣")
print(f"║  PV Array  : {NUM_MODULES}× Jinko Tiger Neo 550W = {PV_KWP:.1f} kWp           ║")
print(f"║  Strings   : {NUM_STRINGS} strings × {MODS_PER_STR} modules/string              ║")
print(f"║  DC Bus    : Vmpp={ARR_VMPP:.1f}V  Impp={ARR_IMPP:.1f}A  P={ARR_KW:.1f}kW        ║")
print(f"║  MPPT      : 100kW  3-channel  Eff=98.5%  Out:{BAT_V}V DC         ║")
print(f"║  Battery   : LFP {BAT_V}V/{BAT_AH}Ah = {BAT_KWH:.0f}kWh  SoC={BAT_SOC}%          ║")
print(f"║              Buffer: 08:00–10:00h  &  17:00–20:00h             ║")
print(f"║  Inverter  : On-Grid 3Ph {INV_KW}kW  Eff={INV_EFF*100:.1f}%  {AC_V3}V/{AC_HZ}Hz    ║")
print(f"║  Sm.Meter  : 3Ph 100A  Modbus TCP / MQTT IoT                   ║")
print(f"║  DB Panel  : MCCB {MCCB_A}A + MCB 40A×2 + 63A×2 + 120A×1          ║")
print(f"║  CH-1 & 2  : 1-Phase   7kW  32A  230V  IEC 62196 Type 2       ║")
print(f"║  CH-3 & 4  : 3-Phase  22kW  63A  400V  IEC 62196 Type 2       ║")
print(f"║  CH-5      : 3-Phase  40kW 100A  400V  IEC 62196 Type 2       ║")
print(f"║  Load      : Active={TOTAL_LOAD}kW  |  Peak={PEAK_LOAD}kW                  ║")
print("╠══════════════════════════════════════════════════════════════════╣")
print("║  ► Close window to exit.                                        ║")
print("╚══════════════════════════════════════════════════════════════════╝")

# Save static preview
plt.savefig('solar_ev_5charger_system.png', dpi=160,
            bbox_inches='tight', facecolor='#060d1a')
print("  ✔  Preview saved: solar_ev_5charger_system.png")

plt.show()