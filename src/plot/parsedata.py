import sys
import re
import json

def get_time_from_log(line):
    result = []
    r = re.compile(r'(\d\d-\d\d\s+\d\d:\d\d:\d\d)')
    match = r.match(line)
    if match:
        return match.group().replace("-","").replace(" ","").replace(":","")
    return "0000000000"

def writeJsonFile(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def parsedata(file_in, file_out):
    d = {}

    with open(file_in, 'r') as f1:
        lines = f1.readlines()

    for line in lines:
        line = line.strip()
        line = line.strip("\r\n")
        r = re.compile(r'(\d\d-\d\d\s+\d\d:\d\d:\d\d\.\d\d\d)\s+(.*)')
        m = r.match(line)
        #print line
        if m:
            t = m.groups()[0]
            s = m.groups()[1]
            a = s.split()
            while len(a) >= 2:
                v = a.pop()
                n = a.pop()
                #print n,v,d
                n = n.strip(":")
                if not d.has_key(n):
                    d[n] = []
                d[n].append((t, v))
    graphic = []

    # You can add the configs to the dictionary
    configs = {}
    configs["type"] = "json-config"
    configs["style"] = "time-series"
    graphic.append(configs)
    for e in d.keys():
        g = {}
        print "----->",e, d[e]
        g["name"] = e
        g["x"] = [i[0] for i in d[e]]
        g["y"] = [i[1] for i in d[e]]
        g["type"] = "json-data"
        graphic.append(g)

    writeJsonFile(file_out, graphic)

def generateTestJsonFile():
    import numpy as np
    x = np.arange(0, 1, .01)
    y1 = np.power(x, 1)
    y2 = np.power(x, 2)
    y3 = np.power(x, 3)
    data1 = {"name": "power_1", "x": list(x), "y": list(y1)}
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_1.json", [data1])
    data2 = {"name": "power_2", "x": list(x), "y": list(y2)}
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_2.json", [data2])
    data3 = {"name": "power_3", "x": list(x), "y": list(y3)}
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_3.json", [data3])
    data = [data1, data2, data3]
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_123.json", data)

def generateJsonFileBatteryInfo():
    import numpy as np
    x = np.arange(0, 1, .01)
    y1 = np.power(x, 1)
    y2 = np.power(x, 2)
    y3 = np.power(x, 3)
    data1 = {"name": "power_1", "x": list(x), "y": list(y1)}
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_1.json", [data1])
    data2 = {"name": "power_2", "x": list(x), "y": list(y2)}
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_2.json", [data2])
    data3 = {"name": "power_3", "x": list(x), "y": list(y3)}
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_3.json", [data3])
    data = [data1, data2, data3]
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_123.json", data)

if __name__ == "__main__":
    import os
    file_in = sys.path[0] + os.sep + "testdata" + os.sep + "graphic.txt"
    file_out = sys.path[0] + os.sep + "testdata" + os.sep + "memory.json"
    parsedata(file_in, file_out)

    generateTestJsonFile()
