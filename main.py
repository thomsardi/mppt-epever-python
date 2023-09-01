from mpptepveper.mppt_epveper import MPPTEPVEPER
from base import ParameterSetting, ParserSetting
import json
import time
from typing import List

if __name__ == "__main__" :
   file = json.load(open('register_config.json')) #convert the json file into dict
   port = file['port'] #get port name from register_config.json file
   mppt =  MPPTEPVEPER(port=port, timeout=0.1) #setup modbus with specified port, 115200 baudrate, 0.1s timeout
   parser = ParserSetting() #create ParserSetting object
   dummy : List[ParameterSetting] = parser.parse(file) #get value from "parameter" key 
   # print(len(dummy))
   for a in dummy :
      isSameFlag = mppt.isSameSetting(a) #check for equalness of setting parameter
      if (isSameFlag == 0) : #different setting
         print("Writing new setting")
         mppt.setBulkParameter(a)
      elif (isSameFlag == 1) : #same setting
         print("Same Setting")
      else : #different type
         print("different type")

   print(mppt.startScan(1,5)) #start id scan
   
   if (mppt.setLoadOn(1)) : #set load on
      print("Success set load at id ", 1)
   else :
      print("Failed set load at id ", 1)
   time.sleep(0.2)
   print(mppt.getAllPVInfo(1)) #get pv info
   time.sleep(0.2)
   print(mppt.getGeneratedEnergy(1)) #get generated energy
   time.sleep(0.2)
   print(mppt.getBatteryInfo(1)) #get battery info
   time.sleep(0.2)
   print(mppt.getLoadInfo(1)) #get load info
   time.sleep(0.2)
   print(mppt.getBatterySoc(1)) #get battery state of charge
   time.sleep(0.2)
   print(mppt.getTemperatureInfo(1)) #get temperature
   time.sleep(0.2)
   print(mppt.getStatusInfo(1)) #get alarm
   time.sleep(0.2)
   print(mppt.getChargingState(1)) #get charge state
   time.sleep(0.2)
   print(mppt.getRatedChargingCurrent(1)) #get rated charge current
   time.sleep(0.2)
   print(mppt.getRatedLoadCurrent(1)) #get rated load current
   time.sleep(0.2)
   print(mppt.getDischargingState(1)) #get discharge state

   if (mppt.setLoadOff(1)) : #set load off
      print("Success set load at id ", 1)
   else :
      print("Failed set load at id ", 1)
   time.sleep(0.2)
   print(mppt.getAllPVInfo(1))
   time.sleep(0.2)
   print(mppt.getGeneratedEnergy(1))
   time.sleep(0.2)
   print(mppt.getBatteryInfo(1))
   time.sleep(0.2)
   print(mppt.getLoadInfo(1))
   time.sleep(0.2)
   print(mppt.getBatterySoc(1))
   time.sleep(0.2)
   print(mppt.getTemperatureInfo(1))
   time.sleep(0.2)
   print(mppt.getStatusInfo(1))
   time.sleep(0.2)
   print(mppt.getChargingState(1))
   time.sleep(0.2)
   print(mppt.getRatedChargingCurrent(1))
   time.sleep(0.2)
   print(mppt.getRatedLoadCurrent(1))
   time.sleep(0.2)
   print(mppt.getDischargingState(1))
   
    