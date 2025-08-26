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
    return (delta_time+in_station_time)//2


class Monitor:
    def __init__(self,cs, dc, rst, spi,normal_spacing = 1):
        self.normal_spacing = normal_spacing

        #create display:
        CS = Pin(cs,Pin.OUT)
        DC = Pin(dc,Pin.OUT)
        RS = Pin(rst,Pin.OUT)
        self.Display = Display(spi,CS,DC,RS)
        
        #load font:
        self.font = XglcdFont('WLM-font1.c',10,16)

    def show_departures(self,departures,ref_time,platform=None,display_line=False,advanced_preview=False):
        text_start = [0,8]
        
        if (platform!=None):
            self.Display.draw_bitmap_mono(f'Gleis{platform}.bmp',0,0,36,64)#TODO: catch no file in directory error
            text_start[0] = 40
        
        for i in range(len(departures)):
            departure = departures[i]

            towards = departure['towards']
            if (display_line):
                towards = (departure['line'] + ' ' + towards)[:16]
            
            countdown = delta_minutes(departure['time'], ref_time)
            if (countdown<0):
                continue
            grayscale_this_departure = 15
            if (advanced_preview and towards[1]>=32 and len(departures)-1>i): 
                #in second line, advanced preview enabled and a next departure exists
                period = 4 #seconds

                t = time.ticks_ms() % (period*math.pi*2000)
                grayscale_this_departure = max(math.floor(15.9*math.cos(t)),0)
                grayscale_next_departure = -min(math.floor(15.9*math.cos(t)),0)
                #display next_departure 
                next_departure = departures[i+1]
                next_towards = next_departure['towards']
                if (display_line):
                    next_towards = (next_departure['line'] + ' ' + next_towards)[:16]
                self.Display.draw_text(*text_start,next_towards,self.font,gs=grayscale_next_departure,spacing=self.normal_spacing)
                next_flag_folding_ramp = departure['foldingRamp']
                if (next_flag_folding_ramp):
                    self.Display.draw_text(216, text_start[1],'-',self.font,gs=grayscale_next_departure)
                next_countdown = delta_minutes(next_departure['time'], ref_time)
                self.Display.draw_text(230,text_start[1],str(next_countdown).zfill(2),self.font,gs=grayscale_next_departure,spacing=self.normal_spacing)
                
            self.Display.draw_text(*text_start,towards,self.font,gs=grayscale_this_departure,spacing=self.normal_spacing)
            flag_folding_ramp = departure['foldingRamp']
            if (flag_folding_ramp):
                self.Display.draw_text(216, text_start[1],'-',self.font,gs=grayscale_this_departure)
            self.Display.draw_text(230,text_start[1],str(countdown).zfill(2),self.font,gs=grayscale_this_departure,spacing=self.normal_spacing)
            towards[1] += 32
            if (towards[1]>=64):#breaks after second entry
                break
        self.Display.present()
        pass

    def cleanup(self):
        self.Display.cleanup()