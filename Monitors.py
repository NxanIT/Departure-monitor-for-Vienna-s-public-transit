from datetime import datetime
from machine import Pin, SPI #type:ignore
import math, time

from micropython_ssd1322.xglcd_font import XglcdFont
from micropython_ssd1322.ssd1322 import Display

def delta_minutes(dtime_1:datetime, dtime_2:datetime):
    cutoff_expired = -2
    in_station_time = 30
    delta_time = (dtime_2-dtime_1).total_seconds()
    if delta_time<cutoff_expired: return -1
    if delta_time<in_station_time: return 0
    return int(delta_time+in_station_time)//60


class Monitor:
    def __init__(self,cs, dc, rst, spi,normal_spacing = 1):
        self.normal_spacing = normal_spacing

        #create display:
        CS = Pin(cs,Pin.OUT)
        DC = Pin(dc,Pin.OUT)
        RS = Pin(rst,Pin.OUT)
        self.Display = Display(spi,CS,DC,RS)
        
        #load font:
        self.font = XglcdFont('fonts/default_font.c',10,16)

    def show_departures(self,departures,ref_time,platform=None,display_line=False,advanced_preview=False):
        max_char_towards = 19 if platform == None else 16
        text_start = [0,8]
        
        if (platform!=None):
            self.Display.draw_bitmap_mono(f'Gleis{platform}.bmp',0,0,36,64)#TODO: catch no file in directory error
            text_start[0] = 40
        
        for i in range(len(departures)):
            departure = departures[i]

            countdown = delta_minutes(departure['time'], ref_time)
            if (countdown<0):
                continue #train no longer in station, continue

            grayscale_this_departure = 15
            if (advanced_preview and text_start[1]>=32 and len(departures)-1>i): 
                #in second line, advanced preview enabled and a next departure exists
                period = 4 #seconds
                t = time.ticks_ms() % (period*math.pi*2000)
                grayscale_this_departure = max(math.floor(15.9*math.cos(t)),0)
                grayscale_next_departure = -min(math.floor(15.9*math.cos(t)),0)
                #display next_departure 
                next_departure = departures[i+1]
                self.__print_towards(*text_start,next_departure,display_line,max_len=max_char_towards,gs=grayscale_next_departure)
                self.__print_foldingRamp(text_start[1],next_departure,gs=grayscale_next_departure)
                next_countdown = delta_minutes(next_departure['time'], ref_time)
                self.__print_countdown(text_start[1],next_countdown,gs=grayscale_next_departure)

            self.__print_towards(*text_start,departure,display_line,max_len=max_char_towards,gs=grayscale_this_departure)
            self.__print_foldingRamp(text_start[1],departure,gs=grayscale_this_departure)
            self.__print_countdown(text_start[1],countdown,gs=grayscale_this_departure)

            text_start[1] += 32
            if (text_start[1]>=64):#breaks after second entry
                break
        self.Display.present()
        pass

    def __print_towards(self,x_start:int,y_start:int,departure,display_line, max_len=16,gs=15):
        towards = departure['towards'][:max_len]
        if (display_line):
            towards = (departure['line'] + ' ' + towards)[:max_len]
        self.Display.draw_text(x_start,y_start,towards,self.font,gs=gs,spacing=self.normal_spacing)

    def __print_foldingRamp(self,y_start:int,departure,gs=15):
        flag_folding_ramp = departure['foldingRamp']
        if (flag_folding_ramp):
            self.Display.draw_text(216, y_start,'-',self.font,gs=gs)

    def __print_countdown(self,y_start:int,countdown:int,gs=15):
        if (countdown==0):
            currently_in_station = [' *', '* ']
            t = int(time.time()) % 2
            symbol = currently_in_station[t]
            self.Display.draw_text(230,y_start,symbol,self.font,gs=gs,spacing=self.normal_spacing)
            return
        
        str_countdown = str(countdown)
        if (countdown<=9):
            str_countdown = ' ' + str_countdown
        self.Display.draw_text(230,y_start,str_countdown,self.font,gs=gs,spacing=self.normal_spacing)

    def cleanup(self):
        self.Display.cleanup()