import time
import clr
import requests
import serial
import os

IOTUSER = os.environ['IOTUSER']
IOTPASS = os.environ['IOTPASS']


IoTURL = "https://my.iot-ticket.com/api/v1/process/write/RbTf0zwcni8bJ4L8oPhKmA"
openhardwaremonitor_hwtypes = ['Mainboard','SuperIO','CPU','RAM','GpuNvidia','GpuAti','TBalancer','Heatmaster','HDD']
openhardwaremonitor_sensortypes = ['Voltage','Clock','Temperature','Load','Fan','Flow','Control','Level','Factor','Power','Data','SmallData']

def getmoduledata():
    with serial.Serial('COM3', 9600, timeout=1) as ser:
        packet = bytearray()
        packet.append(0x3c)
        packet.append(0x02)
        packet.append(0x3e)
        ser.write(packet)
        s = ser.read(50)
        s = str(s)
        s = s.replace("b", "")
        s = s.replace("'", "")
        print(s)
        ser.close()

        r = requests.post(url=IoTURL, json=[{"name": "Room temperature sensor", "unit": "c", "v": s}], auth=(IOTUSER, IOTPASS))


def initialize_openhardwaremonitor():
    file = r'C:\\Users\\mikas\\Downloads\\openhardwaremonitor-v0.9.6\\OpenHardwareMonitor\\OpenHardwareMonitorLib.dll'
    clr.AddReference(file)

    from OpenHardwareMonitor import Hardware

    handle = Hardware.Computer()
    handle.MainboardEnabled = True
    handle.CPUEnabled = True
    handle.RAMEnabled = True
    handle.GPUEnabled = True
    handle.HDDEnabled = True
    handle.Open()
    return handle

def fetch_stats(handle):
    for i in handle.Hardware:
        i.Update()
        for sensor in i.Sensors:
            parse_sensor(sensor)
        for j in i.SubHardware:
            j.Update()
            for subsensor in j.Sensors:
                parse_sensor(subsensor)


def parse_sensor(sensor):
        if sensor.Value is not None:
            if type(sensor).__module__ == 'OpenHardwareMonitor.Hardware':
                sensortypes = openhardwaremonitor_sensortypes
                hardwaretypes = openhardwaremonitor_hwtypes
            else:
                return
            if sensor.SensorType == sensortypes.index('Load'):
                print(u"%s %s Load Sensor #%i %s - %s %%" % (hardwaretypes[sensor.Hardware.HardwareType], sensor.Hardware.Name, sensor.Index, sensor.Name, sensor.Value) + "\n")
                payload = [{"name":sensor.Name + " Load sensor", "unit":"percent", "v": sensor.Value}]
                print(payload)
                r = requests.post(url=IoTURL, json=payload, auth=(IOTUSER,IOTPASS))
                print(r.text)

            if sensor.SensorType == sensortypes.index('Temperature'):
                print(u"%s %s Temperature Sensor #%i %s - %s\u00B0C" % (hardwaretypes[sensor.Hardware.HardwareType], sensor.Hardware.Name, sensor.Index, sensor.Name, sensor.Value) + "\n")
                payload = [{"name":sensor.Hardware.Name, "unit":"c", "v": sensor.Value}]
                print(payload)
                r = requests.post(url=IoTURL, json=payload, auth=(IOTUSER,IOTPASS))
                print(r.text)

if __name__ == "__main__":
    print("OpenHardwareMonitor:")
    HardwareHandle = initialize_openhardwaremonitor()

    starttime = time.time()
    while True:
        try:
            getmoduledata()
            fetch_stats(HardwareHandle)
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
        except:
            print("Internet connection error")


