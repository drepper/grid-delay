#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import svgwrite
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

def plot(t, g1, g2):
    svg = svgwrite.Drawing(filename="gen-t{}.svg".format(t), size=("{}px".format(width), "{}px".format(height)))

    mingen = min(np.min(g1), np.min(g2))
    maxgen = max(np.max(g1), np.max(g2))

    title = svg.add(svg.g(font_size=24, font_family="sans"))
    title.add(svg.text("t = {}".format(t), (20, 30)))

    geninfo = svg.add(svg.g(font_size=24, font_family="sans"))

    def pgrid(g, cx, cy):
        svg.add(svg.rect((cx-2*cr,cy-2*cr), ((gridx+3)*cr,(gridy+3)*cr), fill="rgb(0,20,200)"))

        for y in range(gridy):
            for x in range(gridx):
                if mingen == maxgen:
                    grey = 100.0
                else:
                    grey = 100.0 * (g[y][x] - mingen) / (maxgen - mingen)
                svg.add(svg.circle(center=(cx+cr*x,cy+cr*y), r=cr/2, fill=svgwrite.rgb(grey, grey, grey, mode='%')))
                
        geninfo.add(svg.text("min gen = {}   max gen = {}".format(int(np.min(g)), int(np.max(g))), (cx-2*cr,height-30)))

    pgrid(g1, int((width-2*cr*gridx)/3), int((height-cr*gridy)/2))
    pgrid(g2, int(width/2+(width-2*cr*gridx)/3), int((height-cr*gridy)/2))

    svg.save()

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
        plot(lastt, gen1, gen2)
        continue

    # To accelerate we update all cells which are within half of the medium of the minimal value.
    # This should guarantee that no completed job is uncounted.
    t = min(lastt + dt, mint + min(loc1, loc2) / 2)

    inc_gen(t, gen1, gent1, stalled1, loc1, a1, scale1)
    inc_gen(t, gen2, gent2, stalled2, loc2, a2, scale2)
