#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import matplotlib.pyplot as plt
from parsers import load_ingredients, resolve_ingredients, parse_diary, mean
import numpy as np

sort_by_number_of_consumptions = True

impact_hours_max = 24 * 5  # from two days before poor well-being
impact_hours_min = 24 * 2  # to   one day  before poor well-being

with io.open("ingredients.txt", encoding="utf-8") as f:
    ingredients_raw = f.readlines()

with io.open("diary.txt", encoding="utf-8") as f:
    diary_raw = f.readlines()

ingredients_unresolved = load_ingredients(ingredients_raw)
ingredients_resolved = resolve_ingredients(ingredients_unresolved)
ingredients_diary, wellbeing_diary = parse_diary(diary_raw, ingredients_resolved, interpolate=False)

all_ingredients = []
all_ingredients.extend(ingredients_resolved.keys())
for ingredients_of_diary_entry in ingredients_diary.values():
    all_ingredients.extend(ingredients_of_diary_entry)

all_ingredients_unique = list(set(all_ingredients))
all_ingredients_unique.sort()

critical_idx = []
non_critical_idx = []

for idx in wellbeing_diary.keys():
    influence_area = range(idx + impact_hours_min, idx + impact_hours_max)
    critical = False
    for influence_idx in influence_area:
        if influence_idx in wellbeing_diary:
            if wellbeing_diary[influence_idx] < -0.5:
                critical = True
    if critical:
        critical_idx.append(idx)
    else:
        non_critical_idx.append(idx)

print(str(len(critical_idx)) + " critical times")
print(str(len(non_critical_idx)) + " non-critical times")
all_idx = len(critical_idx) + len(non_critical_idx)

typical_influence = len(critical_idx) / all_idx
print("typical influence: " + str(typical_influence))

critical_ingredients = []
for idx in critical_idx:
    if idx in ingredients_diary:
        critical_ingredients += ingredients_diary[idx]
critical_ingredients.sort()

non_critical_ingredients = []
for idx in non_critical_idx:
    if idx in ingredients_diary:
        non_critical_ingredients += ingredients_diary[idx]
non_critical_ingredients.sort()

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


def make_rgb_transparent(rgb, bg_rgb, alpha):
    return [alpha * c1 + (1 - alpha) * c2
            for (c1, c2) in zip(rgb, bg_rgb)]


influences = []
certainities = []
idx = 0
for ingredient in interesting_ingredients:
    bad = critical_ingredients.count(ingredient)
    good = non_critical_ingredients.count(ingredient)
    sum = bad + good
    if sum != 0:
        influence = 0 - (((bad / sum) * 2) - 1)
    else:
        influence = 0.0

    certainities.append(sum)

    # if influence < typical_influence:
    #     clean_influence = (influence - typical_influence) / (1 + typical_influence)
    # elif influence == typical_influence:
    #     clean_influence = 0
    # else:
    #     clean_influence = (influence - typical_influence) / (1 - typical_influence)
    clean_influence = influence

    print(ingredient.rjust(50) + " bad:" + str(bad).rjust(3) + " good:" + str(good).rjust(
        3) + " influence: " + '{:+1.2f}'.format(influence) + " clean_influence: " + '{:+1.2f}'.format(clean_influence))

    influences.append(clean_influence)
    idx += 1

max_certainity = max(certainities)
colors = []
for idx, influence in enumerate(influences):
    if influence > 0:
        full_color = [0, 128, 0]
    else:
        full_color = [255, 0, 0]
    relative_certainity = certainities[idx] / max_certainity
    alpha_color = make_rgb_transparent(full_color, [255, 255, 255], relative_certainity)
    hex_color = ''.join('{:02X}'.format(int(a)) for a in alpha_color)
    colors.append("#" + hex_color)

plt.rcdefaults()
fig, ax = plt.subplots()

fig.set_size_inches(6, len(interesting_ingredients) * 0.2 + 1)

interesting_ingredients.insert(0, "bias")
influences.insert(0, typical_influence)
if typical_influence > 0:
    colors.insert(0, "#008000")
else:
    colors.insert(0, "#FF0000")

y_pos = np.arange(len(interesting_ingredients))

ax.barh(y_pos, influences,
        # xerr=error,
        align='center',
        color=colors, ecolor='black')
ax.set_yticks(y_pos)
ax.set_yticklabels(interesting_ingredients)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlim(-1.1, +1.1)

plt.show()
