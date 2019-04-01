#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import io
from datetime import datetime
import matplotlib.pyplot as plt

lower_limit = -1 * 24
upper_limit = +4 * 24

sort_by_number_of_consumptions = False

def load_ingredients(raw):
    ingredients = {}
    ingredient_pattern = re.compile("^\\s*(.*?)\\s*:\\s*(.*)\\s*")
    for line in raw:
        line = line.rstrip()
        m = ingredient_pattern.match(line)
        if m:
            ingredients[m.group(1)] = [x.strip() for x in m.group(2).split(",")]
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


def parse_diary(diary_raw, ingredients):
    ingredients_diary = {}
    wellbeing_diary = {}
    well_being = 0
    diary_title_pattern = re.compile("^(\\d+)\\.(\\d+)\\.(\\d*) (\\d+):(\\d+)( -?(\\d+)(.(\\d+))?)?$")
    comment_pattern = re.compile("^#.*")
    next_day = 1
    first_datetime = 0
    diary_offset = 0
    for line in diary_raw:
        line = line.rstrip()
        if (comment_pattern.match(line)):
            continue
        if not line:
            next_day = 1
        else:
            if next_day:
                m = diary_title_pattern.match(line)
                if not m:
                    raise ValueError('Cannot parse diary title line: ' + line)

                year = datetime.now().year
                if m.group(3):
                    year = m.group(3).zfill(2)
                month = m.group(2).zfill(2)
                day = m.group(1).zfill(2)

                hour = m.group(4).zfill(2)
                minute = m.group(5).zfill(2)

                diary_datetime = datetime(int(year), int(month), int(day), int(hour), int(minute))

                if not first_datetime:
                    first_datetime = diary_datetime
                    wellbeing_diary[diary_offset] = well_being
                else:
                    old_diary_offset = diary_offset
                    old_well_being = wellbeing_diary[old_diary_offset]

                    diary_offset = round((diary_datetime - first_datetime).total_seconds() / 3600)
                    if m.group(6):
                        well_being = float(m.group(6))

                    if (old_diary_offset < diary_offset):
                        hours_inbetween = diary_offset - old_diary_offset
                        for i in range(1, hours_inbetween + 1):
                            wellbeing_diary[old_diary_offset + i] = old_well_being * (
                                    1 - (i / hours_inbetween)) + well_being * (i / hours_inbetween)
            else:
                contents = []
                if diary_offset in ingredients_diary:
                    contents = ingredients_diary[diary_offset]
                else:
                    ingredients_diary[diary_offset] = contents
                contents.append(line)
                if line in ingredients:
                    for synonym in ingredients[line]:
                        contents.append(synonym)
                ingredients_diary[diary_offset] = contents
            next_day = 0
    return ingredients_diary, wellbeing_diary


def mean(numbers):
    if len(numbers) > 0:
        return float(sum(numbers)) / len(numbers)


with io.open("ingredients.txt", encoding="utf-8") as f:
    ingredients_raw = f.readlines()

with io.open("diary.txt", encoding="utf-8") as f:
    diary_raw = f.readlines()

ingredients_unresolved = load_ingredients(ingredients_raw)
ingredients_resolved = resolve_ingredients(ingredients_unresolved)
ingredients_diary, wellbeing_diary = parse_diary(diary_raw, ingredients_resolved)

times = wellbeing_diary.keys()
well_beings = list(wellbeing_diary.values())

all_ingredients = []
all_ingredients.extend(ingredients_resolved.keys())
for ingredients_of_diary_entry in ingredients_diary.values():
    all_ingredients.extend(ingredients_of_diary_entry)

all_ingredients_unique = list(set(all_ingredients))
all_ingredients_unique.sort()

interesting_ingredients = []
if sort_by_number_of_consumptions:
    ingredients_with_number_of_consumptions = {}
    for inspected in all_ingredients_unique:
        consumptions = 0
        for consumption_time in ingredients_diary.keys():
            if inspected in ingredients_diary[consumption_time]:
                consumptions += 1
        ingredients_with_number_of_consumptions[inspected] = consumptions

    interesting_ingredients = sorted(
        filter(
            lambda x: ingredients_with_number_of_consumptions[x] > 1, ingredients_with_number_of_consumptions.keys()
        ),
        key=lambda x: ingredients_with_number_of_consumptions[x], reverse=True
    )
else:
    interesting_ingredients = all_ingredients_unique

number_of_ingredients = len(interesting_ingredients)
fig, axs = plt.subplots(number_of_ingredients, 1)

fig.set_size_inches(10, number_of_ingredients * 2)

plot_number = 0

for inspected in interesting_ingredients:
    print(inspected)
    consumption_times = []

    for consumption_time in ingredients_diary.keys():
        if inspected in ingredients_diary[consumption_time]:
            consumption_times.append(consumption_time)

    if len(interesting_ingredients) > 1:
        subplot = axs[plot_number]
    else:
        subplot = axs

    well_being_per_relative_time = []
    x = range(lower_limit, upper_limit)
    for i in x:
        well_being_per_relative_time.append([])

    for consumption_time in consumption_times:
        for relative_time in x:
            if 0 < (consumption_time + relative_time) < len(well_beings):
                well_being_per_relative_time[relative_time + 24].append(well_beings[consumption_time + relative_time])
        subplot.plot([time - consumption_time for time in times], well_beings, linestyle='-', color='#aaaaaa')

    average_well_being = [mean(x) for x in well_being_per_relative_time]
    subplot.plot(x, average_well_being, linestyle='-', )

    if not any([(not x) for x in average_well_being]):
        average_well_being_at_consumption = average_well_being[24]
        positive_effect = [y >= average_well_being_at_consumption for y in average_well_being]
        negative_effect = [y <= average_well_being_at_consumption for y in average_well_being]
        subplot.fill_between(x, average_well_being, average_well_being_at_consumption, where=positive_effect, facecolor='green', interpolate=True)
        subplot.fill_between(x, average_well_being, average_well_being_at_consumption, where=negative_effect, facecolor='red', interpolate=True)

    subplot.set_title(inspected)
    subplot.set_xlim([lower_limit, upper_limit])
    upper_days = int(upper_limit / 24)
    lower_days = int(lower_limit / 24)
    days = range(lower_days, upper_days)
    subplot.set_xticks([0 + x * 24 for x in days])
    subplot.set_xticklabels(["day " + str(x) for x in days])

    plot_number += 1

plt.show()
