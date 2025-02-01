import subprocess
import os
import time

def get_cpu_usage():
    return os.getloadavg()

def get_temperature():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp_raw = f.read().strip()
            # temp_raw ist oft in m°C, also z.B. "42000" für 42°C
            temperature = float(temp_raw) / 1000.0
    except:
        temperature = None
    return temperature

def get_storage_usage():
    try:
        df_output = subprocess.check_output("df -h /", shell=True).decode('utf-8').strip().split("\n")
        # Filesystem      Size  Used Avail Use% Mounted on
        # /dev/root        15G  4.2G  9.5G  31% /
        if len(df_output) > 1:
            fields = df_output[1].split()
            storage_available = fields[3] # root
        else:
            storage_available = None
    except:
        storage_available = None
    return storage_available


def main():
    print("cpu,temp,mem")
    while True:
        print(f"{get_cpu_usage()};{get_temperature()};{get_storage_usage()}")
        time.sleep(5)

if __name__ == "__main__":
    main()
