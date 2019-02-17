#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from pprint import pprint


def load_ingredients(raw):
    ingredients = {}
    ingredient_pattern = re.compile("^\\s*(.*?)\\s*:\\s*(.*)\\s*")
    for line in raw:
        line = line.rstrip()
        m = ingredient_pattern.match(line)
        if m:
            ingredients[m.group(1)] = m.group(2).split(",")
    return ingredients


def resolve_ingredients(synonyms):
    resolved = {}
    for ingredient in synonyms.keys():
        ingredient_synonyms_resolved = resolve_ingredient(synonyms, ingredient)
        resolved[ingredient] = ingredient_synonyms_resolved
    return resolved


def resolve_ingredient(synonyms, ingredient):
    ingredient_synonyms_resolved = []
    for synonym in synonyms[ingredient]:
        ingredient_synonyms_resolved.append(synonym)
        if synonym in synonyms:
            ingredient_synonyms_resolved.extend(resolve_ingredient(synonyms, synonym))
    return ingredient_synonyms_resolved


with open("ingredients.txt") as f:
    ingredients_raw = f.readlines()

with open("some.txt") as f:
    diary_raw = f.readlines()

ingredients_unresolved = load_ingredients(ingredients_raw)

pprint(ingredients_unresolved)
print()
print()

ingredients_resolved = resolve_ingredients(ingredients_unresolved)

pprint(ingredients_resolved)
print()
print()

contents_per_time = {}


def process_diary():
    diary_title_pattern = re.compile("^(\\d+)\\.(\\d+)\\.(\\d+) (\\d+):(\\d+) (\\d+)(.(\\d+))?$")
    next_day = 1
    time = "?"
    for line in diary_raw:
        line = line.rstrip()
        if not line:
            next_day = 1
            print('-------')
        else:
            if next_day:
                print('day:' + line)
                m = diary_title_pattern.match(line)
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


process_diary()

pprint(contents_per_time)
print()
print()
