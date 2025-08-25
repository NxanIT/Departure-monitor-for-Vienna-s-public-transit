# Departure monitor for Vienna's metro system
An adjustable display for departures of one station in Vienna's public transport system. 
In the current version only the metro lines are available for display. Used are:
- The API of "WienerLinien"
- micropython-ssd1322, a repository from rdagger providing a micropython driver for OLED-displays using the SSD1322 chip
- An Arduiono Nano ESP32
- Two monochrome (yellow) [OLED-displays](https://www.mouser.at/ProductDetail/763-3.12-25664UCY2) with a SSD1322 driver IC and a resolution of 265x64 px
>[!Warning]
>This project is not finished yet. Files that need to be changed and tested:
> - [ ] main.py - main file
> - [ ] DataConversions.py - converts json-data to array of departures
> - [ ] Monitors.py - displays departures

>[!Note]
>The code updated to this repository is not the final version. I will update the code as soon as possible to resolve any bugs. 
## About this project:
While working on a monitor displaying the Vienna metro system in real time [(latest version here)](https://github.com/NxanIT/WienerLinienMonitor), 
I was asked by a friend of mine, if
it would be possible to just track one part of a single line. Some time has passed and I finally 
got the free time to work on that. It should be noted that in the meantime three students from TU Wien built a similar product, that can be found [here](https://straba.at/).
Even though I have no affiliation with their project, I encurage you to check it out. When using the same parts as I did, their product would probably be cheaper anyways.
