#import json
import urequests
import network
from datetime import timedelta
from machine import Pin, SPI #type:ignore
import time

from Monitors import Monitors
from DataConversion import getData


#configuration data:
LINES = ["U1","U2","U3","U4","U5","U6"]
Pin_in_selectLine = [5,6,7]
Pin_in_selectStation = [8,9,10,17,18]
Pin_in_selectAdvancedPreview = 20

#global data - pins:
pl_lineSelect = []
pl_stationSelect = []
p_selAdvPrev = None


#global data - station info
AdvancedPrev = None
lineSelect = None
stationIndex = None
meassured_ids = []

#network credentials
ssid = 'your_SSID'
password = 'your_PASSWORD'

def fetch(line:str, station:int):
  data = None
  try:
    URL = generateAPI_URL(meassured_ids)
    response = urequests.get(URL)
    data = response.json()
  except OSError as err:
    print("Error while attempting to open API data. Message:",err)
  finally:
    response.close()
    return data
    

def generateAPI_URL(station_nr_list,FLAG_use_stopID=True):
  assert len(station_nr_list)>0
  request_type = "stopID=" if FLAG_use_stopID else "diva="
  string = "https://www.wienerlinien.at/ogd_realtime/monitor?" + request_type + str(station_nr_list[0])
  for name in station_nr_list[1:]:
    string += "&" + request_type + str(name)
  return string

def init():
  """ - connects to WLAN
      - configures GPIO pins
  """
  # init Displays
  spi = SPI(1, baudrate=250000, sck=Pin(48), mosi=Pin(38))
  #TODO: figure out which platforms to choose
  Mo = Monitors(spi,platforms=(1,2))
  # Connect to WLAN
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(ssid, password)#TODO add catch method retrying connecting to wlan after wait
  while not wlan.isconnected():
    pass
  print("connected to WLAN.")

  #setup GPIO
  global p_selAdvPrev
  p_selAdvPrev = Pin(Pin_in_selectAdvancedPreview,Pin.IN,Pin.PULL_UP)
  
  global pl_lineSelect
  for pin_nr in Pin_in_selectLine:
    pl_lineSelect.append(Pin(pin_nr,Pin.IN,Pin.PULL_UP))
    
  global pl_lineSelect
  for pin_nr in Pin_in_selectStation:
    pl_stationSelect.append(Pin(pin_nr,Pin.IN,Pin.PULL_UP))
  
  return Mo
  
def read_pin_input():
  global AdvancedPrev
  AdvancedPrev = False if p_selAdvPrev.value()==0 else True
  list_lineSelect = [pin_id.value() for pin_id in pl_lineSelect]
  new_lineSelect = LINES[int("".join(map(str,list_lineSelect)),2)]
  list_stationSelect = [pin_id.value() for pin_id in pl_stationSelect]
  new_stationIndex = int("".join(map(str,list_stationSelect)),2)
  global stationIndex, lineSelect
  if(stationIndex!=new_stationIndex or lineSelect!=new_lineSelect):
    stationIndex = new_stationIndex
    lineSelect = new_lineSelect
    return True
  return False

def updateMeassured_ids():
  global stationIndex, lineSelect
  stop_IDs_U1 = [[4134,4133], [4135,4132], [4136,4131], [4137,4130], [4138,4129], [4101,4128], [4103,4126], [4105,4124], [4107,4122], [4109,4120], [4111,4118], [4113,4116], [4115,4114], [4117,4112], [4119,4110], [4121,4108], [4123,4106], [4125,4104], [4127,4102], [4181,4186], [4182,4187], [4183,4188], [4184,4189], [4185,4190]] #index 0,0 is Oberlaa ->Leopoldau
  stop_IDs_U2 = [[4277,4276], [4278,4275], [4279,4274], [4251,4272], [4252,4271], [4253,4270], [4254,4269], [4256,4267], [4255,4268], [4257,4266], [4258,4265], [4259,4264], [4260,4263], [4261,4262], [4201,4214], [4203,4212], [4205,4210], [4209,4206], [4211,4204], [4213,4202]] #index 0,0 is Seestadt -> Karlsplatz
  stop_IDs_U3 = [[4931,4930], [4932,4929], [4933,4928], [4926,4925], [4927,4924], [4921,4920], [4922,4919], [4923,4918], [4909,4908], [4910,4907], [4911,4906], [4912,4905], [4913,4904], [4914,4903], [4915,4902], [4916,4901], [4917,4900], [4934,4941], [4935,4940], [4936,4939], [4937,4938]] #index 0,0 is Ottakring -> Simmering
  stop_IDs_U4 = [[4401,4436], [4403,4434], [4405,4432], [4407,4430], [4409,4428], [4411,4426], [4413,4424], [4437,4438], [4415,4422], [4417,4420], [4419,4418], [4421,4416], [4423,4414], [4425,4412], [4427,4410], [4429,4408], [4431,4406], [4433,4404], [4439,4440], [4435,4402]] #index 0,0 is Hütteldorf -> Heiligenstadt
  stop_IDs_U6 = [[4635,4634], [4636,4633], [4637,4632], [4638,4631], [4639,4630], [4640,4629], [4615,4614], [4616,4613], [4617,4612], [4618,4611], [4619,4610], [4620,4609], [4621,4608], [4622,4607], [4623,4606], [4624,4605], [4625,4604], [4626,4603], [4627,4651], [4641,4650], [4642,4649], [4643,4648], [4644,4647], [4645,4646]] #index 0,0 is Siebenhierten -> Floridsdorf
  Stop_IDs = {"U1":stop_IDs_U1,"U2":stop_IDs_U2,"U3":stop_IDs_U3,"U4":stop_IDs_U4,"U6":stop_IDs_U6}
  return Stop_IDs[lineSelect][stationIndex]
  
def main():
  Mo = init()
  
  while True:
    flag_station_changed = read_pin_input()
    if(flag_station_changed): 
      print("station and or line changed.")
      updateMeassured_ids()
    json_data = fetch()
    if(json_data==None): continue
    departures, ref_time = getData(json_data)
    for i in range(1,60):
      delta_time_fetched = timedelta(seconds=i)
      Mo.show_data(departures,ref_time+delta_time_fetched)
      time.sleep(1)


  
