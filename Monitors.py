from datetime import datetime
from machine import Pin, SPI #type:ignore

from micropython_ssd1322.xglcd_font import XglcdFont
from micropython_ssd1322.ssd1322 import Display
normal_spacing = 1

def delta_minutes(dtime_1:datetime, dtime_2:datetime):
  cutoff_expired = -2
  in_station_time = 30
  delta_time = (dtime_2-dtime_1).total_seconds()
  if delta_time<cutoff_expired: return -1
  if delta_time<in_station_time: return 0
  return (delta_time+in_station_time)//2

class Monitors:
  def __init__(self,spi, platforms:list,cs=(1,2),dc=(4,5),rst=(3,6)):
    
    min_len = min(map(len,[platforms,cs,dc,rst]))
    self.Mo:dict[int,Monitor] = {}
    for i in range(min_len):
      platform = platforms[i]
      cs_i = cs[i]
      dc_i = dc[i]
      rst_i = rst[i]
      self.Mo[platform] = Monitor(cs_i,dc_i,rst_i,spi)
    self.platforms = platforms[:min_len]
    pass
  def show_data(self,data,ref_time,displayGleis=False,displayLine=False):
    for platform in self.platforms:
      self.Mo[platform].show_departures(data[platform],ref_time,platform if displayGleis else None, displayLine)
    pass

class Monitor:
  def __init__(self,cs, dc, rst,spi):

    self.normal_spacing = 1

    #connect to display:
    CS = Pin(cs,Pin.OUT)
    DC = Pin(dc,Pin.OUT)
    RS = Pin(rst,Pin.OUT)
    self.Display = Display(spi,CS,DC,RS)
    
    #load font:
    self.font = XglcdFont('WLM-font1.c',10,16)
    pass

  def show_departures(self,departures,ref_time,platform=None,display_line=False):
    text_start = [0,8]
    
    if(platform!=None):
      self.Display.draw_bitmap_mono(f'Gleis{platform}.bmp',0,0,36,64)#TODO: catch no file in directory error
      text_start[0] = 40
      pass
    
    for departure in departures:
      towards = departure["towards"]
      if(display_line):
        towards = (departure['line'] + " " + towards)[:16]
      countdown = delta_minutes(departure["time"], ref_time)
      if(countdown<0):
        continue
      self.Display.draw_text(*text_start,towards,self.font,spacing=normal_spacing)
      barrier_free = departure["foldingRamp"]
      if(barrier_free):
        self.Display.draw_text(216, text_start[1],"-",self.font)
      self.Display.draw_text(230,text_start[1],str(countdown).zfill(2),self.font,spacing=normal_spacing)
      towards[1] += 32
      if(towards[1]>=64):
        break
    self.Display.present()
    pass
  def show_display(self,departures: dict[list],ref_time,displayGleis=True,displayLine=False):
    platforms = list(departures.keys())
    platforms.sort()
    for direction in range(2):
      D = self.Displays[direction]
      text_start = [0,8]
      platform_nr = platforms[direction]
      if(displayGleis):
        D.draw_bitmap_mono(f'Gleis{platform_nr}.bmp',0,0,36,64)#TODO: check which direction corresponds to which track nr on lines
        text_start[0] = 44
        pass
      
      for departure in departures[platform_nr]:
        towards = departure["towards"]
        if(displayLine):
          towards = departure['line'] + " " + towards
        countdown = delta_minutes(departure["time"], ref_time)
        if(countdown<0):
          continue
        D.draw_text(*text_start,towards,self.font,spacing=normal_spacing)
        barrier_free = departure["foldingRamp"]
        if(barrier_free):
          D.draw_text(216, text_start[1],"-",self.font)
        D.draw_text(230,text_start[1],str(countdown),self.font,spacing=normal_spacing)
        towards[1] += 32
        D.present()
        if(towards[1]>=64):
          break
      text_start = [0,8]
      platform_nr = platforms[direction]
      if(displayGleis):
        D.draw_bitmap_mono(f'Gleis{platform_nr}.bmp',0,0,36,64)#TODO: check which direction corresponds to which track nr on lines
        text_start[0] = 44
        pass
      
      for departure in departures[platform_nr]:
        towards = departure["towards"]
        if(displayLine):
          towards = departure['line'] + " " + towards
        countdown = delta_minutes(departure["time"], ref_time)
        if(countdown<0):
          continue
        D.draw_text(*text_start,towards,self.font,spacing=normal_spacing)
        barrier_free = departure["foldingRamp"]
        if(barrier_free):
          D.draw_text(216, text_start[1],"-",self.font)
        D.draw_text(230,text_start[1],str(countdown),self.font,spacing=normal_spacing)
        towards[1] += 32
        D.present()
        if(towards[1]>=64):
          break
    pass

  def cleanup_all(self):
    for i in range(2):
      D = self.Displays[i]
      D.cleanup()