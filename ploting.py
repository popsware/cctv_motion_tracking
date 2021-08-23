# libraries
import matplotlib.pyplot as plt
import numpy as np

# create data


plt.title('timtle nae')
plt.xlabel('xAxis name')
plt.ylabel('yAxis name')


#y = np.random.random([10, 1])
#values = np.cumsum(np.random.randn(50, 1))
values = [10, 13, 15, 2, 10, 14, 20, 21]
print(values)
plt.plot(values)


plt.pause(4)
values.append(13)
print(values)
# plt.clf()
plt.plot(values)


plt.pause(4)
plt.plot(100, 100)


# plt.show()  # blocks the script untill window is closed
