#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import ceil, log10
import numpy as np
import pysvg.structure
import pysvg.builders
import pysvg.shape
import pysvg.text
from scipy.stats import skewnorm

dist = skewnorm

loc1 = 10
a1 = 4.0
scale1 = 1
loc2 = 11
a2 = 10.0
scale2 = 0.4

gridx = 50
gridy = 50

gen1 = np.zeros((gridx,gridy), int)
gent1 = np.empty((gridx,gridy))
stalled1 = np.empty((gridx,gridy))
gen2 = np.zeros((gridx,gridy), int)
gent2 = np.empty((gridx,gridy))
stalled2 = np.empty((gridx,gridy))

scale = 4.0

width = 500*scale
height = 250*scale
cr = 4*scale

def plot(t, total, g1, g2):
    tndigits = int(ceil(log10(total)))
    svg = pysvg.structure.svg(width = width, height = height)

    mingen = min(np.min(g1), np.min(g2))
    maxgen = max(np.max(g1), np.max(g2))

    textstyle = pysvg.builders.StyleBuilder()
    textstyle.setFilling('#000000')
    textstyle.setFontSize(24)
    textstyle.setFontFamily('sans')

    text = pysvg.text.text("t = {}".format(t), 20, 30)
    text.set_style(textstyle.getStyle())
    svg.addElement(text)

    rectstyle = pysvg.builders.StyleBuilder()
    rectstyle.setFilling('rgb(102,178,255)')

    def pgrid(g, cx, cy):
        rect = pysvg.shape.rect(x = cx-2*cr, y = cy-2*cr, width = (gridx+3)*cr, height = (gridy+3)*cr)
        rect.set_style(rectstyle.getStyle())
        svg.addElement(rect)

        for y in range(gridy):
            for x in range(gridx):
                if mingen == maxgen:
                    grey = 100.0
                else:
                    grey = 100.0 * (g[y][x] - mingen) / (maxgen - mingen)
                circle = pysvg.shape.circle(cx = cx+cr*x, cy = cy+cr*y, r = cr/2)
                circle_style = pysvg.builders.StyleBuilder()
                circle_style.setFilling('rgb({}%,{}%,{}%)'.format(grey,grey,grey))
                circle.set_style(circle_style.getStyle())
                svg.addElement(circle)
                
        text = pysvg.text.text("min gen = {}   max gen = {}".format(int(np.min(g)), int(np.max(g))), cx-2*cr, height-30)
        text.set_style(textstyle.getStyle())
        svg.addElement(text)

    pgrid(g1, int((width-2*cr*gridx)/3), int((height-cr*gridy)/2))
    pgrid(g2, int(width/2+(width-2*cr*gridx)/3), int((height-cr*gridy)/2))

    svg.save(filename = "gen-t{:0{prec}d}.svg".format(t, prec=tndigits))

def can_start(stalled, x, y):
    res = 0.0
    for dy in range(-1,2):
        for dx in range(-1,2):
            if x+dx >= 0 and x+dx < gridx and y+dy >= 0 and y+dy < gridy and not stalled[y][x]:
                return False
    return True

def maxt_env(gt, x, y):
    res = 0
    for dy in range(-1,2):
        for dx in range(-1,2):
            if x+dx >= 0 and x+dx < gridx and y+dy >= 0 and y+dy < gridy:
                res = max(res, gt[y+dy][x+dx])
    return res

def inc_gen(t, g, gt, stalled, loc, a, scale):
    for y in range(gridy):
        for x in range(gridx):
            if not stalled[y][x] and gt[y][x] <= t:
                g[y][x] += 1
                stalled[y][x] = True

    update = [(x, y, maxt_env(gt, x, y)) for y in range(gridy) for x in range(gridx) if can_start(stalled, x, y)]

    for ux, uy, ut in update:
        gt[uy][ux] = ut + dist.rvs(a, loc=loc, scale=scale)
        stalled[uy][ux] = 0

def init_gen(gt, stalled, loc, a, scale):
    for y in range(gridy):
        for x in range(gridx):
            gt[y][x] = dist.rvs(a, loc=loc, scale=scale)
            stalled[y][x] = False

def min_t(after, gt, stalled):
    res = 100000000
    for y in range(gridy):
        for x in range(gridx):
            if not stalled[y][x] and gt[y][x] < res:
                res = gt[y][x]
    return res

t = 0.0
dt = 100
total = 5000
lastt = -dt

init_gen(gent1, stalled1, loc1, a1, scale1)
init_gen(gent2, stalled2, loc2, a2, scale2)

while t < total:
    mint = min(min_t(t, gent1, stalled1), min_t(t, gent2, stalled2))
    print(mint)
    if mint - lastt >= dt:
        lastt += dt
        plot(lastt, total, gen1, gen2)
        continue

    # To accelerate we update all cells which are within half of the medium of the minimal value.
    # This should guarantee that no completed job is uncounted.
    t = min(lastt + dt, mint + min(loc1, loc2) / 2)

    inc_gen(t, gen1, gent1, stalled1, loc1, a1, scale1)
    inc_gen(t, gen2, gent2, stalled2, loc2, a2, scale2)
