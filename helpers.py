import subprocess
import os
from datetime import datetime
import time
from requests import get
from re import findall

"""
# Test env
GPU_Z = "GPU-Z.exe"
MINE_TOOL = "ethminer.exe"
OP_MONITOR = "OpenHardwareMonitor.exe"
# GPUZ_LOG = "C:\\Users\\User\\\Downloads\\GPU-Z Sensor Log.txt"
GPUZ_LOG = "C:\\Users\Sabbir\\Documents\\CodeZone\\PythonLab\\RnD\\gpuzfileparser\\GPU-Z Sensor Log.txt"
ETHMINER_BAT = "C:\\Users\Sabbir\\Documents\\CodeZone\\PythonLab\\RnD\\gpuzfileparser\\test.bat"
LOG_PATH = "C:\\Users\Sabbir\\Documents\\CodeZone\\PythonLab\\RnD\\gpuzfileparser\\log\\" + str(datetime.now().strftime('%Y-%m-%d')) + "-miner_script.txt"
CLOCK_BREACH_VALUE = 200
TEMP_BREACH_LIMIT = 60
API_URL = "http://192.168.2.115:8085/data.json"
"""
# Prod env
GPU_Z = "GPU-Z.exe"
MINE_TOOL = "ethminer.exe"
GPUZ_LOG = "C:\\Users\\User\\\Downloads\\GPU-Z Sensor Log.txt"
# ETHMINER_BAT = "D:\\Ethereum\\ethminer-0.9.41-genoil-1.1.7\\etherminer.org.bat"
ETHMINER_BAT = "D:\\Ethereum\\ethminer-0.9.41-genoil-1.1.7\\dwarfpool.com.bat"
LOG_PATH = "D:\\gpucheck\\log\\" + str(datetime.now().strftime('%Y-%m-%d')) + "-miner_script.txt"
CLOCK_BREACH_VALUE = 1200
TEMP_BREACH_LIMIT = 46
API_URL = "http://localhost:8085/data.json"
OP_MONITOR = "OpenHardwareMonitor.exe"


def wl(txt):
    print(txt)
    with open(LOG_PATH, "a+") as myfile:
        myfile.write(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ": " + txt + "\n")


def start_gpu_z():
    # return False
    try:
        os.remove(GPUZ_LOG)
        # p = subprocess.Popen('start "" "C:\Program Files (x86)\GPU-Z\' + GPU_Z + '"', shell=True)
        p = subprocess.Popen("start \"\" \"C:\\Program Files (x86)\\GPU-Z\\" + GPU_Z + "\"", shell=True)
        stdout_data, stderr_data = p.communicate()
        if p.returncode != 0:
            wl("SOmething went wrong>>" + stderr_data)
        p.wait()
        wl(GPU_Z + " started again")
        return True
    except Exception as ex:
        wl("Something went wrong>>" + str(ex))


def mining_check():
    try:
        with open(GPUZ_LOG) as file:
            last_line = file.readlines()[-1]
    except Exception as ex:
        wl("GPU Z LOG MISSING")
        start_gpu_z()

    # last_line is a string value pointing to last line,
    # to convert it into float, you can do

    # number = float(last_line.strip('\n').strip(' '))
    # [x.strip() for x in my_string.split(',')]
    # print(last_line)

    splited_last_line = last_line.strip("\n").strip("\r").split(",")
    # print(splited_last_line[6].strip(' '))
    min_diff = 0
    if len(splited_last_line) > 2:
        try:
            date_raw = "".join(splited_last_line[0].split())
            fmt = '%Y-%m-%d%H:%M:%S'
            # 2017-06-1615:16:28
            d1 = datetime.strptime(date_raw, fmt)
            d2 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            d2 = datetime.strptime(d2, '%Y-%m-%d %H:%M:%S')
            d1_ts = time.mktime(d1.timetuple())
            d2_ts = time.mktime(d2.timetuple())
            min_diff = int(d2_ts - d1_ts) / 60
        except Exception as ex:
            wl(str(ex))
            wl("Assuming Date data unavailable due to GPU Z not running, so rerun GPU Z")
            kill_process(GPU_Z)
            start_gpu_z()

        if min_diff > 11:
            wl("Assuming its not updating, so rerun GPU Z")
            kill_process(GPU_Z)
            start_gpu_z()
        else:
            final_string = "".join(splited_last_line[1].split())
            try:
                final_val = float(final_string)
                if final_val > CLOCK_BREACH_VALUE:
                    # if final_val > 1180:
                    wl("Things are running fine.")
                    kill_process(GPU_Z)
                    start_gpu_z()
                else:
                    wl("Mining need some boost.")
                    kill_process(MINE_TOOL)
                    mining_start()
                    kill_process(GPU_Z)
                    start_gpu_z()
            except Exception as ex:
                wl(str(ex))


def mining_start():
    # os.startfile("C:\\Users\\Sabbir\\Desktop\\test.bat")
    os.startfile(ETHMINER_BAT)
    wl("Mining started...!")
    return True

    p = subprocess.Popen("C:\\Users\\Sabbir\\Desktop\\test.bat", creationflags=subprocess.CREATE_NEW_CONSOLE)
    # p = subprocess.Popen("cmd /k C:\\Users\\Sabbir\\Desktop\\test.bat", shell=False)
    stdout_data, stderr_data = p.communicate()
    if p.returncode != 0:
        wl("Something went wrong>>" + stderr_data)
        p.wait()
    else:
        p.wait()
        wl("Mining started successfully.")
        return True


def kill_process(process_name):
    subp = subprocess.check_output(['tasklist'])
    if process_name in str(subp):
        wl(process_name + " : found.")
        p = subprocess.Popen('taskkill /f /IM ' + process_name, shell=True)
        stdout_data, stderr_data = p.communicate()
        if p.returncode == 0:
            wl("Kill Sucess")
        else:
            wl("Something went wrong for kill >>" + process_name + ": " + str(stderr_data))
    wl("I passed kill process.")


def tempereture_base_scale():
    wl("\n\n-------------A NEW PROCESS-------------------- \n" + ETHMINER_BAT + "\n")

    try:
        resp = get(API_URL)
        if resp.status_code == 200:
            json_data = resp.json()
            try:
                gpu_json = json_data['Children'][0]['Children']
                for gpu_item in gpu_json:
                    if 'Radeon RX 580 Series' in gpu_item['Text']:
                        for item in gpu_item['Children']:
                            if 'Temperatures' in item['Text']:
                                temp_item = item['Children']
                                tempereture = temp_item[0]['Value']
                                try:
                                    int_temp_list = findall(r'\d+', tempereture)
                                    # print(int_temp)
                                    real_temp = int_temp_list[0]
                                    if(int(real_temp) < TEMP_BREACH_LIMIT):
                                        wl(str(real_temp) + ": Which is lower than expected.")
                                        kill_process(MINE_TOOL)
                                        mining_start()
                                        exit()
                                    else:
                                        wl("Check passed with tempereture " + str(real_temp))
                                except Exception as ex:
                                    wl("Number extract error, " + str(ex))
                                    kill_and_open_hw_mon()
                                    exit()
            except Exception as ex:
                wl(str(ex))
                kill_and_open_hw_mon()
                exit()
        else:
            wl("API Call error for " + API_URL)
    except Exception as ex:
        wl(str(ex))
        # kill_and_open_hw_mon()


def kill_and_open_hw_mon():
    kill_process(OP_MONITOR)

    try:
        # p = subprocess.Popen('start "" "C:\Program Files (x86)\GPU-Z\' + GPU_Z + '"', shell=True)
        p = subprocess.Popen("start \"\" \"C:\\Program Files\\OpenHardwareMonitor\\" + OP_MONITOR + "\"", shell=True)
        stdout_data, stderr_data = p.communicate()
        if p.returncode != 0:
            wl("Something went wrong for OP HW Montinor>>" + stderr_data)
        p.wait()
        wl(OP_MONITOR + " started again")
        return True
    except Exception as ex:
        wl(OP_MONITOR + " :: Something went wrong>>" + str(ex))
