import obspy
import numpy as np
from obspy.geodetics import gps2dist_azimuth, kilometer2degrees


# Input file
xml_ml = ["TNTI.xml", "TOLI2.xml", "LUWI.xml"]
mseed_ml = ["TNTI.mseed", "TOLI2.mseed", "LUWI.mseed"]

xml_msmb = ["THERA.xml", "SALTA.xml", "MARCO.xml"]
mseed_msmb = ["THERA.mseed", "SALTA.mseed", "MARCO.mseed"]

# Load Info Stasiun
def load_station_info(xml_file):
    inv = obspy.read_inventory(xml_file)
    sta = inv[0][0]
    return sta.latitude, sta.longitude

# Ambil Amplitudo
def load_waveform_amplitude(mseed_file, freqmin=None, freqmax=None, use_wood_anderson=False):

    st = obspy.read(mseed_file)
    tr = st[0]
    tr.detrend("linear")

    if freqmin and freqmax:
        tr.filter("bandpass", freqmin=freqmin, freqmax=freqmax)

    if use_wood_anderson:
        tr = apply_wood_anderson(tr)

    return np.max(np.abs(tr.data))

# Hitung jarak R & Δ
def compute_distance(ev_lat, ev_lon, sta_lat, sta_lon):
    d_m, _, _ = gps2dist_azimuth(ev_lat, ev_lon, sta_lat, sta_lon)
    R = d_m / 1000.0
    Δ = kilometer2degrees(R)
    return R, Δ

# Simulasi Wood-Anderson
def apply_wood_anderson(trace):

    paz_wa = {
        'poles': [-6.2832 + 4.7124j, -6.2832 - 4.7124j],
        'zeros': [0j],
        'gain': 2080,
        'sensitivity': 0.1
    }

    tr = trace.copy()
    tr.simulate(paz_remove=None, paz_simulate=paz_wa)
    return tr

# Rumus Ml, Ms, mB
def calc_ml(A, R):
    return np.log10(A) + 1.11 * np.log10(R) + 0.00189 * R - 2.09

def calc_ms(Vmax, Δ):
    return np.log10(Vmax / (2 * np.pi)) + 1.66 * np.log(Δ) + 0.3

def calc_mb(Vmax, Δ, h):
    Q = 1.8 * np.log(Δ + 1) + 0.003 * h
    return np.log10(Vmax / (2 * np.pi)) + Q - 3.0

# Proses Ml
def process_ml(xml_list, mseed_list, ev_lat, ev_lon, ev_depth):

    results = []

    for xml_file, mseed_file in zip(xml_list, mseed_list):

        sta_lat, sta_lon = load_station_info(xml_file)
        R, Δ = compute_distance(ev_lat, ev_lon, sta_lat, sta_lon)

        A = load_waveform_amplitude(
            mseed_file, freqmin=0.01, freqmax=0.02,
            use_wood_anderson=True
        )

        ML = calc_ml(A, R)
        results.append(ML)

    return results, np.mean(results)

# Proses Ms & mB
def process_ms_mb(xml_list, mseed_list, ev_lat, ev_lon, ev_depth):

    MS_results = []
    MB_results = []

    for xml_file, mseed_file in zip(xml_list, mseed_list):

        sta_lat, sta_lon = load_station_info(xml_file)
        R, Δ = compute_distance(ev_lat, ev_lon, sta_lat, sta_lon)

        V_ms = load_waveform_amplitude(mseed_file, freqmin=0.0001, freqmax=0.0005)
        MS = calc_ms(V_ms, Δ)

        V_mb = load_waveform_amplitude(mseed_file, freqmin=0.05, freqmax=5)
        MB = calc_mb(V_mb, Δ, ev_depth)

        MS_results.append(MS)
        MB_results.append(MB)

    return MS_results, MB_results, np.mean(MS_results), np.mean(MB_results)
