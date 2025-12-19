import os
import time
import glob
import numpy as np
import tensorflow as tf
import psutil
import csv





from scipy.io import wavfile
from jtop import jtop
import matplotlib.pyplot as plt
import platform
from datetime import datetime
import errno

import subprocess

# ==== CONFIG ====
SAMPLE_RATE = 8000
NPY_PATH = 'npy-files'
TEST_DIR = 'test_recordings_split_1_sec'
MODEL_PATH = 'model.h5'
PLOTS_DIR = 'Inference+benchmarking'
INA3221_PATH = "/sys/bus/i2c/drivers/ina3221/1-0040/hwmon/hwmon1"
os.makedirs(PLOTS_DIR, exist_ok=True)

# ==== Get datetime string & device name for filenames ====
now_str = datetime.now().strftime("%H%M%S")
try:
    device_name = os.uname().nodename
except AttributeError:
    device_name = platform.node()
file_prefix = f"{device_name}_{now_str}"

log_file_path = os.path.join(PLOTS_DIR, f"{file_prefix}_test_results.txt")
resource_log_path = os.path.join(PLOTS_DIR, f"{file_prefix}_resource_usage.csv")

# ==== Enable GPU for TensorFlow ====
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)

# ==== Load Model ====
model = tf.keras.models.load_model(MODEL_PATH)

# ==== Label Index ====
labels = sorted([f.replace('.npy', '') for f in os.listdir(NPY_PATH)])
label_to_index = {label: i for i, label in enumerate(labels)}

# ==== Logging Setup ====
log_lines = []
def log(message):
    print(message)
    log_lines.append(message)

# ==== Feature Extraction ====
def safe_log(x):
    x = np.maximum(x, 1)
    return np.log2(x)

def chop_array(arr, window_size, hop_size):
    return [arr[i - window_size:i] for i in range(window_size, len(arr) + 1, hop_size)]

def filterbanks(sample_rate, num_filt, fft_len):
    def hertz_to_mels(f): return 1127. * np.log(1. + f / 700.)
    def mel_to_hertz(m): return 700. * (np.exp(m / 1127.) - 1.)
    def correct_grid(x):
        offset = 0
        for prev, i in zip([x[0] - 1] + x, x):
            offset = max(0, offset + prev + 1 - i)
            yield i + offset
    grid_mels = np.linspace(hertz_to_mels(0), hertz_to_mels(sample_rate), num_filt + 2, True)
    grid_hertz = mel_to_hertz(grid_mels)
    grid_indices = (grid_hertz * fft_len / sample_rate).astype(int)
    grid_indices = list(correct_grid(grid_indices))
    banks = np.zeros([num_filt, fft_len])
    for i, (left, middle, right) in enumerate(chop_array(grid_indices, 3, 1)):
        banks[i, left:middle] = np.linspace(0., 1., middle - left, False)
        banks[i, middle:right] = np.linspace(1., 0., right - middle, False)
    return banks

def frames2feature(audio):
    a = []
    frames = chop_array(audio, 256, 256)
    frames = np.short(frames)
    for frame in frames:
        fft = np.fft.fft(frame)
        fft = np.array(np.int32(fft.real)) >> 7
        fft = np.short(fft)
        sqr = (fft.astype("int32") ** 2) >> 8
        sqr[sqr >= 32768] = 32767
        filters = filterbanks(SAMPLE_RATE, 16, 256)
        intfltrs = np.array(filters * 32).round().astype("int8")
        mels = np.dot(sqr.astype("int32"), intfltrs.T.astype("int32")) & 0xffff
        features = np.array(safe_log(mels), dtype=np.int16)
        a.append(features)
    return np.expand_dims(np.array(a), axis=-1)

# ==== INA3221 Reader ====
import os
import subprocess
import glob

import os
import psutil

import os
import glob
import time
import subprocess

def read_ina3221_power_and_temp(power_path):
    def read_file_low_level(path, retries=3, delay=0.05, as_int=True):
        for attempt in range(retries):
            try:
                fd = os.open(path, os.O_RDONLY)
                content = os.read(fd, 64)
                os.close(fd)
                content_str = content.decode().strip()
                return int(content_str) if as_int else content_str
            except OSError as e:
                if e.errno == 11:  # EAGAIN
                    print(f"[RETRY] {path} temporarily unavailable. Retrying...")
                    time.sleep(delay)
                else:
                    print(f"[ERROR] Reading {path}: {e}")
                    break
            except Exception as e:
                print(f"[UNEXPECTED ERROR] {path}: {e}")
                break
        return None

    # INA3221 power and current readings (mV and mA)
    power_data = {
        "in1_input": read_file_low_level(os.path.join(power_path, "in1_input")),
        "in2_input": read_file_low_level(os.path.join(power_path, "in2_input")),
        "in3_input": read_file_low_level(os.path.join(power_path, "in3_input")),
        "curr1_input": read_file_low_level(os.path.join(power_path, "curr1_input")),
        "curr2_input": read_file_low_level(os.path.join(power_path, "curr2_input")),
        "curr3_input": read_file_low_level(os.path.join(power_path, "curr3_input")),
    }

    # psutil-based temperature readings
    thermal_data = {}
    for sensor_name, entries in psutil.sensors_temperatures().items():
        for i, entry in enumerate(entries):
            label = entry.label or f"N/A-{i}"
            key = f"{sensor_name} ({label})"
            thermal_data[key] = entry.current
            print(f"{key}: {entry.current:.1f} °C")

    return {
        "power": power_data,
        "temperature_C": thermal_data
    }

# ==== Thermal Zone Reader ====


# ==== Resource Monitoring ====
resource_log = []
monitoring = True

def monitor_all_resources():
    pid = os.getpid()
    proc = psutil.Process(pid)
    psutil.cpu_percent(interval=None, percpu=True)

    with jtop() as jetson:
        while monitoring and jetson.ok():
            start_time = time.time()

            # INA3221 sensor data (power and temp)
            ina3221_metrics = read_ina3221_power_and_temp(INA3221_PATH)
            ina3221_power = ina3221_metrics['power']
            ina3221_temp = ina3221_metrics['temperature_C']

            stats = jetson.stats

            timestamp = time.time()
            gpu_percent = stats.get("GPU", {}).get("usage", 0) if isinstance(stats.get("GPU", {}), dict) else stats.get("GPU", 0)
            cpu_power = (ina3221_power['in2_input'] * ina3221_power['curr2_input']) / 1000  # in mW
            gpu_power = (ina3221_power['in1_input'] * ina3221_power['curr1_input']) / 1000
            drawn_power = (ina3221_power['in3_input'] * ina3221_power['curr3_input']) / 1000
            ram_percent = psutil.virtual_memory().percent
            cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
            avg_cpu = np.mean(cpu_per_core)

            # Extract CPU-related temps (e.g., zone name includes 'cpu')
            cpu_temps = {k: v for k, v in ina3221_temp.items() if 'cpu' in k.lower()}

            # Log all
            log_entry = {
                "timestamp": timestamp,
                "gpu_percent": gpu_percent,
                "cpu_power": cpu_power,
                "gpu_power": gpu_power,
                "drawn_power": drawn_power,
                "ram_percent": ram_percent,
                "avg_cpu_percent": avg_cpu,
                "cpu_per_core": cpu_per_core,
                **ina3221_power,
                **ina3221_temp  # merged CPU temperature readings
            }

            resource_log.append(log_entry)

            elapsed = time.time() - start_time
            time.sleep(max(0.1 - elapsed, 0))


# ==== Inference ====
y_true = []
y_pred = []
inference_times = []

resource_thread = threading.Thread(target=monitor_all_resources)
resource_thread.start()

for class_dir in sorted(os.listdir(TEST_DIR)):
    dir_path = os.path.join(TEST_DIR, class_dir)
    if not os.path.isdir(dir_path): continue
    for fname in sorted(os.listdir(dir_path)):
        if not fname.endswith(".wav"): continue
        fpath = os.path.join(dir_path, fname)
        try:
            sr, wave = wavfile.read(fpath)
            if sr != SAMPLE_RATE: continue
            wave = np.pad(wave, (0, max(0, 7680 - len(wave))))[-7680:]
            features = frames2feature(wave)
            features = np.expand_dims(features, axis=0)
            start = time.perf_counter()
            preds = model.predict(features, verbose=0)
            end = time.perf_counter()
            inference_time = (end - start) * 1000
            inference_times.append(inference_time)
            pred_label = labels[np.argmax(preds)]
            true_label = class_dir.lower()
            if true_label not in label_to_index:
                log(f"⚠️ Skipped {fpath}: label '{true_label}' not in known labels.")
                continue
            status = "Correct" if pred_label == true_label else "Wrong"
            log(f"{fpath}: '{true_label}' == '{pred_label}' → {status} Inference time({inference_time:.2f} ms)")
            y_true.append(label_to_index[true_label])
            y_pred.append(label_to_index[pred_label])
        except Exception as e:
            log(f"⚠️ Error processing {fpath}: {e}")

monitoring = False
resource_thread.join()

# ==== Save Logs ====
avg_time = np.mean(inference_times)
power = [entry.get("drawn_power", 0) for entry in resource_log]
avg_power = sum(power)/len(power)
log(f"\n⏱️ Average inference time: {avg_time:.2f} ms")
log(f"⚡ Estimated throughput: {1000 / avg_time:.2f} samples/sec")
log(f"Estimated Power consumption: {avg_power:.0f} mW")

avgMeterCurr = float(input("Record the Power consumption from Meter in Amps"))
log(f"Current (Amps) Measurement from USB DIGITAL TESTER: {avgMeterCurr:.4f} A")
avgMeterVolt = float(input("Record the Voltage value from USB DIGITAL TESTER in Volts"))
log(f"Voltage (Volt) Measurement from USB DIGITAL TESTER: {avgMeterVolt:.4f} V")
avgMeterWatts = float(input("Record the Power consumption from USB DIGITAL TESTER in Watts"))
log(f"Power (Watts) Measurement from USB DIGITAL TESTER: {avgMeterWatts:.4f} W")

with open(log_file_path, 'w') as f:
    for line in log_lines:
        f.write(line + '\n')

# ==== CSV Export ====
timestamps = [entry["timestamp"] for entry in resource_log]
timestamps_sec = [ts - timestamps[0] for ts in timestamps]

# Extract metrics
gpu_percents = [entry["gpu_percent"] for entry in resource_log]
cpu_powers = [entry["cpu_power"] for entry in resource_log]
gpu_powers = [entry["gpu_power"] for entry in resource_log]
combined_powers = [entry["drawn_power"] for entry in resource_log]
ram_percents = [entry["ram_percent"] for entry in resource_log]
avg_cpu_percents = [entry["avg_cpu_percent"] for entry in resource_log]
cpu_cores_usage = [entry["cpu_per_core"] for entry in resource_log]
num_cores = len(cpu_cores_usage[0]) if cpu_cores_usage else 0

# Get INA3221 voltages for labeling
vdd_gpu = [entry.get("gpu_power", 0) for entry in resource_log]
vdd_cpu = [entry.get("cpu_power", 0) for entry in resource_log]
vdd_soc = [entry.get("drawn_power", 0) for entry in resource_log]

temp_labels = ['tmp451 (N/A-0)', 'tmp451 (N/A-1)', '6800000ethernet']

print(resource_log)
# Match keys that include any of the prefixes
temp_keys = [
    k for k in resource_log[0].keys()
    if isinstance(resource_log[0][k], (int, float)) and any(label in k for label in temp_labels)
]



# Extract values for those temperature keys
temp_data = {
    key: [entry.get(key, 0) for entry in resource_log]
    for key in temp_keys
}

# Write to CSV
with open(resource_log_path, 'w', newline='') as f:
    writer = csv.writer(f)
    header = ["timestamp", "gpu_percent", "cpu_power", "gpu_power", "combined_power",
              "ram_percent", "avg_cpu_percent", "VDD_5V_PWR", "VDD_CPU_GPU", "VDD_SOC"]
    header += [f"cpu_core_{i}_percent" for i in range(num_cores)]
    header += [f"temp_{k}" for k in temp_keys]  # Add temp headers
    writer.writerow(header)
    print("temp keys is ", temp_keys)

    for i in range(len(timestamps)):
        row = [
            timestamps[i], gpu_percents[i], cpu_powers[i], gpu_powers[i], combined_powers[i],
            ram_percents[i], avg_cpu_percents[i], vdd_cpu[i], vdd_gpu[i], vdd_soc[i]
        ] + cpu_cores_usage[i] + [temp_data[k][i] for k in temp_keys]  # Add temp values
        writer.writerow(row)


# ==== Plot All Metrics Automatically ====

# Function to generate line plots
def save_line_plot(x_values, y_values, title, ylabel, filename):
    plt.figure(figsize=(12, 6))
    plt.plot(x_values, y_values, label=title)
    plt.xlabel("Time (seconds)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f"{file_prefix}_{filename}.png"))
    plt.close()

# Fixed metrics
save_line_plot(timestamps_sec, gpu_percents, "GPU Usage (%)", "GPU Usage (%)", "gpu_usage")
save_line_plot(timestamps_sec, avg_cpu_percents, "Average CPU Usage (%)", "CPU Usage (%)", "avg_cpu_usage")
save_line_plot(timestamps_sec, ram_percents, "RAM Usage (%)", "RAM Usage (%)", "ram_usage")
save_line_plot(timestamps_sec, vdd_soc, "INA3221 POM_5V_IN Power (mW)", "Power (mW)", "vdd_soc")
save_line_plot(timestamps_sec, vdd_cpu, "INA3221 POM_5V_CPU Power (mW)", "Power (mW)", "vdd_cpu_power")
save_line_plot(timestamps_sec, vdd_gpu, "INA3221 POM_5V_GPU Power (mW)", "Power (mW)", "vdd_gpu_power")

# Per-core CPU usage plots
for i in range(0, num_cores, 4):
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    for j in range(4):
        core_idx = i + j
        if core_idx >= num_cores:
            axs[j // 2, j % 2].axis("off")
            continue
        core_usage = [cpu_cores_usage[k][core_idx] for k in range(len(cpu_cores_usage))]
        axs[j // 2, j % 2].plot(timestamps_sec, core_usage, label=f"CPU Core {core_idx}")
        axs[j // 2, j % 2].set_title(f"CPU Core {core_idx}")
        axs[j // 2, j % 2].set_xlabel("Time (seconds)")
        axs[j // 2, j % 2].set_ylabel("Usage (%)")
        axs[j // 2, j % 2].legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f"{file_prefix}_cpu_cores_{i}_to_{min(i+3, num_cores-1)}.png"))
    plt.close()

# Plot all temperature metrics
for temp_key in temp_keys:
    temp_values = temp_data[temp_key]
    clean_key = temp_key.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
    save_line_plot(timestamps_sec, temp_values, f"{temp_key} Temperature (°C)", "Temperature (°C)", f"temp_{clean_key}")
