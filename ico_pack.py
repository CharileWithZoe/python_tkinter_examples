import sys

if sys.version_info < (3,0,0):
    sys.stdout.write("***python2\n")
    from Tkinter import *
    from ttk import * 
    import tkFont
else:
    sys.stdout.write("***python3\n")
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.font as tkFont

"""
Using pack() to manager the layout of tk window
expand: YES NO
fill: X Y BOTH NONE
"""
root = Tk()

# Change the default font to the font you like
#print(tkFont.families())
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(family='微软雅黑', size=10)

root.title('Main Window of ICO')
root.resizable(width=False, height=False)
root.geometry('800x480+200+100')
root.minsize(800, 480)
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
# the root window was already created, so we have to update it ourselves
root.config(background="light blue")

frame1 = Frame(root, height=480, width=600, relief=RIDGE, borderwidth=0)
frame1.pack(fill=BOTH, expand=YES, side=LEFT)

frame1_1 = Frame(frame1, height=100, width=600, relief=RIDGE, borderwidth=0)
frame1_1.pack(fill=NONE, expand=False, side=TOP)
# Notebook
# padding: the distance away from the parent frame
note = Notebook(frame1_1, height=100, width=600)
note.enable_traversal()
note.pack(side=LEFT, fill=X)

tab_main = Frame(note)
tab_power = Frame(note)
tab_perf = Frame(note)
tab_stab = Frame(note)
tab_log = Frame(note)
Button(tab_main, text ='button1.1', command=root.destroy).grid(row=0, column=0)
Button(tab_main, text ='button1.2').grid(row=0, column=1)
Button(tab_main, text ='button1.3').grid(row=0, column=2)
Button(tab_power, text ='button2.1').grid(row=0, column=0)
Button(tab_power, text ='button2.2').grid(row=0, column=1)
Button(tab_power, text ='button2.3').grid(row=0, column=2)
Button(tab_perf, text ='button3.1').grid(row=0, column=0)
Button(tab_perf, text ='button3.2').grid(row=0, column=1)
Button(tab_perf, text ='button3.3').grid(row=0, column=2)
note.add(tab_main, text="  Main  ")
note.add(tab_power, text="  Power/Thermal  ")
note.add(tab_perf, text="  Perf  ")
note.add(tab_stab, text="  Stablility  ")
note.add(tab_log, text="  Log Function  ")

frame1_2 = Frame(frame1, height=300, width=600, relief=RIDGE, borderwidth=1)
frame1_2.pack(fill=BOTH, ipadx=2, ipady=2, expand=False, side=TOP)
#Button(frame1_2, text ='frame1_2 button').pack(side=LEFT, expand=Y)

frame1_3 = Frame(frame1, height=80, width=600, relief=RIDGE, borderwidth=0)
frame1_3.pack(fill=BOTH, ipadx=2, ipady=2, expand=False, side=TOP)
# LogPath Entry
Label(frame1_3, text=" Log Path: ").pack(side=LEFT)#第一行
entry_logpath = Entry(frame1_3)
entry_logpath.pack(side=LEFT, fill=X)

frame2 = Frame(root, height=480, width=200, relief=RIDGE, borderwidth=1)
frame2.pack(fill=NONE, ipadx=2, ipady=2, expand=False, side=RIGHT)

root.mainloop()
exit()
