import sys

if sys.version_info < (3,0,0):
    sys.stdout.write("***python2\n")
    from Tkinter import *
    from ttk import * 
    import tkFont
    import Tkinter.tkFileDialog as FileDiag
else:
    sys.stdout.write("***python3\n")
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.font as tkFont
    import tkinter.filedialog as FileDiag

"""
pack layout：
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
        
        Label(frame_logpath, text=" Log Path: ").pack(fill=NONE, expand=False, side=LEFT)
        self.entry_logpath = Entry(frame_logpath)
        self.entry_logpath.pack(fill=X, expand=YES, side=LEFT)
        self.fileName = ""
        button_browse = Button(frame_logpath, text ='Select..',
                               command=self.button_browse_callback)
        button_browse.pack(fill=NONE, expand=False, side=LEFT, padx=10)
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
        listbox_frame2 = Listbox(frame2)
        ybar_frame2 = Scrollbar(frame2, orient=VERTICAL, command=listbox_frame2.yview)
        listbox_frame2.configure(yscrollcommand=ybar_frame2.set)
        listbox_frame2.pack( side=LEFT, expand=YES, fill=BOTH)
        ybar_frame2.pack( side=RIGHT, fill=Y)
        # test
        listbox_frame2.insert(1, "Python")
        listbox_frame2.insert(2, "Perl")
        listbox_frame2.insert(3, "C")
        listbox_frame2.insert(4, "PHP")
        listbox_frame2.insert(5, "JSP")
        listbox_frame2.insert(6, "Ruby")
        
        #frame3 = Frame(self.master, relief=RIDGE, borderwidth=1)
        #frame3.pack(fill=BOTH, ipadx=2, ipady=2, expand=True, side=BOTTOM)
        #label = Label(frame3, text='status', relief=SUNKEN,anchor=W)  # anchor left align W -- WEST
        #label.pack(side=BOTTOM,fill=X)

    def general_setting(self, root):        
        sys.stdout.write("***general_setting\n")
                #print(tkFont.families())
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family='微软雅黑', size=10)
        
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
        #root.option_add("*Font", default_font)
        
        # make all widgets light blue
        root.option_add("*Background", "light blue")
        # use gold/black for selections
        root.option_add("*selectBackground", "gold")
        root.option_add("*selectForeground", "black")
        # the root window was already created, so we
        # have to update it ourselves
        root.config(background="light blue")

    def button_browse_callback(self):
        """ What to do when the Browse button is pressed """
        options = {}
        options['initialdir'] = '.'
        options['title'] = 'Select the log directory'
        options['mustexist'] = False
        self.fileName = FileDiag.askdirectory(**options)
        sys.stdout.write("***%s\n" % fileName)
        if self.fileName == "":
            return None
        else:
            return self.fileName

    def create_misc_clocks(self):
        import misc_clock
        top = Toplevel()
        top.title('Digital Clock')
        misc_clock.Clock(top, 200, 200, 400, 400, 150)

if __name__ == '__main__':
    root = Tk()
    MainWindowICO(root)
    root.mainloop()
