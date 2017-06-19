import os
from helpers import start_gpu_z, LOG_PATH, mining_check, tempereture_base_scale


"""
try:
    os.remove(LOG_PATH)
except Exception as ex:
    print(str(ex))

mining_check()
"""

tempereture_base_scale()
