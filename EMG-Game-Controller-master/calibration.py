import serial       # Import serial module

## Set number of samples to be written to file ##
# sampleCount = 1
# sampleEnd = 1000

## Conversion constants ##
voltUnit = 3.3 / 1024
accelRange = 2
gyroRange = 250

## Function to convert raw analog values to V ##
def convertAnalog(nRaw):
    analogScaled = int(nRaw) * voltUnit
    return analogScaled

## Function to convert raw accelerometer values to g ##
def convertAccel(aRaw):
    accelScaled = ((int(aRaw) / 32768.0) * accelRange)
    return accelScaled

## Function to convert raw gyroscope values to */s ##
def convertGyro(gRaw):
    gyroScaled = (int(gRaw) / 32768.9) * gyroRange
    return gyroScaled

## Function to convert microseconds to milliseconds $$
def convertTime(microS):
    timeScaled = microS * 0.001
    return timeScaled

################################################################################

ser = serial.Serial("/dev/cu.usbmodem1411")     # Open serial port

print "Please input file name: "   
OpenSignal# Ask for a file name
myFile = raw_input()                    # Get user input
f = open(myFile, "w")                   # Open file

print ser.readline()                    # Print welcome message
print ser.readline()

keyPress = raw_input()                  # Get key press from user and write to serial port
ser.write(keyPress)

## Write serial outputs to file ##
while(1):
    try:
        # ## Analog sensor ##
        # if keyPress == "n":
        #     myLine = ser.readline()
        #     myLine = myLine.split()
        #     print myLine
        #     if len(myLine) == 0:
        #         pass
        #     else:
        #         f.write("Sample number: %s" % myLine[0])
        #         f.write("\n")
        #         f.write("Analog (V): ")
        #         for index in range(1, 4):
        #             f.write(" ")
        #             f.write(convertAnalog(myLine[index]))
        #         f.write("\n")
        #         f.write("Time since last sample (ms): %s" % convertTime(int(myLine[4])))
        #         f.write("\n")
        #         f.write("------------------------------------------------------------")
        #         f.write("\n")

        ## Accelerometer ##
        if keyPress == "a":
            myLine = ser.readline()
            myLine = myLine.split()
            # print myLine
            if len(myLine) == 0:
                pass
            else:
                ax = convertAccel(myLine[1])
                ay = convertAccel(myLine[2])
                az = convertAccel(myLine[3])
                am = (ax**2 + ay**2 + az**2)**(0.5)
                print("%r %r" % (time, am))
                f.write(time)
                f.write(" ")
                f.write("%f" % am)
                # print ("%r %r %r" %(ax, ay, az))
                f.write("\n")

        ## Gyroscope ##
        if keyPress == "g":
            myLine = ser.readline()
            myLine = myLine.split()
            # print myLine
            if len(myLine) == 0:
                pass
            else:
                time = myLine[0]
                gx = convertGyro(myLine[1])
                gy = convertGyro(myLine[2])
                gz = convertGyro(myLine[3])
                gm = (gx**2 + gy**2 + gz**2)**(0.5)
                # print(gm)
                print ("%r %r %r %r" %(time, gx, gy, gz))
                f.write(time)
                f.write(" ")
                f.write("%r %r %r" %(gx, gy, gz))
                f.write("\n")


        # sampleCount = sampleCount + 1
    except KeyboardInterrupt:
        f.close()
