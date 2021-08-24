# libraries
import datetime
import sys
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) > 1:
    targetcam = sys.argv[1]
else:
    targetcam = "nole1"


plt.title('Motion of '+targetcam)
plt.xlabel('Timeline')
plt.ylabel('Motion Detected')

dates = []
numbers = []
with open("logs_motion\log_motion_"+targetcam+".txt") as file_object:
    for index, line in enumerate(file_object):
        rowelements = line.split()
        datestring = rowelements[0]+" "+rowelements[1]
        m_date = datetime.datetime.strptime(
            datestring, '%Y/%m/%d %H:%M:%S')
        m_float = float(rowelements[2])
        print(index, m_date, m_float)
        dates.append(m_date)
        numbers.append(m_float)
        # plt.plot(index, m_float, 'bo')

plt.plot(dates, numbers)
# plt.axis([-10, 10, 0, 5])
plt.show()
