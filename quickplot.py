#!/usr/bin/python3
# -*- coding: iso-8859-15 -*-

import matplotlib
from matplotlib import pyplot
import sys
import csv
import os
import argparse
import collections

__author__ = "Markus Mäsker"
__email__ = "maesker@gmx.net"
__version__ = "1.0"
__status__ = "Development"


DEFAULT_FIG_SIZE = (17, 9)
STRIP_CHARS = ' \n\t$€%'


class Series:

    def __init__(self, name=""):
        self.name = name
        self.values = collections.OrderedDict()

    def add(self, key, val):
        self.values[key] = val

    def get_range(self, minkey, maxkey):
        x = []
        y = []
        xapp = x.append
        yapp = y.append
        for k, v in self.values.items():
            if minkey <= k:
                if k > maxkey:
                    break
                xapp(k)
                yapp(v)
        return x, y


class Csvplotter:

    def __init__(self, args):
        self.data = {}
        self.figure = pyplot.figure(figsize=DEFAULT_FIG_SIZE)
        self.subplots = {}
        self.noheader = args.noheader
        self.attrs = args.columns.split(',')
        self.tmpatts = args.columns.split(',')
        self.delimiter = args.delimiter

    def csv_import(self, file):
        def convert_value(val):
            try:
                return float(val.strip(STRIP_CHARS))
            except ValueError:
                if len(val) == 0:
                    return
                print(
                    "Row index: %i, float(%s) failed." %
                    (rowindex, k))

        absfile = os.path.join(os.getcwd(), file)
        if not os.path.isfile(absfile):
            print("File %s not found." % absfile)
            exit(1)

        with open(absfile, 'r') as csvfile:
            look_for_header = not self.noheader
            rowindex = 0
            for row in csv.reader(csvfile, delimiter=self.delimiter):
                index = 0
                if look_for_header:
                    look_for_header = False
                    tmp = []
                    for k in row:
                        for pat in self.tmpatts:
                            if pat == k:
                                print("add header:", pat)
                                tmp.append(k)
                                break
                        key = k.strip()
                        s = Series(key)
                        self.data[index] = s
                        index += 1
                    self.attrs = tmp
                else:
                    rowindex += 1
                    s = None
                    for k in row:
                        if index not in self.data.keys():
                            s = Series(index)
                            self.data[index] = s
                        else:
                            s = self.data[index]
                        s.add(rowindex, convert_value(k))
                        index += 1

    def gen_subplots(self):
        bottempos = 0.12
        subplotwidth = 0.92
        subplotheight = (0.95 - bottempos) / len(self.attrs)
        subplotindex = 0
        self.minx = sys.maxsize
        self.maxx = -sys.maxsize
        for key, val in sorted(self.data.items()):
            if val.name in self.attrs:
                self.subplots[key] = self.figure.add_axes(
                    (0.06,
                     bottempos + (subplotindex * subplotheight),
                        subplotwidth,
                        subplotheight),
                    ylabel=val.name)
                subplotindex += 1
                self.figure.add_subplot()
                for x, y in val.values.items():
                    self.maxx = max(self.maxx, x)
                    self.minx = min(self.minx, x)

    def get_data(self, key, start, end):
        if key in self.data.keys():
            diff = self.maxx - self.minx
            s = self.minx + (diff * (start / 100))
            e = self.minx + (diff * (end / 100))
            return self.data[key].get_range(s, e)
        return [], []

    def slided_plotter(self):
        min_ref = min
        max_ref = max
        range_ref = range
        slax1 = self.figure.add_axes((0.08, 0.05, 0.85, 0.04))
        sl1 = matplotlib.widgets.Slider(slax1, "Trace", 0, 100, valinit=50.0)
        slax2 = self.figure.add_axes((0.08, 0.01, 0.85, 0.04))
        sl2 = matplotlib.widgets.Slider(
            slax2,
            "Window size",
            0,
            100,
            valinit=100.0)
        self.gen_subplots()

        def update_trace(arg):
            tracenum = sl1.val
            windowsize = sl2.val
            start = max_ref(0, tracenum - windowsize / 2)
            end = min_ref(tracenum + windowsize / 2, 100)
            for key, plot in sorted(self.subplots.items()):
                yaxis = plot.get_yaxis()
                name = yaxis.get_label_text()
                plot.cla()
                x, y = self.get_data(key, start, end)

                minx = min_ref(x)
                maxx = max_ref(x)
                ticks = []

                tickcnt = 10
                for i in range_ref(tickcnt):
                    ticks.append(minx + ((maxx - minx) / (tickcnt - 1)) * i)
                plot.set_xticks(ticks)
                plot.plot(x, y)
                yaxis.set_label_text(name)
            self.figure.canvas.draw()
        update_trace(None)
        sl1.on_changed(update_trace)
        sl2.on_changed(update_trace)
        pyplot.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Visualize selected columns from a csv file.')
    parser.add_argument('-f', '--file', help='CSV File to plot', required=True)
    parser.add_argument(
        '-c', '--columns', help='Comma separated list of columns to plot',
        required=True)
    parser.add_argument(
        '-n',
        '--noheader',
        help='CSV File does not contain a header file',
        default=False,
        action='store_true')
    parser.add_argument(
        '-d',
        '--delimiter',
        help='Delimiter used in the csv file. Default is ";" ',
        default=";")

    args = parser.parse_args()
    a = Csvplotter(args)
    a.csv_import(args.file)
    a.slided_plotter()
