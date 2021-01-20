# -*- coding:utf8 -*-
import argparse
import csv

import matplotlib.font_manager as mfm
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import numpy as np
font_path = './STHeitiLight.ttc'
prop = mfm.FontProperties(fname=font_path)

parser = argparse.ArgumentParser(description='')
parser.add_argument('--plt_name', default='')
parser.add_argument('--data', default='')
args = parser.parse_args()
print(args)

datafile = args.data
plt_name = args.plt_name

def sortedDictValues1(adict):
    items = adict.items()
    sorted(items)
    return [key for key, _ in items], [value for _, value in items]


def load_data():
    csvfile = csv.DictReader(open(datafile), delimiter='\t')
    datas = {}
    for row in csvfile:
        row['dealdate'] = row['dealdate'][:7]
        row['totalPrice'] = row['totalPrice'].split('-')[0]
        row['unitPrice'] = row['unitPrice'].split('-')[0]
        count = float(row['count'])
        datas[row['dealdate']] = datas.get(row['dealdate'], np.array([0., 0., 0., 0.])) + np.array(
            [float(row['totalPrice']) * count, float(row['unitPrice']) * count, float(row['square'])*count, count])

    datas = sortedDictValues1(datas)

    dates = datas[0]
    AverageTotalPrice = [item[0]/item[-1] for item in datas[1]]
    AverageUnitPrice = [item[1]/item[-1] for item in datas[1]]
    AverageSquare = [item[2]/item[-1] for item in datas[1]]
    DealCounts = [item[-1] for item in datas[1]]
    return dates, AverageTotalPrice, AverageUnitPrice, DealCounts, AverageSquare


if "__main__" == __name__:
    dates, AverageTotalPrice, AverageUnitPrice, DealCounts, AverageSquare = load_data()

    fig = plt.figure(figsize=(14, 8))
    plt.title(fontproperties=prop, label=plt_name)
    plt.xticks(range(len(dates)), dates, rotation=90, fontsize=6)
    plt.yticks([])

    host = host_subplot(111, axes_class=AA.Axes)
    plt.subplots_adjust(left=0.08, right=0.8)

    par1 = host.twinx()
    par2 = host.twinx()
    par3 = host.twinx()

    new_fixed_axis = par2.get_grid_helper().new_fixed_axis
    par2.axis["right"] = new_fixed_axis(loc="right", axes=par2, offset=(60, 0))

    new_fixed_axis = par3.get_grid_helper().new_fixed_axis
    par3.axis["right"] = new_fixed_axis(loc="right", axes=par3, offset=(120, 0))

    par1.axis["right"].toggle(all=True)
    par2.axis["right"].toggle(all=True)
    par3.axis["right"].toggle(all=True)

    host.set_xlim(0, len(dates)-1)
    host.set_ylim(0, max(AverageTotalPrice) * 1.2)

    host.set_ylabel(u"AverageTotalPrice")
    par1.set_ylabel("AverageUnitPrice")
    par2.set_ylabel("DealCounts")
    par3.set_ylabel("AverageSquare")

    p0, = host.plot(dates, AverageTotalPrice, label=u"AverageTotalPrice", linestyle=':', marker='*')
    p1, = par1.plot(range(len(dates)), AverageUnitPrice, label="AverageUnitPrice", linestyle='--', marker='+')
    p2, = par2.plot(range(len(dates)), DealCounts, label="DealCounts", linestyle='-', marker='o')
    p3, = par3.plot(range(len(dates)), AverageSquare, label="AverageSquare", linestyle=':', marker='+')

    par1.set_ylim(0, max(AverageUnitPrice) * 1.2)
    par2.set_ylim(0, max(DealCounts) * 1.2)
    par3.set_ylim(0, max(AverageSquare) * 1.8)

    host.legend(loc='upper left')

    host.set_xticklabels(host.get_xticklabels(), rotation=90, fontsize=6)
    host.axis["left"].label.set_color(p0.get_color())
    par1.axis["right"].label.set_color(p1.get_color())
    par2.axis["right"].label.set_color(p2.get_color())
    par3.axis["right"].label.set_color(p3.get_color())

    plt.show()
