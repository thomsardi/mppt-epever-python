from mpptepveper.mppt_epveper import MPPTEPVEPER
from base import ParameterSetting, ParserSetting
import json
import time

if __name__ == "__main__" :
   file = json.load(open('register_config.json')) #convert the json file into dict
   port = file['port'] #get port name from register_config.json file
   mppt =  MPPTEPVEPER(port=port) #setup modbus with specified port and 115200 baudrate
   parser = ParserSetting() #create ParserSetting object
   dummy : list[ParameterSetting] = parser.parse(file) #get value from "parameter" key 
   # print(len(dummy))
   for a in dummy :
      if(mppt.setBulkParameter(a)) : #write modbus register
         print("Success write into id ", a.id)
      else :
         print("Failed to write into id ", a.id)
   
   test = mppt.getCurrentSetting(1) #get current setting
   if (test is not None) :
      test.printContainer() #print the container
   test = mppt.getCurrentSetting(2) #get current setting
   if (test is not None) :
      test.printContainer() #print the container
   else :
      print("Failed")

   if (mppt.setLoadOn(1)) :
      print("Success set load at id ", 1)
   else :
      print("Failed set load at id ", 1)

   print(mppt.getAllPVInfo(1))
   print(mppt.getGeneratedEnergy(1))
   print(mppt.getBatteryInfo(1))
   print(mppt.getLoadInfo(1))
   print(mppt.getBatterySoc(1))
   print(mppt.getTemperatureInfo(1))
   print(mppt.getStatusInfo(1))
   print(mppt.getChargingState(1))
   print(mppt.getRatedChargingCurrent(1))
   print(mppt.getRatedLoadCurrent(1))
   # time.sleep(5)
   print(mppt.getDischargingState(1))
   
   # print(mppt.getStatusInfo(2))
   
    