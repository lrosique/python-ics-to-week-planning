# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 16:44:02 2018

@author: lambe
"""

from ics import Calendar
import arrow
import shutil
from PIL import Image, ImageFont, ImageDraw
import requests

### Génération du planning par semaine
def get_weekday(event):
    return event.begin.datetime.weekday()

url = "https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics"
c = Calendar(requests.get(url).text)
#file = open('myevents.ics','r')
#c = Calendar(file)

now = arrow.now()
today = now.datetime.weekday()

def convert_to_int(ar):
    s = f'{ar.year:04}'+f'{ar.month:02}'+f'{ar.day:02}'
    return int(s)

def construct_week_events(now, c, begin, end):
    this_week = []
    for i in range(begin, end):
        current_day_int = convert_to_int(now.replace(days=i))
        day_events = []
        for e in c.events:
            if current_day_int == convert_to_int(e.begin):
                day_event = {"titre":e.name,"heureDebut":f'{e.begin.hour:02}',"minuteDebut":f'{e.begin.minute:02}',"heureFin":f'{e.end.hour:02}',"minuteFin":f'{e.end.minute:02}',"date":convert_to_int(e.begin)}
                day_events.append(day_event)
        this_week.append(day_events)
    return this_week

#This week
this_week = construct_week_events(now, c, -today, 5-today)
#Next week
next_week = construct_week_events(now, c, -today +7, 5 -today +7)

### Copie du planning
file_planning = "current_planning.png"
shutil.copy2("empty_planning.png",file_planning)

### Edition de l'image
img = Image.open(file_planning)

# Ajout des post-it
def load_postit():
    comp = Image.open("postit.png").convert("RGBA")
    width, height = comp.size
    new_width  = 840
    new_height = new_width * height // width 
    new_height = 380
    new_width  = new_height * width // height
    
    comp = comp.resize((new_width, new_height), Image.ANTIALIAS)
    return comp

positions_postit_current_week = [(180,255),(530,255),(874,255),(1216,255),(1559,255)]
positions_postit_next_week = [(180,670),(530,670),(874,670),(1216,670),(1559,670)]

posit = load_postit()
for i in range(0,5):
    if len(this_week[i]) > 0:
        img.paste(posit, positions_postit_current_week[i], mask=posit)
    if len(next_week[i]) > 0:
        img.paste(posit, positions_postit_next_week[i], mask=posit)

# Ajout du texte des post-it
def multiline_text(hour,txt):
    max_len = 13
    split = txt.split(" ")
    result = hour+"\n\n"
    sentence = ""
    for s in split:
        if (len(s) > max_len):
            result += sentence + " " + s[0:max_len-1 -len(sentence)]
            sentence = s[max_len-1 -len(sentence):]
        elif len(sentence) + len(s) < max_len:
            if sentence == "":
                sentence += s
            else:
                sentence += " "+s
        else:
            result += sentence + "\n"
            sentence = s
    result += sentence
            
    return result

def construct_hours(event):
    start = event["heureDebut"]+"h"+event["minuteDebut"]
    end = event["heureFin"]+"h"+event["minuteFin"]
    return start + " - " + end

def draw_text(events, font, draw, position):
    texte = ""
    for event in events:
        hour,txt = construct_hours(event), event["titre"]
        texte += multiline_text(hour,txt) + "\n\n"
    width,height= draw.textsize(texte, font=font)
    draw.multiline_text(position,texte,(0,0,0),font=font, align='center')
    
font = ImageFont.truetype("arial-bold.ttf", 38)
draw = ImageDraw.Draw(img)

position_text_current_week = [(240, 350),(590, 350),(934, 350),(1276, 350),(1619, 350)]
position_text_next_week = [(240, 765),(590, 765),(934, 765),(1276, 765),(1619, 765)]
for i in range(0,5):
    if len(this_week[i]) > 0:
        draw_text(this_week[i],font,draw,position_text_current_week[i])
    if len(next_week[i]) > 0:
        draw_text(next_week[i],font,draw,position_text_next_week[i])

# Add "completed" stamp
def load_completed():
    comp = Image.open("completed.png").convert("RGBA")
    width, height = comp.size
    new_width  = 345
    new_height = new_width * height // width 
    new_height = 155
    new_width  = new_height * width // height
    
    comp = comp.resize((new_width, new_height), Image.ANTIALIAS)
    return comp

positions_completed = [(199,495),(549,495),(893,495),(1235,495)]
completed = load_completed()
for i in range(0,today):
    img.paste(completed, positions_completed[i], mask=completed)

# Sauvegarde finale de l'image complète
img.save(file_planning, format="png")