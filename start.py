#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from pprint import pprint

ingredients = {}

with open("ingredients.txt", "r", encoding='utf-8') as f:
    ingredient_pattern = re.compile("^\\s*(.*?)\\s*:\\s*(.*)\\s*")
    for line in f:
        line = line.rstrip()
        m = ingredient_pattern.match(line)
        if m:
            ingredients[m.group(1)] = m.group(2).split(",")

pprint(ingredients)
print()
print()


ingredients_resolved = {}
for ingredient, ingredient_synonyms in ingredients.items():
    ingredient_synonyms_resolved = []
    for ingredient_synonym in ingredient_synonyms:
        ingredient_synonyms_resolved.append(ingredient_synonym)
        if ingredient_synonym in ingredients:
            for ingredient_synonym_synonyms in ingredients[ingredient_synonym]:
                ingredient_synonyms_resolved.append(ingredient_synonym_synonyms)
    ingredients_resolved[ingredient] = ingredient_synonyms_resolved

pprint(ingredients_resolved)
print()
print()

contents_per_time = {}

with open("some.txt", "r", encoding='utf-8') as f:
    ingredient_pattern = re.compile("^(\\d+)\.(\\d+)\.(\\d+) (\\d+):(\\d+) (\\d+)(.(\\d+))?$")
    next_day = 1
    time = "?"
    for line in f:
        line = line.rstrip()
        if not line:
            next_day = 1
            print('-------')
        else:
            if next_day:
                print('day:' + line)
                m = ingredient_pattern.match(line)
                if m:
                    year = m.group(3).zfill(2)
                    month = m.group(2).zfill(2)
                    day = m.group(1).zfill(2)

                    hour = m.group(4).zfill(2)
                    minute = m.group(5).zfill(2)

                    time = year + "-" + month + "-" + day + "-" + hour + "-" + minute
                    print("ok " + time)
                else:
                    print("nok")
            else:
                contents = []
                if time in contents_per_time:
                    contents = contents_per_time[time]
                else:
                    contents_per_time[time] = contents
                contents.append(line)
                if line in ingredients_resolved:
                    for synonym in ingredients_resolved[line]:
                        contents.append(synonym)
                contents_per_time[time] = contents
                print(line)
            next_day = 0

pprint(contents_per_time)
print()
print()

