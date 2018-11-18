#-*-coding:utf-8-*-
import sys

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
        self.plot_style = self.STYLE_NORMAL
        self.datax = []
        self.datay = []

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
        self.styleChosen.bind("<<ComboboxSelected>>", self.style_selected)

        button = Button(master=frame_3, text="Quit", command=self._quit)
        button.pack(side=LEFT)
        button = Button(master=frame_3, text="Draw", command=self._draw)
        button.pack(side=LEFT)

    def style_selected(self, *args):
        var = self.styleChosen.get()
        self.plot_style = self.STYLE_DICT.get(var)
        print "choose ", var, ", plot_style=%d" % self.plot_style

    def style_selected(self, *args):
        var = self.styleChosen.get()
        self.plot_style = self.STYLE_DICT.get(var)
        print "choose ", var, ", plot_style=%d" % self.plot_style

    def plot_with_style(self, x, y):
        print "plot_with_style() plot_style=", self.plot_style
        if self.plot_style == self.STYLE_NORMAL:
            print "normal"
            plt.plot(x, y)
        elif self.plot_style == self.STYLE_BAR:
            print "bar"
            plt.bar(x, y)
        plt.show()

    def _quit(self):
        root.quit()     # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def destroy(self):
        # self.t.
        print "destroy()"

    def _draw(self):
        print "_draw() plot_style=", self.plot_style
        x = np.arange(0, 3, .01)
        y = 2 * np.sin(2 * np.pi * x)
        self.plot_with_style(x, y)

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    root = Tk()
    app = PlotWithStyle(root)
    root.mainloop()
    app.destroy()