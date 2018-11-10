# coding=utf-8
import sys

"""
from https://www.jb51.net/article/144294.htm
"""

if sys.version_info < (3,0,0):
    sys.stdout.write("***python2\n")
    from Tkinter import *
    from ttk import * 
    import tkFont
    import tkFileDialog as FileDiag
else:
    sys.stdout.write("***python3\n")
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.font as tkFont
    import tkinter.filedialog as FileDiag
import math
import time
from threading import Thread

class Clock:
  def __init__(self, master, x, y, width, height, radius):
    '''
    :param master: 父窗口
    :param x: 时钟中心点的x坐标
    :param y: 时钟中心点的y坐标
    :param width: 画布的宽度
    :param height: 画布的高度
    :param radius: 时钟钟盘的半径
    '''
    self.centerX = x
    self.centerY = y
    self.radius = radius
    self.canvas = Canvas(master, width=width, height=height) # 画布
    self.canvas.pack()
    self.canvas.create_oval(
      x - radius,
      y - radius,
      x + radius,
      y + radius) # 画钟框
    self.id_lists = []
    self.hourHandRadius = self.radius * 1.0 / 4  # 指针长度
    self.minHandRadius = self.radius * 2.0 / 3  # 分针长度
    self.secHandRadius = self.radius * 4.0 / 5  # 秒针长度
    self.timeVar = StringVar()
    # self.timeVar.set('')
    self.timeLabel = Label(self.canvas.master, textvariable=self.timeVar)
    self.timeLabel.pack(side=BOTTOM)
    #self.canvas.master.protocol('WM_DELETE_WINDOW', self.canvas.master.destroy)
    
    self.drawClockDial()
    self.run()

  def __del__(self):
    self._deleteItems(self.id_lists)

  # 绘制时钟钟盘
  def drawClockDial(self):
    # 绘制钟盘上的数字1-12
    r = self.radius - 15
    for i in range(1, 13):
      rad = 2 * math.pi / 12 * i
      x = self.centerX + math.sin(rad) * r
      y = self.centerY - math.cos(rad) * r
      id = self.canvas.create_text(x, y, text=str(i))
      self.id_lists.append(id)
    # 绘制钟盘上的刻度
    r1 = self.radius - 5
    r2 = self.radius
    for i in range(1, 61):
      rad = 2 * math.pi / 60 * i
      x1, y1 = self._getPosByRadAndRadius(rad, r1)
      x2, y2 = self._getPosByRadAndRadius(rad, r2)
      id = self.canvas.create_line(x1, y1, x2, y2)
      self.id_lists.append(id)

  # 显示时间
  def showTime(self, tm):
    hour = tm.tm_hour % 12
    min = tm.tm_min
    sec = tm.tm_sec
    sec_rad = 2 * math.pi / 60 * sec
    min_rad = 2 * math.pi / 60 * (min + sec / 60.0)
    hour_rad = 2 * math.pi / 12 * (hour + min / 60.0)
    timeStr = '当前时间: %d-%02d-%02d %02d:%02d:%02d' % (
      tm.tm_year, tm.tm_mon, tm.tm_mday, hour, min, sec)
    self.timeVar.set(timeStr)
    hour_id = self._drawLine(hour_rad, self.hourHandRadius, 6)
    min_id = self._drawLine(min_rad, self.minHandRadius, 4)
    sec_id = self._drawLine(sec_rad, self.secHandRadius, 3)
    return (hour_id, min_id, sec_id)

  def run(self):
    def _run():
      while True:
        tm = time.localtime()
        id_lists = self.showTime(tm)
        self.canvas.master.update()
        time.sleep(1)
        self._deleteItems(id_lists)
    thrd = Thread(target=_run) # 创建新的线程
    thrd.run() # 启动线程
    
  def _drawLine(self, rad, radius, width):
    x, y = self._getPosByRadAndRadius(rad, radius)
    id = self.canvas.create_line(
      self.centerX, self.centerY, x, y, width=width)
    return id

  def _getPosByRadAndRadius(self, rad, radius):
    x = self.centerX + radius * math.sin(rad)
    y = self.centerY - radius * math.cos(rad)
    return (x, y)

  def _deleteItems(self, id_lists):
    for id in id_lists:
      try:
        self.canvas.delete(id)
      except BaseException:
        pass

if __name__ == '__main__':
  root = Tk()
  root.title('misc clock')
  clock = Clock(root, 200, 200, 400, 400, 150)
  root.mainloop()