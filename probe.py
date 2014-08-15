# probe.py

import serial
import re
import time
import os.path
import sys

# Margin from border to first measure in nn
border=10
# Nmber of probes in each direction
nProbesX = 4
nProbesY = 4
fileName='probes.csv'
# Desired hot end temperature (None - use current)
temp = None

# Flying level of hot end
level=5

zposPat = re.compile('Bed Position X: ([0-9.-]+) +Y: ([0-9.-]+) +Z: ([0-9.-]+)')
tempPat = re.compile('ok T:([0-9.]+) /([0-9.]+) B:([0-9.]+) /([0-9.]+) T.+')
zoffsetPat = re.compile('echo:  M212 X([0-9.-]+) +Y([0-9.-]+) +Z([0-9.-]+)')
sizePat = re.compile('echo:  M211 X([0-9.-]+) +Y([0-9.-]+) +Z([0-9.-]+)');


class Handler:
  """ State and communication with the PrintrBot Meta Simple """

  s = None
  z = None
  t = None
  b = None
  # From M212 echo of M503
  zOffset = None  
  # from M212 echo of M503
  xMax = None  
  yMax = None

  def connect(self, port = '/dev/ttyACM0', baudrate = 250000, callbackObject = None):
    self.s = serial.Serial(str(port), baudrate, timeout=10000, writeTimeout=10000)

  def close(self):
    if self.s is not None:
      self.s.close()
      self.s = None

  def readLine(self):
    return self.s.readline().rstrip()


  def sendCmd(self,cmd):
   self.s.write(cmd + '\n')


  def doCmd(self,cmd):
   print 'Send: ' + cmd
   self.sendCmd(cmd)
   line = ''
   while not line.startswith('ok'):
      line = self.readLine()
      print 'Recd: ' + line
      m = zposPat.match(line)
      if m:
         print '--- Z: ' + m.group(3)
         self.z = m.group(3)
      m = tempPat.match(line)
      if m:
        print '--- TEMP extruder: ' + m.group(1) + ', bed: ' + m.group(3)
        self.t = m.group(1)
        self.b = m.group(3)
      m = zoffsetPat.match(line)
      if m:
         print '--- Z offset: ' + m.group(3)
         self.zOffset = m.group(3)
      m = sizePat.match(line)
      if m:
         print '--- xMax: ' + m.group(1) + ', yMax:' + m.group(2)
         self.xMax = float(m.group(1))
         self.yMax = float(m.group(2))

  def probePoint(self,x,y):
    self.z = None
    self.t = None
    self.b = None
    self.doCmd('G0 Z' + str(level)) # Lift
    self.doCmd('G0 X' +  "{:4.2f}".format(x) + ' Y'+  "{:4.2f}".format(y)) # Move to probe position
    self.doCmd('M114') # Show current pos
    self.doCmd('G30')  # Probe z
    self.doCmd('M105') # Probe temperatures
  

now = time.strftime("%Y-%m-%d %H:%m:%S")

h = Handler()

print 'Connecting at ' + now
h.connect()
print "INTITIALIZE:"
h.doCmd('G21')  # metric values (mm)
h.doCmd('M107') # fan off
# Move the Z a little bit higher to avoid tuching bed during homing
h.doCmd('G91') # relative
h.doCmd('G0 Z3') # safer Z location
h.doCmd('G90')  # absolute
# Home
h.doCmd('G28 X0 Y0')   #Home
h.doCmd('G28 Z0')
h.doCmd('G1 F5000') # Speed for move
# Get initial state
print "STATE:"
h.doCmd('M503')  # Status general (aslo get xMax and yMay)
if h.xMax is None or h.yMax is None:
   print 'Could not read xMax/yMax from M503 response'
   sys.exit(1)

xpos = []
for i in range(nProbesX):
   xpos.append(border+i*(h.xMax-2*border)/(nProbesX-1))

ypos = []
for i in range(nProbesY):
   ypos.append(border+i*(h.yMax-2*border)/(nProbesY-1))


h.doCmd('M105') # Show curent temperature
if h.t is None:
   print 'Could not read temperature from M105 response'
   sys.exit(1)

if (not temp is None) and (temp > 0):
   print "--- SET TEMP " + str(temp)
   if h.t > temp + 5 and h.t > 30:
      h.doCmd('M106 S255') # Fan on to cool faster
   h.doCmd('M109 S'+str(temp))
   # Wait for temp also if cooling, also this seems to be done by M109 anyhow
   while True:
      h.doCmd('M105')
      if abs((float(t)-temp)) < 1.5:
          break
      time.sleep(2)
   h.doComd('M107') # fan off

   
if h.zOffset is None:
   print "z offset (M212) not parsed"
   h.zOffset = ''     # To avoid error in print

newFile = not os.path.isfile(fileName)

with open(fileName, 'a') as results:
  if newFile:
    print '--- Created file ' + fileName
    results.write('"date/time","X","Y","Z offset","Extr. Temp","Bed Temp","Z probe"\n')
  else:
    print '--- Appending to file '  + fileName
  print 'PROBING:'
  for x in xpos:
    for y in ypos:
      h.probePoint(x, y)
      print '>>> ' + now + ',' +  "{:4.2f}".format(x) + ',' +  "{:4.2f}".format(y) + ',' + h.zOffset + ',' + h.t + ',' + h.b + ',' + h.z
      results.write(now + ',' +  "{:4.2f}".format(x) + ',' +  "{:4.2f}".format(y) + ',' + h.zOffset + ',' + h.t +  ',' + h.b + ',' + h.z + '\n')

h.doCmd('G0 Z10') # lift
if (not temp is None):
   h.doCmd('M104 S0')  # Cool down
h.doCmd('M84') # Disable motors

h.close()

print 'Terminated sucessfuly'
