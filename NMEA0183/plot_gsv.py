#!/usr/bin/env python3

import datetime
from math import cos

import matplotlib.pyplot
import numpy


def plot_gsv(data, time):
  r = list()
  theta = list()
  label = list()
  color = list()
  for s in data:
    id = s[0]
    elevation = s[1]
    azimuth = s[2]
    snr = s[3]

    if elevation and azimuth:
      label.append(id)
      r.append(cos(float(elevation) / 180.0 * 3.141))
      theta.append(float(azimuth) / 180.0 * 3.141)
      color.append(snr if snr else 0.0)

  fig = matplotlib.pyplot.figure(figsize=(4, 5), dpi=300)
  ax = matplotlib.pyplot.subplot(1, 1, 1, polar=True)
  ax.set_theta_zero_location('N')
  ax.set_theta_direction(1)

  scatter = ax.scatter(theta, r, c=color)
  for i,j,k in zip(theta, r, label):
    ax.text(i, j, 'PRN%s' % k, fontsize=7)

  ax.set_rmin(0.0)
  ax.set_rmax(1.0)
  ax.set_xticklabels([])
  ax.set_yticklabels([])

  ax.legend(*scatter.legend_elements(num=4), loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, ncol=4, title="SNR - higher is better")

  matplotlib.pyplot.title('%d satellites in view\n%s' % (len(data), time))
  matplotlib.pyplot.savefig('satellites_in_view.png')
