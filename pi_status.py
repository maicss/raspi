# coding: utf-8

import re
import subprocess

import psutil
from pymongo import MongoClient

db = MongoClient("mongodb://localhost:27017/raspi", connect=False)

collection = db['status']

data = {}


def get_cpu_usage():
    cpu_count = psutil.cpu_count()
    usage = []
    for i in range(cpu_count):
        usage.append(psutil.cpu_percent(interval=1))
    return {
        "cpu_usage": usage
    }


def get_mer_usage():
    svmem = psutil.virtual_memory()
    Gb = 1024 ** 3
    rest = svmem[4] / Gb
    percent = svmem[2]
    _all = svmem[0] / Gb

    return {
        'mem_rest': round(rest, 2),
        'percent': percent,
        'all': round(_all, 2)
    }


def get_disk_usage():
    Gb = 1024 ** 3
    disk = psutil.disk_usage('/')
    return {
        'disk_rest': round(disk[2] / Gb, 2),
        'percent': round(disk[3] / Gb, 2),
        'all': round(disk[0] / Gb, 2)
    }


def get_temperature():
    temp_file = open("/sys/class/thermal/thermal_zone0/temp")
    gpu_temp = float(re.compile(r'\d+\.\d').search(subprocess.getoutput('/opt/vc/bin/vcgencmd measure_temp')).group())
    cpu_temp = temp_file.read()
    temp_file.close()

    return {
        'cpu_t': float(cpu_temp) / 1000,
        'gpu_t': gpu_temp
    }


if __name__ == '__main__':
    data.update(get_cpu_usage())
    data.update(get_disk_usage())
    data.update(get_mer_usage())
    data.update(get_temperature())
    collection.insertOne(data)
