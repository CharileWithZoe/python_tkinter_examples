#-*-coding:utf-8-*-
import os, sys

if sys.version_info < (3,0,0):
    from Tkinter import *
    from ttk import *
    import tkFont
    import tkFileDialog as FileDiag
    import Queue
else:
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.font as tkFont
    import tkinter.filedialog as FileDiag
    import queue as Queue

import matplotlib.pyplot as plt
import numpy as np
import json

def scanJsonFiles(path):
    jsfiles = []
    for rt, dirs, files in os.walk(path):
        for f in files:
            ff = os.path.join(rt,f)
            if ".json" == os.path.splitext(ff)[-1]:
                jsfiles.append(ff)
                print "json file:", ff
    return jsfiles

def writeJsonFile(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def readJsonFile(filename):
    data = {}
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data

def generateTestJsonFile():
    x = np.arange(0, 1, .01)
    y1 = np.power(x, 1)
    y2 = np.power(x, 2)
    y3 = np.power(x, 3)
    data1 = {"name": "power_1", "x" : list(x), "y" : list(y1)}
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_1.json", [data1])
    data2 = {"name": "power_2", "x": list(x), "y": list(y2)}
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_2.json", [data2])
    data3 = {"name": "power_3", "x": list(x), "y": list(y3)}
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_3.json", [data3])
    data = [data1, data2, data3]
    writeJsonFile(sys.path[0] + os.sep + "testdata" + os.sep + "power_123.json", data)

class PlotWithStyle:
    STYLE_NORMAL    = 1  # 柱状图和散点图都一样
    STYLE_BAR       = 2
    STYLE_PIE       = 3
    # Should set with unicode, because the style_selected() return value is unicode
    STYLE_DICT = {
        u"柱状图": STYLE_BAR,
        u"散点图或折线图": STYLE_NORMAL,
        u"饼状图": STYLE_PIE
    }

    def __init__(self, master):
        self.master = master
        self.plot_style = None
        self.jsonfile = None
        self.datax = []
        self.datay = []

        master.title('MyPlot')
        # root.resizable(width=False, height=False)
        master.geometry('%dx%d+200+100' % (600, 300))

        frame_1 = Frame(self.master, relief=RIDGE, borderwidth=2)
        frame_1.pack(fill=X, expand=NO, side=TOP, ipady=5)
        frame_2 = Frame(self.master, relief=RIDGE, borderwidth=2)
        frame_2.pack(fill=X, expand=NO, side=TOP, ipady=5)
        frame_3 = Frame(self.master, relief=RIDGE, borderwidth=2)
        frame_3.pack(fill=X, expand=NO, side=TOP, ipady=5)

        Label(frame_1, text=" Style: ").pack(fill=NONE, expand=False, side=LEFT)
        self.styleChosen = Combobox(frame_1, state='readonly')
        self.styleChosen['values'] = self.STYLE_DICT.keys()     # 设置下拉列表的值
        self.styleChosen.pack(side=TOP, fill=BOTH, expand=YES)
        self.styleChosen.current(0)    # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值
        self.plot_style = self.STYLE_DICT.get(self.styleChosen['values'][0])
        self.styleChosen.bind("<<ComboboxSelected>>", self.style_selected)

        self.allJsonFiles = scanJsonFiles(sys.path[0])
        Label(frame_2, text=" Data: ").pack(fill=NONE, expand=False, side=LEFT)
        self.dataChosen = Combobox(frame_2, state='readonly')
        self.dataChosen['values'] = self.allJsonFiles    # 设置下拉列表的值
        self.dataChosen.pack(side=TOP, fill=BOTH, expand=YES)
        self.dataChosen.current(0)    # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值
        self.jsonfile = self.dataChosen['values'][0]
        self.dataChosen.bind("<<ComboboxSelected>>", self.data_selected)

        button = Button(master=frame_3, text="Quit", command=self._quit)
        button.pack(side=LEFT)
        button = Button(master=frame_3, text="Draw", command=self._draw)
        button.pack(side=LEFT)

    def style_selected(self, *args):
        var = self.styleChosen.get()
        self.plot_style = self.STYLE_DICT.get(var)
        print "style_selected(), choose ", var, ", plot_style=%d" % self.plot_style

    def data_selected(self, *args):
        self.jsonfile = self.dataChosen.get()
        print "data_selected(), choose ", self.jsonfile

    def plot_with_style(self, x, y):
        print "plot_with_style() plot_style=", self.plot_style
        if self.plot_style == self.STYLE_NORMAL:
            print "normal"
            plt.plot(x, y)
        elif self.plot_style == self.STYLE_BAR:
            print "bar"
            plt.bar(x, y)
        plt.show()

    def plot_in_subplot(self, data):
        plt.figure(1)
        num = len(data)
        for i in range(0, len(data)):
            plt.subplot(num, 1, i+1)
            plt.plot(data[i]['x'], data[i]['y'], label=data[i]['name'])
            plt.title(data[i]['name'])
            plt.grid(True)
        plt.show()

    def plot_in_onefigure(self, data):
        plt.figure(2)
        plt.subplot(1, 1, 1)
        for i in range(0, len(data)):
            plt.plot(data[i]['x'], data[i]['y'], label = data[i]['name'])
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.show()

    def _quit(self):
        root.quit()
        root.destroy()

    def destroy(self):
        print "destroy()"

    def _draw(self):
        if self.plot_style is None:
            print "no plot style for plot"
            return
        if self.jsonfile is None:
            print "no jsonfile to plot"
            return
        print "_draw() plot_style=", self.plot_style
        data = readJsonFile(self.jsonfile)
        self.plot_in_subplot(data)
        self.plot_in_onefigure(data)

if __name__ == '__main__':
    generateTestJsonFile()
    reload(sys)
    sys.setdefaultencoding('utf8')
    root = Tk()
    app = PlotWithStyle(root)
    root.mainloop()
    app.destroy()