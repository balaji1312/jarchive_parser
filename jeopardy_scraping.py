# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 04:18:58 2020

@author: Balaji's Laptop
"""

import requests
from bs4 import BeautifulSoup
import re
import numpy
import pandas as pd



def find_clue(soup, x, show_num, date, df, rnd):
    
    
    all_clues = soup.find(id=rnd)
    
    if rnd == "jeopardy_round":
        rnd_name = "Jeopardy"
    elif rnd == "double_jeopardy_round":
        rnd_name = "Double Jeopardy"
    
    
    categories = [c.get_text() for c in all_clues.find_all("td", class_="category_name")]

    cat_num = 0
    for i in all_clues.find_all("td", class_="clue"):
        is_missing = True if not i.get_text().strip() else False
        if not is_missing:
            clue = i.find("td", class_="clue_text").get_text()
            value = int(i.find("td", class_=re.compile("clue_value")).get_text().lstrip("D: $").replace(',',''))
            answer = BeautifulSoup(i.find("div", onmouseover=True).get("onmouseover"), "lxml")
            answer = answer.find("em", class_="correct_response").get_text()
            df = df.append(pd.Series([x, show_num, date, rnd_name, categories[cat_num], value, clue, answer]), ignore_index=True)
        cat_num +=1
        cat_num%=6
    return df
        
df = pd.DataFrame()

break_count = 0

for x in range(6386, 6610):
    url = "http://www.j-archive.com/showgame.php?game_id=" + str(x)
    response = requests.get(url)
    print(response.status_code, x)
    
    if not 200<=response.status_code<230:
        break

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.get_text().split()
    if len(title)<4:
        break_count+=1
        if break_count>3:
            break
        continue
    break_count = 0
    show_num = soup.title.get_text().split()[4].strip("#")
    show_num = show_num.strip(",")                              
    date = soup.title.get_text().split()[6]
    final = soup.find("table", class_="final_round")
    if final:
        category = final.find("td", class_="category_name").get_text()
        clue = final.find("td", class_="clue_text").get_text()
        answer = BeautifulSoup(final.find("div", onmouseover=True).get("onmouseover"), "lxml")
        values = answer.find_all("td")
        value = 0
        for i in values:
            if "$" in i.get_text() and i.get_text().strip('$').replace(',', '').isnumeric():
                if int(i.get_text().strip('$').replace(',', ''))>value:
                    value = int(i.get_text().strip('$').replace(',', ''))
        
        answer = answer.find("em").get_text()
        
        df = df.append(pd.Series([x, show_num, date, "Final Jeopardy", category, value, clue, answer]), ignore_index=True)
        
        df = find_clue(soup, x, show_num, date, df, "jeopardy_round")
        df = find_clue(soup, x, show_num, date, df, "double_jeopardy_round")



df = df.rename({0:'Game ID', 1: 'Show Number', 2: 'Airdate', 3:'Round', 4:'Category', 5:'Value', 6:'Clue', 7:'Answer'}, axis='columns')

df.to_csv('jeopardy_archive13.csv', index= False)





