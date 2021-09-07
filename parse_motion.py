# libraries
import plotly.graph_objects as go
import plotly.express as px
import datetime
import sys
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

filename = "logs_motion\log_motion_"+targetcam


# Grabbing the data

indecies = []
dates = []
numbers = []
with open(filename+".txt") as file_object:
    for index, line in enumerate(file_object):
        rowelements = line.split()
        datestring = rowelements[0]+" "+rowelements[1]
        m_date = datetime.datetime.strptime(
            datestring, '%Y/%m/%d %H:%M:%S')
        m_float = float(rowelements[2])
        # print(index, m_date, m_float)
        indecies.append(index)
        dates.append(m_date)
        numbers.append(m_float)
        # plt.plot(index, m_float, 'bo')

# Plotting the data


# Using the plotly library to display plot in a browser

#fig = go.Figure(data=go.Scatter(x=dates, y=numbers))
fig = go.Figure(data=px.area(x=dates, y=numbers))
# Set title
fig.update_layout(
    title_text="Motion Detection on "+targetcam
)
# Add range slider
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1h",
                     step="hour",
                     stepmode="backward"),
                dict(count=4,
                     label="4h",
                     step="hour",
                     stepmode="backward"),
                dict(count=8,
                     label="8h",
                     step="hour",
                     stepmode="backward"),
                dict(count=1,
                     label="1d",
                     step="day",
                     stepmode="backward"),
                dict(count=1,
                     label="YTD",
                     step="year",
                     stepmode="todate"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

fig.write_html(filename+'.html', auto_open=True)
