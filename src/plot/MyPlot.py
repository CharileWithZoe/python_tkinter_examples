#-*-coding:utf-8-*-
import os, sys
sys.path.append('..')
from myutils.mylog import mylog
"""
if sys.version_info < (3,0,0):
    from Tkinter import *
    from ttk import *
    import tkFont
    import tkFileDialog as FileDiag
    import Queue
    import matplotlib.dates as mdates
else:
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.font as tkFont
    import tkinter.filedialog as FileDiag
    import queue as Queue
"""
from tkinter import *
from tkinter.ttk import *
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import json
import matplotlib
matplotlib.use('TkAgg')

log = mylog(level="info", filename="output.log")

def scanJsonFiles(path):
    log.i("scanJsonFiles(), path=%s" % path)
    jsfiles = []
    for rt, dirs, files in os.walk(path):
        for f in files:
            ff = os.path.join(rt,f)
            if ".json" == os.path.splitext(ff)[-1]:
                jsfiles.append(ff)
                log.i("json file: %s" % ff)
    return jsfiles

def writeJsonFile(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def readJsonFile(filename):
    data = {}
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data

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
        self.styleChosen['values'] = list(self.STYLE_DICT.keys())     # 设置下拉列表的值
        self.styleChosen.pack(side=TOP, fill=BOTH, expand=YES)
        self.styleChosen.current(0)    # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值
        self.plot_style = self.STYLE_DICT.get(self.styleChosen['values'][0])
        self.styleChosen.bind("<<ComboboxSelected>>", self.style_selected)

        self.allJsonFiles = scanJsonFiles(sys.path[0])
        Label(frame_2, text=" Data: ").pack(fill=NONE, expand=False, side=LEFT)
        self.dataChosen = Combobox(frame_2, state='readonly')
        if len(self.allJsonFiles) < 1:
            self.dataChosen['values'] =  'Choose your file...'
            self.jsonfile = None
        else:
            self.dataChosen['values'] = self.allJsonFiles    # 设置下拉列表的值
            self.dataChosen.current(0)  # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值
            self.jsonfile = self.dataChosen['values'][0]
        self.dataChosen.pack(side=TOP, fill=BOTH, expand=YES)
        self.dataChosen.bind("<<ComboboxSelected>>", self.data_selected)

        button = Button(master=frame_3, text="Quit", command=self._quit)
        button.pack(side=LEFT)
        button = Button(master=frame_3, text="Draw", command=self._draw)
        button.pack(side=LEFT)

    def style_selected(self, *args):
        var = self.styleChosen.get()
        self.plot_style = self.STYLE_DICT.get(var)
        log.i("style_selected(), choose %s, plot_style=%d" % (var,self.plot_style))

    def data_selected(self, *args):
        self.jsonfile = self.dataChosen.get()
        log.i("data_selected(), choose %s" % self.jsonfile)

    def plot_with_style(self, x, y):
        log.i("plot_with_style() plot_style=", self.plot_style)
        if self.plot_style == self.STYLE_NORMAL:
            log.i("normal")
            plt.plot(x, y)
        elif self.plot_style == self.STYLE_BAR:
            log.i("bar")
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

    def plot_with_date(self, data):
        from datetime import datetime

        plt.figure(3)
        plt.subplot(1, 1, 1)
        for i in range(0, len(data)):
            # "11-13 07:16:30.577",
            # datetime.strptime(s, '%m-%d %H:%M:%S').date()
            # xs = [datetime.strptime(d, '%m-%d %H:%M:%S').date() for d in data[i]['x']]
            xs = []
            for d in data[i]['x']:
                d = "2018-" + d[0:-4]
                temp = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
                xs.append(temp)
            print(xs)
            ys = []
            for dd in data[i]['y']:
                dd = dd[0:-1]
                temp = int(dd)
                ys.append(temp)
            print(ys)
            plt.plot(xs, ys, label = data[i]['name'])

        # 配置横坐标
        #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        # if set, only the major is show
        #plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gcf().autofmt_xdate()  # 自动旋转日期标记
        plt.legend(loc='upper right')
        plt.grid(True)
        plt.show()

    def _quit(self):
        root.quit()
        root.destroy()

    def destroy(self):
        log.i("destroy()")

    def _draw(self):
        if self.plot_style is None:
            log.i("no plot style for plot")
            return
        if self.jsonfile is None:
            log.i("no jsonfile to plot")
            return
        log.i("_draw() plot_style=%sf" % self.plot_style)
        data = readJsonFile(self.jsonfile)

        if len(data)>=2 and data[0].get("type") == "json-config" and data[0].get("style") == "time-series":
            self.plot_with_date(data[1:-1])
        else:
            self.plot_in_subplot(data)
            self.plot_in_onefigure(data)

if __name__ == '__main__':
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    root = Tk()
    app = PlotWithStyle(root)
    root.mainloop()
    app.destroy()