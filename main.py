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

   for a in dummy : #for loop to write a new setting
      print("Read setting on slave id :", a.id)
      isSameFlag = mppt.checkSetting(a) #check for equalness of setting parameter
      if (isSameFlag == 0) : #different setting
         print("New setting detected.. Writing new setting..")
         if (mppt.setBulkParameter(a)) :
            print("Success writing new setting")
         else :
            print("Failed to write new setting")
      elif (isSameFlag == 1) : #same setting
         print("Same setting.. Skip writing..")
      else : #different type
         print("different type.. Skip writing..")
      time.sleep(0.1) #always add sleep when using modbus within for loop. without sleep, the modbus result always failed

   slaveList = mppt.startScan(1,3) #start id scan
   print("List of connected slave :", slaveList)
   for slave in slaveList :
      params = mppt.getCurrentSetting(slave)
      if (params is not None) :
         params.printContainer()
      if (mppt.setLoadOn(slave)) : #set load on
         print("Success set load on at id", slave)
      else :
         print("Failed set load on at id", slave)
      print(mppt.getAllPVInfo(slave)) #get pv info
      print(mppt.getGeneratedEnergy(slave)) #get generated energy
      print(mppt.getBatteryInfo(slave)) #get battery info
      print(mppt.getLoadInfo(slave)) #get load info
      print(mppt.getBatterySoc(slave)) #get battery state of charge
      print(mppt.getTemperatureInfo(slave)) #get temperature
      print(mppt.getStatusInfo(slave)) #get alarm
      print(mppt.getChargingState(slave)) #get charge state
      print(mppt.getRatedChargingCurrent(slave)) #get rated charge current
      print(mppt.getRatedLoadCurrent(slave)) #get rated load current
      print(mppt.getDischargingState(slave)) #get discharge state
      time.sleep(0.1) #always add sleep when using modbus within for loop. without sleep, the modbus result always failed
   
    