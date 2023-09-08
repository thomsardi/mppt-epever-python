# from mppt.logger import *
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from .address import *
from base import BaseMPPTSync, ParameterSetting, Status
import datetime
import time

class MPPTEPVEPER(BaseMPPTSync):

    def __init__(self, port:str, baudrate:int=115200, timeout:int = 1):
        super().__init__(port, baudrate, timeout=timeout)

    def getRegisters(self, id:int, info:tuple, input_register=False) -> list:
        addr = info[0]
        length = info[1]
        # rr = self.client.read_holding_registers(addr, length, unit=id)
        if(not self.client.connect()) :
            print("Failed to connect")
            return None
        if input_register:
            response_register = self.client.read_input_registers(addr, length, unit=id)
        else:
            response_register = self.client.read_holding_registers(addr, length, unit=id)
        # log.debug(rr.encode())
        self.client.close()
        return response_register
    
    def checkSetting(self, newSetting : ParameterSetting) -> int :
        """
        Check the equalness of ParameterSetting

        Args :
        newSetting(Parameter Setting) : new parameter to be sent into mppt

        Returns :
        int : the result of comparison between new setting and old setting. return 1 if same, 0 if it is different, -1 if it is different type
        """
        oldSetting = self.getCurrentSetting(newSetting.id)
        if type(oldSetting) is not ParameterSetting :
            return -1
        return newSetting == oldSetting

    def scan(self, start_id : int, end_id : int) :
        return self.startScan(startId=start_id, endId=end_id)
    
    def get_pv_info(self, id:int) -> dict:
        return self.getAllPVInfo(id=id)

    def get_load_info(self, id:int) -> dict:
        return self.getLoadInfo(id=id)

    def get_battery_info(self, id:int) -> dict:
        return self.getBatteryInfo(id=id)

    def get_load_status(self, id:int) -> dict:
        return self.getLoadInfo(id=id)

    def get_and_change_setting(self, id : int, val : list[int]) -> int :
        paramList : list[int] = self.getCurrentSetting(id=id).getListParam()
        for index, element in enumerate(val) :
            if (paramList[index] == element) :
                continue
            else :
                return 0
        return 1

    def startScan(self, startId : int, endId : int) -> list[int] :
        """
        Scan for connected id

        Args :
        startId (int) : start id to be scanned
        endId (int) : last id to be scanned

        Returns :
        list[int] : list of connected id
        """
        connectedIdList : list[int] = []
        for i in range(startId, endId+1) :
            arrayRatedVoltage = self.getArrayRatedVoltage(i)
            if (arrayRatedVoltage >= 0) :
                connectedIdList.append(i)
            time.sleep(0.1) #always add sleep when using modbus within for loop. without sleep, the modbus result always failed
        return connectedIdList

    def setBulkParameter(self, setting : ParameterSetting) -> int:
        """
        Set Bulk Parameter, convert ParameterSetting into list of integer with length of 15
        
        Args :
        setting (ParameterSetting) : ParameterSetting Object, refer to ParameterSetting description for member information        
        """
        value : list[int] = [
            setting.batteryType,
            setting.capacity,
            setting.tempCompensation,
            setting.overvoltageDisconnect,
            setting.chargingLimitVoltage,
            setting.overvoltageReconnect,
            setting.equalizeChargingVoltage,
            setting.boostChargingVoltage,
            setting.floatChargingVoltage,
            setting.boostReconnectVoltage,
            setting.lowVoltageReconnect,
            setting.underVoltageWarningRecover,
            setting.underVoltageWarning,
            setting.lowVoltageDisconnect,
            setting.dischargingLimitVoltage
        ]

        if (len(value) == 15) :
            request = self.setRegisters(setting.id, SETTING_PARAMETER[0], value)
            if (not request.isError()) :
                return 1
            else :
                return 0
        else :
            return 0

    def getArrayRatedVoltage(self, id : int) -> int :
        ratedVoltage = -1
        response = self.getRegisters(id, ARRAY_RATED_VOLTAGE, input_register=True)
        if (not response.isError() and response is not None) :
            ratedVoltage = response.registers[0]
        return ratedVoltage

    def getPVInfo(self, id:int):
        response = self.getRegisters(id, PV_INFO, input_register=True)
        return {
            'pv_voltage': {
                'value': response.registers[0] * 0.01,
                'satuan': 'Volt'
            },
            'pv_current': {
                'value': response.registers[1] * 0.01,
                'satuan': 'Ampere'
            }
        }
    
    def getCurrentSetting(self, id : int) -> ParameterSetting :
        """
        Get current parameter setting from address 0x9000 - 0x900E

        Args :
        id (int) : slave id of target device

        Returns :
        ParameterSetting : object

        """
        response = self.getRegisters(id, SETTING_PARAMETER)
        if (response.isError() and response is not None) :
            # print("Response error")
            return None
        p = ParameterSetting()
        if (not p.setParam(response.registers)) :
            print("Failed to set parameter")
            return None
        p.id = id
        return p

    def getAllPVInfo(self, id:int) -> dict:
        """
        Get all PV info such as voltage, current and power

        Args :
        id (int) : slave id of the target device

        Returns :
        dict : dictionary with key:value pair
        """
        voltage = -1
        current = -1
        power = -1
        response = self.getRegisters(id, PV_INFO, input_register=True)
        if (not response.isError() and response is not None) :
            voltage = round(response.registers[0] / 100, 2)
            current = round(response.registers[1] / 100, 2)
            power = round(((response.registers[3] << 16) + response.registers[2]) / 100, 2)
        
        result = {
            'pv_voltage': {
                'value': voltage,
                'satuan': 'Volt'
            },
            'pv_current': {
                'value': current,
                'satuan': 'Ampere'
            },
            'pv_power' : {
                'value': power,
                'satuan': 'Watt'
            }
        }
        
        return result

    def getEnergyDay(self, id: int):
        response = self.getRegisters(id, HARVEST_ENERGY, input_register=True)
        return {
            'harvest_energy': {
                'value': response.registers[0],
                'satuan': '?'
            }
        }
    
    def getGeneratedEnergy(self, id: int) -> dict:
        """
        Get all generated energy info such as today, this month, and this year generated enery

        Args :
        id (int) : slave id of target device

        Returns :
        dict : dictionary with key:value pair
        """
        generatedEnergyToday = -1
        generatedEnergyThisMonth = -1
        generatedEnergyThisYear = -1
        generatedEnergyTotal = -1
        response = self.getRegisters(id, GENERATED_ENERGY_INFO, input_register=True)
        if (not response.isError() and response is not None) :
            generatedEnergyToday = ((response.registers[1] << 16) + response.registers[0]) / 100
            generatedEnergyThisMonth = ((response.registers[3] << 16) + response.registers[2]) / 100
            generatedEnergyThisYear = ((response.registers[5] << 16) + response.registers[4]) / 100
            generatedEnergyTotal = ((response.registers[7] << 16) + response.registers[6]) / 100

        result = {
            'harvest_energy': {
                'value': generatedEnergyToday,
                'satuan': 'Watt'
            },
            'harvest_energy_this_month': {
                'value': generatedEnergyThisMonth,
                'satuan': 'Watt'
            },
            'harvest_energy_this_year': {
                'value': generatedEnergyThisYear,
                'satuan': 'Watt'
            },
            'harvest_energy_total': {
                'value': generatedEnergyTotal,
                'satuan': 'Watt'
            }
        }
        return result
    
    def setLoadOn(self, id : int) -> int :
        """
        Set load on

        Args :
        id (int) : slave id of target device

        Returns :
        int : 1 if success, 0 if failed
        """
        request = self.client.write_coil(LOAD_MANUAL_CONTROL[0], 1, unit=id)
        if (request.isError()) :
            return 0
        return 1
    
    def setLoadOff(self, id : int) -> int :
        """
        Set load off

        Args :
        id (int) : slave id of target device

        Returns :
        int : 1 if success, 0 if failed
        """
        request = self.client.write_coil(LOAD_MANUAL_CONTROL[0], 0, unit=id)
        if (request.isError()) :
            return 0
        return 1
    
    def setChargeOn(self, id : int) -> int :
        """
        Set charge on

        Args :
        id (int) : slave id of target device

        Returns :
        int : 1 if success, 0 if failed
        """
        request = self.client.write_coil(CHARGING_SET[0], 1, unit=id)
        if (request.isError()) :
            return 0
        return 1
    
    def setChargeOff(self, id : int) -> int :
        """
        Set charge off

        Args :
        id (int) : slave id of target device

        Returns :
        int : 1 if success, 0 if failed
        """
        request = self.client.write_coil(CHARGING_SET[0], 0, unit=id)
        if (request.isError()) :
            return 0
        return 1
    
    def setOutputManualMode(self, id : int) -> int :
        """
        Set output mode into manual

        Args :
        id (int) : slave id of target device

        Returns :
        int : 1 if success, 0 if failed
        """
        request = self.client.write_coil(OUTPUT_CONTROL_MODE[0], 1, unit=id)
        if (request.isError()) :
            return 0
        return 1
    
    def setOutputAutoMode(self, id : int) -> int :
        """
        Set output mode into auto

        Args :
        id (int) : slave id of target device

        Returns :
        int : 1 if success, 0 if failed
        """
        request = self.client.write_coil(OUTPUT_CONTROL_MODE[0], 0, unit=id)
        if (request.isError()) :
            return 0
        return 1
    
    def setDefaultLoadOn(self, id : int) -> int :
        """
        Set default state of load to on. load will normally on when the mppt turn on

        Args :
        id (int) : slave id of target device

        Returns :
        int : 1 if success, 0 if failed
        """
        request = self.client.write_coil(DEFAULT_LOAD_STATE[0], 1, unit=id)
        if (request.isError()) :
            return 0
        return 1
    
    def setDefaultLoadOff(self, id : int) -> int :
        """
        Set default state of load to off. load will normally off when the mppt turn on

        Args :
        id (int) : slave id of target device

        Returns :
        int : 1 if success, 0 if failed
        """
        request = self.client.write_coil(DEFAULT_LOAD_STATE[0], 0, unit=id)
        if (request.isError()) :
            return 0
        return 1

    def settingParameter(self, id ,val = [0, 832,300, 5570, 5520, 5370, 5470, 5470, 5470, 5370, 4950, 4900, 4800, 4700, 4600]):
        request = self.setRegisters(id, SETTING_PARAMETER[0], val)
        return request

    def setMode(self, id, val=[4,]):
        request =self.setRegisters(id, MODE[0], val)
        return request

    def setDateTime(self, id, dt=None):
        if dt is None:
            waktu = datetime.datetime.now()
        else:
            waktu = dt
        raw_menit =  waktu.minute
        raw_detik = waktu.second
        hasil1 = raw_menit*256 + raw_detik

        raw_jam = waktu.hour
        raw_hari = waktu.day
        hasil2 = raw_hari *256 + raw_jam

        raw_bulan = waktu.month
        raw_tahun = int(str(waktu.year)[-2:])
        hasil3 = raw_tahun *256 + raw_bulan

        request = self.setRegisters(id, DATETIME_ADDR[0], val=[hasil1,hasil2,hasil3])
        return request

    def getSettingParam(self, id):
        response = self.getRegisters(id, SETTING_PARAMETER)
        return response.registers

    def getBattVoltage(self, id: int):
        response = self.getRegisters(id, BATT_VOLTAGE, input_register=True)
        return {
            'battery_voltage': {
                'value': round((response.registers[0]* 0.01), 2),
                'satuan': 'Volt'
            }
        }
    
    def getBatteryInfo(self, id : int) -> dict:
        """
        Get battery info such as battery voltage & current

        Args : 
        id(int) : slave id of target device

        Returns :
        dict : dictionary with key:value pair
        """
        response = self.getRegisters(id, BATTERY_INFO, input_register=True)
        batteryVoltage = -1
        batteryCurrent = -1
        if (not response.isError() and response is not None) :
            batteryVoltage = round(response.registers[0] / 100, 2)
            batteryCurrent = round((((response.registers[2] << 16) + response.registers[1]) / 100) , 2)

        result = {
            'battery_voltage': {
                'value': batteryVoltage,
                'satuan': 'Volt'
            },
            'battery_current': {
                'value': batteryCurrent,
                'satuan': 'Ampere'
            }
        }
        return result
    
    def getLoadInfo(self, id : int) -> dict :
        """
        Get load info such as load voltage, current & power

        Args : 
        id(int) : slave id of target device

        Returns :
        dict : dictionary with key:value pair
        """
        response = self.getRegisters(id, LOAD_INFO, input_register=True)
        loadVoltage = -1
        loadCurrent = -1
        loadPower = -1
        if (not response.isError() and response is not None) :
            loadVoltage = round(response.registers[0] / 100, 2)
            loadCurrent = round(response.registers[1] / 100, 2)
            loadPower = round((((response.registers[3] << 16) + response.registers[2]) / 100) , 2)

        result = {
            'load_voltage': {
                'value': loadVoltage,
                'satuan': 'Volt'
            },
            'load_current': {
                'value': loadCurrent,
                'satuan': 'Ampere'
            },
            'load_power': {
                'value': loadPower,
                'satuan': 'Watt'
            }
        }

        return result
    
    def getBatterySoc(self, id : int) -> dict :
        """
        Get battery SoC

        Args : 
        id(int) : slave id of target device

        Returns :
        dict : dictionary with key:value pair
        """
        response = self.getRegisters(id, BATTERY_SOC, input_register=True)
        soc = -1
        if (not response.isError() and response is not None) :
            soc = response.registers[0]
        
        result = {
            'battery_soc': {
                'value': soc,
                'satuan': '%'
            }
        }

        return result
    
    def getTemperatureInfo(self, id : int) -> dict :
        """
        Get temperature info such as battery temperature & device temperature

        Args : 
        id(int) : slave id of target device

        Returns :
        dict : dictionary with key:value pair
        """
        response = self.getRegisters(id, TEMPERATURE_INFO, input_register=True)
        batteryTemperature = -1
        deviceTemperature = -1
        if (not response.isError() and response is not None) :
            batteryTemperature = round(response.registers[0] / 100, 2)
            deviceTemperature = round(response.registers[1] / 100, 2)
        
        result = {
            'battery_temperature': {
                'value': batteryTemperature,
                'satuan': 'Celsius'
            },
            'device_temperature': {
                'value': deviceTemperature,
                'satuan': 'Celsius'
            }
        }

        return result
    
    def getStatusInfo(self, id : int) -> dict :
        """
        Get status info such as battery status, charging status and discharging status

        Args : 
        id(int) : slave id of target device

        Returns :
        dict : dictionary with key:value pair
        """
        response = self.getRegisters(id, STATUS_INFO, input_register=True)
        s = Status()
        batteryStatus = -1
        chargingStatus = -1
        dischargingStatus = -1
        if (not response.isError() and response is not None) :
            batteryStatus = response.registers[0]
            batteryStatusDict = s.unpackBatteryStatus(batteryStatus)
            chargingStatus = response.registers[1]
            chargingStatusDict = s.unpackChargingStatus(chargingStatus)
            dischargingStatus = response.registers[2]
            dischargingStatusDict = s.unpackDischargingStatus(dischargingStatus)
        
            result = {
                'battery_status' : batteryStatusDict,
                'charging_status' : chargingStatusDict,
                'discharging_status' : dischargingStatusDict
            }
            return result
        else :
            return None
        
    def getDischargingState(self, id : int) -> int :
        """
        Get discharging state

        Args : 
        id(int) : slave id of target device

        Returns :
        int : 1 is running, 0 is standby
        """
        response = self.getRegisters(id, STATUS_INFO, input_register=True)
        s = Status()
        batteryStatus = -1
        chargingStatus = -1
        dischargingStatus = -1
        if (not response.isError() and response is not None) :
            batteryStatus = response.registers[0]
            s.unpackBatteryStatus(batteryStatus)
            chargingStatus = response.registers[1]
            s.unpackChargingStatus(chargingStatus)
            dischargingStatus = response.registers[2]
            s.unpackDischargingStatus(dischargingStatus)
            result = s.dischargingStatus.dischargingState 
            return result
        else :
            return -1
        
    def getChargingState(self, id : int) -> int :
        """
        Get charging state

        Args : 
        id(int) : slave id of target device

        Returns :
        int : 1 is running, 0 is standby
        """
        response = self.getRegisters(id, STATUS_INFO, input_register=True)
        s = Status()
        batteryStatus = -1
        chargingStatus = -1
        dischargingStatus = -1
        if (not response.isError() and response is not None) :
            batteryStatus = response.registers[0]
            s.unpackBatteryStatus(batteryStatus)
            chargingStatus = response.registers[1]
            s.unpackChargingStatus(chargingStatus)
            dischargingStatus = response.registers[2]
            s.unpackDischargingStatus(dischargingStatus)
            result = s.chargingStatus.chargingState 
            return result
        else :
            return -1
        
    def getRatedChargingCurrent(self, id : int) -> dict :
        """
        Get rated charging current

        Args : 
        id(int) : slave id of target device

        Returns :
        dict : dictionary with key:value pair
        """
        response = self.getRegisters(id, RATED_CHARGING_CURRENT, input_register=True)
        chargingCurrent = -1
        if (not response.isError() and response is not None) :
            chargingCurrent = round(response.registers[0] / 100, 2)
        
        result = {
            'rated_charging_current': {
                'value': chargingCurrent,
                'satuan': 'Ampere'
            }
        }
        return result
    
    def getRatedLoadCurrent(self, id : int) -> dict :
        """
        Get rated load current

        Args : 
        id(int) : slave id of target device

        Returns :
        dict : dictionary with key:value pair
        """
        response = self.getRegisters(id, RATED_LOAD_CURRENT, input_register=True)
        loadCurrent = -1
        if (not response.isError() and response is not None) :
            loadCurrent = round(response.registers[0] / 100, 2)
        
        result = {
            'rated_load_current': {
                'value': loadCurrent,
                'satuan': 'Ampere'
            }
        }
        return result
