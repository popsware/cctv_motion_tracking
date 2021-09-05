# libraries
import datetime
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import tkinter as tk
from tkinter import simpledialog

if len(sys.argv) > 1:
    targetcam = sys.argv[1]
else:
    ROOT = tk.Tk()
    ROOT.withdraw()
    # the input dialog
    targetcam = simpledialog.askstring(
        title="Which cam ?", prompt="Camera Name [nole1,nole2,...,dawara]:")


dates = []
numbers = []
with open("logs_motion\log_motion_writefile_"+targetcam+".txt") as file_object:
    for index, line in enumerate(file_object):
        rowelements = line.split()
        datestring = rowelements[0]+" "+rowelements[1]
        m_date = datetime.datetime.strptime(
            datestring, '%Y/%m/%d %H:%M:%S')
        m_float = float(rowelements[2])
        #print(index, m_date, m_float)
        dates.append(m_date)
        numbers.append(m_float)
        # plt.plot(index, m_float, 'bo')


fig, ax = plt.subplots()
ax.set(xlabel='Start: '+str(dates[0])+'\n  End:'+str(dates[len(dates)-1]),
       ylabel="Motion Detected",
       title='Motion of '+targetcam)
ax.plot(dates, numbers)

myFmt = mdates.DateFormatter('%d %H:%M')
ax.xaxis.set_major_formatter(myFmt)

# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
fig.autofmt_xdate()

plt.show()
