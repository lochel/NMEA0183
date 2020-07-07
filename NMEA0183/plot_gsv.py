#!/usr/bin/env python3

import matplotlib.pyplot
import numpy
from math import cos

def plot_gsv(data):
  r = list()
  theta = list()
  label = list()
  for s in data:
    id = s[0]
    elevation = s[1]
    azimuth = s[2]
    snr = s[3]

    if elevation and azimuth:
      label.append(id)
      r.append(cos(float(elevation) / 180.0 * 3.141))
      theta.append(float(azimuth) / 180.0 * 3.141)

  fig = matplotlib.pyplot.figure(figsize=(3, 3), dpi=300)
  ax = matplotlib.pyplot.subplot(1, 1, 1, polar=True)
  ax.set_theta_zero_location('N')
  ax.set_theta_direction(-1)
  ax.plot(theta, r, 'bo')
  for i,j,k in zip(theta, r, label):
    ax.annotate('%s' % k, xy=(i,j))
  ax.set_rmin(0.0)
  ax.set_rmax(1.0)
  ax.set_xticklabels([])
  ax.set_yticklabels([])
  matplotlib.pyplot.title('%d satellites in view' % len(data))
  matplotlib.pyplot.savefig('satellites_in_view.png')
