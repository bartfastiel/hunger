#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import matplotlib.pyplot as plt
from parsers import load_ingredients, resolve_ingredients, parse_diary, mean

lower_limit = -1 * 24
upper_limit = +4 * 24

sort_by_number_of_consumptions = False

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
