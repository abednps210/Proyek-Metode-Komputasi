import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import obspy

# Import fungsi kalkulasi
from Kalkulasi_Magnitudo import (
    process_ml,
    process_ms_mb,
    xml_ml, mseed_ml,
    xml_msmb, mseed_msmb
)

# Membuat Window Utama
ctk.set_appearance_mode("system")     
ctk.set_default_color_theme("dark-blue")   
root = ctk.CTk()
root.title("Kalkulasi Magnitudo")
root.geometry("1300x780")

# Tampilan Perhitungan
frame_left = ctk.CTkFrame(root, width=360)
frame_left.pack(side="left", fill="y", padx=10, pady=10)

label_info = ctk.CTkLabel(frame_left, text="Gempa Mindanao, Filipina\n10 Oktober 2025",
                           font=("Arial", 15, "bold"))
label_info.pack(pady=10)
label_info = ctk.CTkLabel(
    frame_left,
    text="Masukkan koordinat dan kedalaman gempa",
    font=("Arial", 12),
    anchor="w",
    justify="left"
)
label_info.pack(pady=6)

# Input Data Gempa
entry_lat = ctk.CTkEntry(frame_left, placeholder_text="Latitude", width=200)
entry_lon = ctk.CTkEntry(frame_left, placeholder_text="Longitude", width=200)
entry_dep = ctk.CTkEntry(frame_left, placeholder_text="Depth (km)", width=200)
entry_lat.pack(pady=6)
entry_lon.pack(pady=6)
entry_dep.pack(pady=6)

# Output Box
output_box = tk.Text(frame_left, height=25, width=45, font=("Mono", 12))
output_box.pack(pady=10)

# Fungsi perhitungan
def jalankan_perhitungan():
    output_box.delete("1.0", ctk.END)

    try:
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())
        dep = float(entry_dep.get())
    except ValueError:
        messagebox.showerror("Input Error", "Latitude, Longitude, dan Depth harus angka!")
        return

    # Hitung ML
    ML_list, ML_avg = process_ml(xml_ml, mseed_ml, lat, lon, dep)

    # Hitung MS & MB
    MS_list, MB_list, MS_avg, MB_avg = process_ms_mb(xml_msmb, mseed_msmb, lat, lon, dep)

    # Tulis Output
    output_box.insert(tk.END, "HASIL Ml\n")
    for i, ml in enumerate(ML_list):
        output_box.insert(tk.END, f"Stasiun {i+1}: Ml = {ml:.3f}\n")
    output_box.insert(tk.END, f"Ml Rata-rata = {ML_avg:.3f}\n\n")

    output_box.insert(tk.END, "HASIL Ms\n")
    for i, ms in enumerate(MS_list):
        output_box.insert(tk.END, f"Stasiun {i+1}: Ms = {ms:.3f}\n")
    output_box.insert(tk.END, f"Ms Rata-rata = {MS_avg:.3f}\n\n")

    output_box.insert(tk.END, "HASIL mB\n")
    for i, mb in enumerate(MB_list):
        output_box.insert(tk.END, f"Stasiun {i+1}: mB = {mb:.3f}\n")
    output_box.insert(tk.END, f"mB Rata-rata = {MB_avg:.3f}\n")

# Tampilan Plot
frame_right = ctk.CTkFrame(root)
frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
fig = plt.Figure(figsize=(8,7), dpi=100)
ax = fig.subplots(3, 2)
fig.tight_layout()

canvas = FigureCanvasTkAgg(fig, master=frame_right)
canvas.get_tk_widget().pack(fill="both", expand=True)

# Fungsi Plot
def plot_waveform():
    for i in range(3):
        # ML waveform
        st1 = obspy.read(mseed_ml[i])
        tr1 = st1[0]

        time1 = tr1.times("relative")

        ax[i][0].cla()
        ax[i][0].plot(time1, tr1.data, color="red", linewidth=1.0)
        ax[i][0].grid(True, linestyle="--", alpha=0.5)
        ax[i][0].set_title(f"Ml - {mseed_ml[i]}")
        ax[i][0].set_xlabel("Time (s)")
        ax[i][0].set_ylabel("Amplitude")

        # Ms/mb waveform
        st2 = obspy.read(mseed_msmb[i])
        tr2 = st2[0]

        time2 = tr2.times("relative")

        ax[i][1].cla()
        ax[i][1].plot(time2, tr2.data, color="blue", linewidth=1.0)
        ax[i][1].grid(True, linestyle="--", alpha=0.5)
        ax[i][1].set_title(f"Ms/mB - {mseed_msmb[i]}")
        ax[i][1].set_xlabel("Time (s)")
        ax[i][1].set_ylabel("Amplitude")
    fig.tight_layout()
    canvas.draw()

# Tombol Hitung dan Plot
btn_hitung = ctk.CTkButton(frame_left, text="Hitung Magnitudo", width=200, command=jalankan_perhitungan)
btn_hitung.pack(pady=5)
btn_plot = ctk.CTkButton(frame_left, text="Plot Gelombang", width=200, command=plot_waveform)
btn_plot.pack(pady=5)

# Jalankan GUI
root.mainloop()
