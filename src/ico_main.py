#-*-coding:utf-8-*-
import sys
import os
import threading, time
import re
import subprocess
import json
from utils import *

if sys.version_info < (3,0,0):
    info("***python2")
    from Tkinter import *
    from ttk import * 
    import tkFont
    import tkFileDialog as FileDiag
    import Queue
else:
    info("***python3")
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.font as tkFont
    import tkinter.filedialog as FileDiag
    import queue as Queue

script_path = os.path.dirname(__file__)
if script_path:
    PYTHON_CMD = "python " + script_path + os.sep
else:
    PYTHON_CMD = "python "

"""
pack layout:
expand − When set to true, widget expands to fill any space not otherwise used
in widget's parent.
     It used when the window trun to big size, set this to NO if you don't want to
change the size of the widget

fill − Determines whether widget fills any extra space allocated to it by the 
packer, or keeps its own minimal dimensions: 
NONE (default),
X (fill only horizontally)
Y (fill only vertically)
BOTH (fill both horizontally and vertically).

side − Determines which side of the parent widget packs against: 
    TOP (default), BOTTOM, LEFT, or RIGHT.
"""

class MainWindowICO:
    def __init__(self, master):
        self.master = master
        self.general_setting(master)

        self.pre_init()

        # For logpath notebook and text window
        frame1 = Frame(self.master, width=self.w*3/4, relief=RIDGE, borderwidth=0)
        frame1.pack(fill=BOTH, expand=YES, side=LEFT)
        
        # For logpath and notebook
        frame1_1 = Frame(frame1, relief=RIDGE, borderwidth=0)
        frame1_1.pack(fill=BOTH, expand=NO, side=TOP)
        
        frame_logpath = Frame(frame1_1, relief=RIDGE, borderwidth=2)
        frame_logpath.pack(fill=X, expand=NO, side=TOP, ipady=5)
        frame_notebook = Frame(frame1_1, relief=RIDGE, borderwidth=2)
        frame_notebook.pack(fill=BOTH, expand=NO, side=TOP)

        self.variable = StringVar()
        Label(frame_logpath, text=" Log Path: ").pack(fill=NONE, expand=False, side=LEFT)
        #self.entry_logpath = Entry(frame_logpath)
        #self.entry_logpath.pack(fill=X, expand=YES, side=LEFT)
        self.logs_history = Combobox(frame_logpath, textvariable=self.variable)
        self.cur_history = read_history()
        if len(self.cur_history) == 0:
            self.cur_history = ["logs"]
        self.logs_history['values'] = self.cur_history
        self.logs_history.current(0)
        self.logs_history.pack(fill=X, expand=YES, side=LEFT)
        self.logs_history.bind("<<ComboboxSelected>>", self.logs_selected)

        self.path_select = Button(frame_logpath, text ='Select..',
                               command=self.selectPath)
        self.path_select.pack(fill=NONE, expand=False, side=LEFT, padx=10)
        #Label(frame_logpath, text="     ").pack(fill=NONE, expand=False, side=LEFT)
        # Notebook
        # padding: the distance away from the parent frame
        note = Notebook(frame_notebook)
        note.enable_traversal()
        note.pack(fill=BOTH, expand=YES, side=LEFT)
        
        tab_main = Frame(note)
        tab_power = Frame(note)
        tab_perf = Frame(note)
        tab_stab = Frame(note)
        tab_log = Frame(note)
        tab_misc = Frame(note)
        note.add(tab_main, text="  Main  ")
        note.add(tab_power, text="  Power/Thermal  ")
        note.add(tab_perf, text="  Perf  ")
        note.add(tab_stab, text="  Stablility  ")
        note.add(tab_log, text="  Log Function  ")
        note.add(tab_misc, text="  Misc  ")
        
        Button(tab_main, text ='button1.1', command=self.master.destroy).grid(row=0, column=0)
        Button(tab_main, text ='button1.2').grid(row=0, column=1)
        Button(tab_main, text ='button1.3').grid(row=0, column=2)
        Button(tab_power, text ='button2.1').grid(row=0, column=0)
        Button(tab_power, text ='button2.2').grid(row=0, column=1)
        Button(tab_power, text ='button2.3').grid(row=0, column=2)
        Button(tab_perf, text ='button3.1').grid(row=0, column=0)
        Button(tab_perf, text ='button3.2').grid(row=0, column=1)
        Button(tab_perf, text ='button3.3').grid(row=0, column=2)
        self.ADB_PULL = Button(tab_log, text ='抓取日志', command=self.adb_pull_logs)
        self.ADB_PULL.grid(row=0, column=0)

        self.ANALYZE = Button(tab_log, text ='分析日志', command=self.analyze)
        self.ANALYZE.grid(row=0, column=1)

        self.JOIN = Button(tab_log, text ='合并日志', command=self.join_log)
        self.JOIN.grid(row=0, column=2)

        self.OPEN_LOG_DIR = Button(tab_log, text ='打开日志', command=self.open_log_dir)
        self.OPEN_LOG_DIR.grid(row=0, column=3)

        Button(tab_misc, text ='DigitalClock', command=self.create_misc_clocks).grid(row=0, column=0)
        Button(tab_misc, text ='misc.2').grid(row=0, column=1)
        Button(tab_misc, text ='misc.3').grid(row=0, column=2)
        
        frame1_2 = Frame(frame1, relief=RIDGE, borderwidth=1)
        frame1_2.pack(fill=BOTH, expand=YES, side=TOP, ipadx=2, ipady=2)

        self.text = Text(frame1_2, wrap='word')
        ybar = Scrollbar(frame1_2, orient=VERTICAL, command=self.text.yview )
        self.text.configure(yscrollcommand=ybar.set)
        self.text.pack(side=LEFT, expand=YES, fill=BOTH)
        ybar.pack(side=RIGHT, fill=Y)
        
        frame2 = Frame(self.master, relief=RIDGE, borderwidth=1)
        frame2.pack(fill=BOTH, ipadx=2, ipady=2, expand=NO, side=RIGHT)
        self.listbox = Listbox(frame2)
        ybar_frame2 = Scrollbar(frame2, orient=VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=ybar_frame2.set)
        self.listbox.pack( side=LEFT, expand=YES, fill=BOTH)
        ybar_frame2.pack( side=RIGHT, fill=Y)
        self.bug_list = []
        self.update_bug_list()
        self.listbox.bind("<Double-Button-1>", self.ok)
        
        #frame3 = Frame(self.master, relief=RIDGE, borderwidth=1)
        #frame3.pack(fill=BOTH, ipadx=2, ipady=2, expand=True, side=BOTTOM)
        #label = Label(frame3, text='status', relief=SUNKEN,anchor=W)  # anchor left align W -- WEST
        #label.pack(side=BOTTOM,fill=X)

        self.post_init()

    def general_setting(self, root):        
        info("***general_setting")
                #print(tkFont.families())
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family='Microsoft YaHei', size=10)
        
        self.w = 800
        self.h = 480
        root.title('Main Window of ICO')
        #root.resizable(width=False, height=False)
        root.geometry('%dx%d+200+100' % (self.w, self.h))
        # Set the minum size of the window
        root.minsize(self.w, self.h)
        # replace the tkinter ico
        #root.iconbitmap('c:\\test\\48X48_tk_logo.ico')
        #root.rowconfigure(0, weight=1)
        #root.columnconfigure(0, weight=1)
        
        # font to use for label widgets
        #root.option_add("*Font", "courier 12 bold")
        #root.option_add("*Button*Font", "courier 12 bold")
        root.option_add("*Font", default_font)
        
        # make all widgets light blue
        root.option_add("*Background", "light blue")
        # use gold/black for selections
        root.option_add("*selectBackground", "gold")
        root.option_add("*selectForeground", "black")
        # the root window was already created, so we
        # have to update it ourselves
        root.config(background="light blue")

    def pre_init(self):
        self.create_thread()
        self.message = {}

    def post_init(self):
        # TBD
        info("post_init()")

    def button_browse_callback(self):
        """ What to do when the Browse button is pressed """
        options = {}
        options['initialdir'] = '.'
        options['title'] = 'Select the log directory'
        options['mustexist'] = False
        self.fileName = FileDiag.askdirectory(**options)
        info("***%s" % self.fileName)
        if self.fileName == "":
            return None
        else:
            return self.fileName

    def logs_selected(self, *args):
        path_ = self.logs_history.get()
        if len(path_) > 0:
            self.update_history(path_)

    def update_bug_list(self):
        self.listbox.delete(0, END)
        for item in self.bug_list:
            self.listbox.insert(END, item)

    def ok(self, event):
        info(self.listbox.index(ANCHOR))
        info(self.listbox.get(ANCHOR))
        lines = get_bug_info(self.listbox.get(ANCHOR))
        self.text.delete(1.0, END)
        s = ""
        for l in self.bug_results_info:
            s += l
        s += "======================================================================================================\n\n\n"
        # for l in lines:
        #     s += l
        self.text.insert('insert', s)
        self.text.tag_config("blue", foreground="blue")
        self.text.tag_config("red", foreground="red")
        rules = read_rules()
        for l in lines:
            # a = color_keyword("", l, rules)
            a = color_all_keyword("", l, rules)
            if not a:
                self.text.insert('insert', l)
                continue
            for (c, m) in a:
                if c:
                    self.text.insert('insert', m, c)
                else:
                    self.text.insert('insert', m)

    def update_history(self, path_):
        self.variable.set(path_)
        if len(self.cur_history) > 10:
            self.cur_history.pop()
        if path_ in self.cur_history:
            self.cur_history.remove(path_)
        self.cur_history.insert(0, path_)
        self.logs_history['values'] = self.cur_history
        self.logs_history.current(0)
        write_history(self.cur_history)

    def selectPath(self):
        path_ = FileDiag.askdirectory()
        if len(path_) > 0:
            self.update_history(path_)
        info(path_)

    def adb_pull_logs(self):
        info("message begin")
        self.message["catch logs"] = self.adb_pull_fn
        self.queue.put("catch logs")
        info("message")

    def adb_pull_fn(self):
        path_ = os.getcwd() + os.sep + "logs" + os.sep + time.strftime("%Y%m%d-%H%M%S", time.localtime())
        self.text.delete(1.0, END)
        info("path_ %s" % path_)
        self.text.insert('insert', path_ + "\n")
        # self.text.update()
        # os.system("adb pull /cache/logs/ "+path_)
        self.ADB_PULL.config(state=DISABLED, text="抓取中...")
        self.ANALYZE.config(state=DISABLED)
        self.path_select.config(state=DISABLED)

        if not connectDevcie():
            self.text.insert(END, "***adb端口没有找到，请检查设备连接状态\n")
            self.text.see(END)
            self.ADB_PULL.config(state=NORMAL, text="抓取日志")
            self.ANALYZE.config(state=NORMAL, text="分析")
            self.path_select.config(state=NORMAL, text="路径选择")
            return

        cmd = "adb pull /cache/logs/ " + path_
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        for l in p.stdout:
            info(l)
            self.text.insert(END, l)
            # self.text.update()
            self.text.see(END)
        self.text.insert(END, "抓取日志完成\n")
        self.text.see(END)
        self.ADB_PULL.config(state=NORMAL, text="抓取日志")
        self.ANALYZE.config(state=NORMAL, text="分析")
        self.path_select.config(state=NORMAL, text="路径选择")
        self.variable.set(path_)
        info(path_)

    def quit(self):
        self.master.quit()

    def cancel(self):
        self.master.quit()

    def get_bug_list(self, lines):
        filename = "out" + os.sep + "result.txt"
        if not os.path.isfile(filename):
            return []
        with open(filename, "r") as f:
            return [line.strip() for line in f.readlines()]

    def analyze(self):
        self.message["analyze logs"] = self.analyze_fn
        self.queue.put("analyze logs")

    def join_log(self):
        self.message["join logs"] = self.join_fn
        self.queue.put("join logs")

    def open_log_dir(self):
        self.message["open log dir"] = self.open_log_dir_fn
        self.queue.put("open log dir")

    def analyze_fn(self):
        remove_files("out")
        log_dir = self.variable.get()
        if not log_dir:
            self.bug_results_info = []
            self.bug_list = []
            self.update_bug_list()
            self.text.delete(1.0, END)
            self.text.tag_config("a", foreground="red")
            self.text.insert(END, "日志不存在\n", "a")
            return

        if log_dir not in self.cur_history:
            self.update_history(log_dir)

        self.config_button(DISABLED)
        self.text.delete(1.0, END)
        self.text.insert(END, self.variable.get() + "\n")

        cmd = PYTHON_CMD + "main.py --skip=Non-protected-broadcast,JankyFrame -o out " + log_dir
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        lines = []
        while True:
            l = p.stdout.readline()
            if not l:
                break
            # info(l)
            self.text.insert(END, l)
            self.text.see(END)
            lines.append(l)
        self.text.insert(END, "\n完成\n")
        # self.text.tag_add('tag1', 1.2, 1.7)
        # self.text.tag_config('tag1',background='yellow',foreground='red')
        # self.text.tag_add('tag1', 2.2, 2.7)
        # self.text.tag_config('tag1',background='yellow',foreground='red')
        self.bug_results_info = lines
        self.bug_list = self.get_bug_list(lines)
        self.update_bug_list()
        self.config_button(NORMAL)

    def join_fn(self):
        info("enter join_fn()")
        log_dir = self.variable.get()
        if not log_dir:
            self.bug_results_info = []
            self.bug_list = []
            self.update_bug_list()
            self.text.delete(1.0, END)
            self.text.tag_config("a", foreground="red")
            self.text.insert(END, "日志不存在\n", "a")
            return
        self.text.insert(END, "\ntest1\n")
        if log_dir not in self.cur_history:
            self.update_history(log_dir)
        self.text.insert(END, "\ntest2\n")
        self.config_button(DISABLED)
        self.text.delete(1.0, END)
        self.text.insert(END, u"日志路径：" + self.variable.get() + "\n")

        self.text.insert(END, "***开始合并日志，请稍等片刻...\n")
        self.text.see(END)
        import extract_log
        extract_log.main(log_dir)

        self.text.insert(END, "***完成\n")
        self.text.see(END)
        self.config_button(NORMAL)
        info("try to open %s" % log_dir)
        # os.system("start "+"\""+log_dir+"\"")
        os.startfile(log_dir)
        info("open end %s" % log_dir)

    def open_log_dir_fn(self):
        log_dir = self.variable.get()
        if not log_dir:
            self.bug_results_info = []
            self.bug_list = []
            self.update_bug_list()
            self.text.delete(1.0, END)
            self.text.tag_config("a", foreground="red")
            self.text.insert(END, "日志不存在\n", "a")
            return

        if log_dir not in self.cur_history:
            self.update_history(log_dir)
        os.startfile(log_dir)

    def create_thread(self):
        self.thread_exit = False
        self.queue = Queue.Queue()
        self.t = threading.Thread(target=loop, name='LoopThread', args=(self,))
        self.t.start()

    def destroy(self):
        # self.t.
        self.thread_exit = True
        self.queue.put("")

    def config_button(self, state):
        self.ADB_PULL.config(state=state)
        self.ANALYZE.config(state=state)
        self.JOIN.config(state=state)
        self.OPEN_LOG_DIR.config(state=state)
        self.path_select.config(state=state)

    def create_misc_clocks(self):
        import misc_clock
        top = Toplevel()
        top.title('Digital Clock')
        misc_clock.Clock(top, 200, 200, 400, 400, 150)

def remove_files(dirname):
    if not os.path.isdir(dirname):
        return
    lfiles = [dirname + os.sep + i for i in os.listdir(dirname)]
    for f in lfiles:
        os.remove(f)

def read_files(filename):
    if not os.path.isfile(filename):
        info("%s not exist" % filename)
        return []
    with open(filename, "r") as f:
        return f.readlines()

def write_file(filename, lines):
    with open(filename, "w+") as f:
        f.writelines(lines)

def get_bug_info(line):
    ss = line.split()[0]
    bug_filename = ss.replace("/", "-").replace(" ", "").replace(":", "")
    info("bug_filename=%s" % bug_filename)
    return read_files("out" + os.sep + bug_filename + ".txt")

def loop(argv):
    t = argv
    info(t)
    while not t.thread_exit:
        event = t.queue.get()
        info("Receive event=%s" % event)
        if t.message.has_key(event):
            t.message[event]()
        info("End event=%s" % event)

def read_history():
    h = "ss_config" + os.sep + "logs_history.txt"
    if os.path.isfile(h):
        lines = read_files(h)
        history = []
        for l in lines:
            l = l.strip()
            if l == "":
                continue
            history.append(l)
        return history
    return []

def write_history(lines):
    h = "ss_config" + os.sep + "logs_history.txt"
    write_file(h, [l + "\n" for l in lines])

def ss_init():
    if not os.path.isdir("ss_config"):
        os.mkdir("ss_config")

def read_rules():
    rules = []
    rule_file = "config" + os.sep + "key_description.txt"
    if not os.path.isfile(rule_file):
        return rules
    lines = read_files(rule_file)
    nrule = None
    for l in lines:
        # print l
        l = l.strip()
        if l == "":
            continue
        if l.startswith("rule"):
            nrule = {"rule": ""}
            rules.append(nrule)
        if not nrule:
            continue
        index = l.find(" ")
        if index <= 0:
            nrule[l] = ""
            continue
        if l[0:index] == "keyword":
            if nrule.has_key(l[0:index]):
                nrule[l[0:index]].append(l[index + 1:])
            else:
                nrule[l[0:index]] = [l[index + 1:]]
        elif l[0:index] == "regular":
            info("found regular %s" % l[index + 1:].strip())
            nrule[l[0:index]] = re.compile(l[index + 1:].strip())
        else:
            nrule[l[0:index]] = l[index + 1:]
    return rules


def color_keyword(bug_type, line, rules):
    def find_keyword(line, ks):
        for k in ks:
            if line.find(k) >= 0:
                return k
        return None

    line = line.strip("\n")
    for r in rules:
        ks = r["keyword"] if r.has_key("keyword") else []
        c = r["color"] if r.has_key("color") else "red"
        m = r["desc"] if r.has_key("desc") else ""
        regular = r["regular"] if r.has_key("regular") else None
        k = None
        if regular:
            s = regular.search(line)
            if s:
                k = find_keyword(line, s.groups())
        else:
            k = find_keyword(line, ks)
        if not k:
            continue
        a = line.split(k)
        lines = [(None, a[0])]
        for i in a[1:]:
            lines.append((c, k))
            lines.append((None, i))
        lines.append((c, m + "\n"))
        return lines
    return None

def color_all_keyword(bug_type, line, rules):
    def find_keyword(line, ks):
        for k in ks:
            if line.find(k) >= 0:
                return k
        return None

    def color(bug_type, cw, rules, message):
        keywords = []
        for e in cw:
            (c0, w0) = e
            if c0:
                keywords.append([c0, w0])
                continue

            for r in rules:
                ks = r["keyword"] if r.has_key("keyword") else []
                c = r["color"] if r.has_key("color") else "red"
                m = r["desc"] if r.has_key("desc") else ""
                regular = r["regular"] if r.has_key("regular") else None
                k = None
                if regular:
                    s = regular.search(w0)
                    if s:
                        k = find_keyword(w0, s.groups())
                else:
                    k = find_keyword(w0, ks)
                if not k:
                    continue
                a = w0.split(k)
                keywords.append((None, a[0]))
                for i in a[1:]:
                    keywords.append((c, k))
                    keywords.append((None, i))
                message[0] += m
                break
            else:
                keywords.append((c0, w0))
        if len(cw) == len(keywords):
            return keywords
        else:
            return color(bug_type, keywords, rules, message)

    line = line.strip("\n")
    s = [""]
    ws = color(bug_type, [(None, line)], rules, s)
    for (c, l) in ws:
        if c:
            break
    ws.append((c, s[0] + "\n"))
    return ws

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    ss_init()
    root = Tk()
    app = MainWindowICO(root)
    root.mainloop()
    app.destroy()
