import matplotlib.pyplot as plt                 # Import matplotlib module

time = []
boxCar = []
am = []
gy = []
gz = []
buttonPush = []

threshold_mV = 0.15
threshold_rotate_us = 700000

################################################################################
print "Please input name of data file: "
myFile = raw_input()
f = open(myFile, "r")

# time, analog, am, gy, gz

myLine = 1
while myLine:
    myLine = f.readline()
    myLine = myLine.split()
    print myLine
    for index in range(0, len(myLine)):
        time.append(float(myLine[0]))
        boxCar.append(float(myLine[1]))
        am.append(float(myLine[2]))
        gy.append(float(myLine[3]))
        gz.append(float(myLine[4]))

for index in range(0, len(boxCar)):
    if boxCar[index] >= threshold_mV:
        buttonPush.append(1)
    else:
        buttonPush.append(0)

################################################################################
plt.figure(1)
plt.subplot(2, 1, 1)
plt.plot(time, boxCar)
plt.title("EMG")
plt.xlabel("Time (us)")
plt.ylabel("emg")
plt.subplot(2, 1, 2)
plt.plot(time, buttonPush)
plt.title("Button Push")
plt.xlabel("Time (us)")
plt.ylabel("button push")

plt.figure(2)
plt.subplot(3, 1, 1)
plt.plot(time, am)
plt.title("am")
plt.xlabel("Time (us)")
plt.ylabel("am")
plt.subplot(3, 1, 2)
plt.plot(time, gy)
plt.title("gy")
plt.xlabel("Time (us)")
plt.ylabel("gy")
plt.subplot(3, 1, 3)
plt.plot(time, gz)
plt.title("gz")
plt.xlabel("Time (us)")
plt.ylabel("gz")

plt.show()
