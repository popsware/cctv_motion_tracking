# libraries
import plotly.graph_objects as go
import plotly.express as px
import datetime
import sys
import numpy as np
from tkinter import *
from tkinter import simpledialog

if len(sys.argv) > 1:
    targetcam = sys.argv[1]
else:
    ROOT = Tk()
    ROOT.withdraw()
    # the input dialog
    targetcam = simpledialog.askstring(
        title="Which cam ?", prompt="Camera Name [nole1,nole2,...,dawara]:"
    )


OPTIONS = ["log_motion", "log_globalstatechange", "log_deepsleep"]  # etc

master = Tk("Choose the log file")
master.geometry("600x100")
master.title("Choose the log file")

variable = StringVar(master)
variable.set(OPTIONS[0])  # default value

w = OptionMenu(master, variable, *OPTIONS)
w.pack()

targetfile = ""


def ok():
    print("value is:" + variable.get())
    targetfile = variable.get()


button = Button(master, text="OK", command=ok)
button.pack()

mainloop()

# Grabbing the data

filename = "..\logs\\motion_tracking\\" + targetfile + "_" + targetcam + ".log"
indecies = []
dates = []
numbers = []
with open(filename) as file_object:
    for index, line in enumerate(file_object):
        rowelements = line.split()
        datestring = rowelements[0] + " " + rowelements[1]
        m_date = datetime.datetime.strptime(datestring, "%Y/%m/%d %H:%M:%S")
        m_float = float(rowelements[2])
        # print(index, m_date, m_float)
        indecies.append(index)
        dates.append(m_date)
        numbers.append(m_float)
        # plt.plot(index, m_float, 'bo')

# Plotting the data


# Using the plotly library to display plot in a browser

# fig = go.Figure(data=go.Scatter(x=dates, y=numbers))
fig = go.Figure(data=px.area(x=dates, y=numbers))
# Set title
fig.update_layout(title_text="Motion Detection on " + targetcam)
# Add range slider
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=4, label="4h", step="hour", stepmode="backward"),
                    dict(count=12, label="shift", step="hour", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(step="all"),
                ]
            )
        ),
        rangeslider=dict(visible=True),
        type="date",
    )
)

fig.write_html(
    "logs\motion_tracking\chart_motion_" + targetcam + ".html", auto_open=True
)
