#!/usr/bin/python3
# -*- coding: latin-1 -*-

"""
Preference statistics
"""

import collections
import re
import tomuss_init
from ..PLUGINS import suivi_preferences
from .. import utilities
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
plt = matplotlib.pyplot

not_modifiable_by_user = {
    "v_scrollbar",
    "scrollbar_right",
    "home_3scrollbar",
    "display_tips",
    "interface", # Must be modifiable in the futur
    }

deprecated = {
    "nr_lines",
    "nr_cols",
    "favoris_sort",
    "nr_favorites",
    }

yes = utilities._("yes")
no = utilities._("no")

class Preference:
    def __init__(self, preference):
        self.values = {}
        self.preference = preference
    def add(self, value):
        self.values[value] = self.values.get(value, 0) + 1
    def terminate(self):
        self.nr_user = sum(self.values.values())
        self.nr_choices = len(self.values)
        self.choices = sorted(self.values.items())
        choices = set(self.values)
        choices.discard("0")
        choices.discard("1")
        self.boolean = len(choices) == 0
    def plot(self):
        print("{}[{}]".format(self.preference,  self.nr_user), end="")
        msg = utilities._("Preferences_" + self.preference)
        if msg.startswith("Preferences_"):
            msg = utilities._("Preference_" + self.preference)
            if msg.startswith("Preference_"):
                msg = utilities._("MSG_" + self.preference)
                if msg.startswith("MSG_"):
                    msg = self.preference
        msg = re.sub(" *<[^>]*> *", " ", msg).strip("  :.")
        msg = msg[0].upper() + msg[1:] + ' [' + str(self.nr_user) + ']'
        plt.text(0.11, self.y + self.nr_choices + 0.2, msg, color=(0,0,0))
        for i, (k, nr) in enumerate(self.choices):
            print(" {}:{}%".format(k, int(100*nr/self.nr_user)), end="")
            y = self.y + i
            if self.boolean and k == "1":
                color = (0.75, 1, 0.75)
            else:
                color= (0.75, 0.75, 0.75)
            plt.barh((y,), (nr,), 1, color=color, linewidth=0)
            if self.boolean:
                label = yes if k == '1' else no
            else:
                label = k
            percent = 100*nr/self.nr_user
            if percent >= 10:
                percent = str(int(percent))
            elif percent >= 1:
                percent = "{:.1f}".format(percent)
            elif percent >= 0.1:
                percent = "{:.2f}".format(percent)
            else:
                percent = "{:.3f}".format(percent)
            plt.text(0.2, y+0.5, "{} : {}%".format(label, percent),
                     verticalalignment='center', color=(0,0,1))
        print()

class Preferences:
    def __init__(self):
        self.preferences = {}
        for dummy_login, d in suivi_preferences.read():
            for k in sorted(d):
                self.add(k, str(d[k]))
        self.terminate()

    def add(self, preference, value):
        if preference not in self.preferences:
            self.preferences[preference] = Preference(preference)
        self.preferences[preference].add(value)

    def terminate(self):
        self.sorted = [preference
                       for preference in self.preferences.values()
                       if preference.preference not in deprecated
                       and preference.preference not in not_modifiable_by_user
                       ]
        self.sorted.sort(key = lambda x: x.preference, reverse=True)
        i = 0
        for preference in self.sorted:
            preference.y = i
            preference.terminate()
            i += preference.nr_choices + 1
        self.max = max(preference.nr_user
                       for preference in self.sorted)

    def yticks(self):
        return [preference.y + preference.nr_choices/2
                for preference in self.sorted]
    def ylabels(self):
        return [preference.preference
                for preference in self.sorted]

    def plot(self):
        plt.figure(figsize=(8, 20))
        plt.axes().set_xscale("log")
        plt.axes().set_xlim(xmin=0.1, xmax=self.max)
        plt.axes().set_ylim(ymin=0, ymax=self.sorted[-1].y + self.sorted[-1].nr_choices + 1)
        plt.axes().set_yticks(self.yticks())
        plt.axes().set_yticklabels(self.ylabels(), multialignment='center')
        plt.tick_params(labeltop=True)
        for preference in self.sorted:
            preference.plot()
        plt.tight_layout()
        plt.savefig("TMP/xxx.preferences.png")

Preferences().plot()


