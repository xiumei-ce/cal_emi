# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 15:26:11 2019

@author: chier
"""

import csv
import re
import os
import numpy as np
import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LinearSegmentedColormap  
import matplotlib.patches as patches
import sys
import xlrd
from new import write_pm25
#设置matplotlib正常显示中文和负号
#mpl.rcParams['fonts.sans-serif']=['SimHei']  #用黑体显示中文
mpl.rcParams['axes.unicode_minus']=False     #正常显示负号


#解决报错：_csv.Error: field larger than field limit (131072)

maxInt = sys.maxsize
decrement = True
 
while decrement:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.
 
    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt / 10)
        decrement = True

lim_lon = 118.95
lim_lat =  32.05
nemission=[]
m=0
#reading river speed
inputfile1=r'C:\Users\chier\Desktop\avspeed in a year.xlsx'
wb=xlrd.open_workbook(filename=inputfile1)
sheet=wb.sheet_by_index(0)
river_v = sheet.col_values(6)

# reading ais data
root_dir=r'E:\work\emission\data2'
for file in os.listdir(root_dir):
	inputfile=root_dir+'\\'+file
# inputfile = r'E:\work\calculate emission\data2\output_20181124.csv'
	with open(inputfile,'r') as csvfile:
		readCSV = csv.reader(csvfile)
		times = []
		names = []
		lats  = []
		lons  = []
		speed = []
		mmsi  = []
		nsec  = []
		ship_length = []
		
		for rows in readCSV:
			row=rows
			#row=re.sub('"','',row)
			time = row[0]
			name = row[1]
			mmsi_ship  = row[2]
			speed_ship = float(row[3])
			longitude  = float(row[4])
			latitude  = float(row[5])
			ship_type = int(row[6])
			isec  = float(row[7])
			ilength = float(row[8])
			if 0 <= speed_ship <= 30 and 0 < ilength < 400 and 118.6< longitude <119.0 and 31.9< latitude <32.3:
				if ship_type > 79 and ship_type < 90:
					mmsi.append(mmsi_ship)
					nsec.append(isec)
					speed.append(speed_ship)
					lons.append(longitude)
					lats.append(latitude)
					ship_length.append(ilength)
	for i in range(len(nsec)-1):
		if nsec[i+1] < nsec[i]:
			nsec[i+1] = nsec[i+1]+86400

	river =  float(river_v[m])/1.852  #river speed's unit is km/h, now convert to knot.
	m=m+1
	ummsi = np.unique(mmsi)
	nr_ships = len(np.unique(mmsi))
	shiplist=ummsi
	nr_calls  = [0] * nr_ships
	nr_calls2 = [0] * nr_ships
	ifirst    = [-1] * nr_ships
	ilast     = [0] * nr_ships
	avspeed   = [0] * nr_ships
	ilon      = [0] * nr_ships
	ilat      = [0] * nr_ships
	interval  = [0] * nr_ships
	emi       = [0] * nr_ships
	bi        = [0] * nr_ships
	acspeed   = [0] * nr_ships
	length    = [0] * nr_ships #each ship length

	for j in range(nr_ships):
		avspeed [j] = []
		acspeed [j] = []
		interval[j] = []
		length[j]   = []
		ilon[j]     = []
		ilat[j]     = []
	i=-1
	for shipcode in mmsi:
		i = i+1
		for j in range(nr_ships):
			if shipcode == shiplist[j]:
				nr_calls[j] = nr_calls[j]+1
				if float(lons[i]) < lim_lon and float(lats[i]) > lim_lat:
					if ifirst[j] == -1:
						ifirst[j]=i
					ilast[j]=i
					avspeed[j].append(speed[i])
					acspeed[j].append(speed[i])
					interval[j].append(nsec[i])
					length[j].append(ship_length[i])
					ilon[j].append(lons[i])
					ilat[j].append(lats[i])
					nr_calls2[j] = nr_calls2[j]+1

	for j in range(nr_ships):
		if ifirst[j] != -1:
			if len(avspeed[j])>4:
				for i in range(len(avspeed[j])-1):
					if ilon[j][-1] > ilon[j][0]:
						acspeed[j][i]=float(avspeed[j][i])+river
					if ilon[j][-1] < ilon[j][0]:
						acspeed[j][i]=float(avspeed[j][i])-river
						if acspeed[j][i] < 0:
							acspeed[j][i]=0


	for j in range(nr_ships):
		print (' ')
		emission=[]
		if ifirst[j] != -1:
			il=ilast[j]
			bias    =[]
			if len(avspeed[j])>4:
				for i in range(len(acspeed[j])-1):
					c=float(nr_calls2[j]+1)/float(nr_calls2[j]) 
					formula=8.692*10**(-5)*((length[j][0])**2)*(((acspeed[j][i+1]+acspeed[j][i])*1.852/2)**3)*(interval[j][i+1]-interval[j][i])*c*0.95*0.47*0.98/3600
					load=((acspeed[j][i+1]+acspeed[j][i])*1.852/2/12)**3
					if load >=0.195:
						emission.append(formula)
					elif 0.185<= load < 0.195:
						emission.append(formula*1.02)
					elif 0.175<= load < 0.185:
						emission.append(formula*1.04)
					elif 0.165<= load < 0.175:
						emission.append(formula*1.06)
					elif 0.155<= load < 0.165:
						emission.append(formula*1.08)
					elif 0.145<= load < 0.155:
						emission.append(formula*1.11)
					elif 0.135<= load < 0.145:
						emission.append(formula*1.15)
					elif 0.125<= load < 0.135:
						emission.append(formula*1.19)
					elif 0.115<= load < 0.125:
						emission.append(formula*1.24)
					elif 0.105<= load < 0.115:
						emission.append(formula*1.30)
					elif 0.095<= load < 0.105:
						emission.append(formula*1.38)
					elif 0.085<= load < 0.095:
						emission.append(formula*1.48)
					elif 0.075<= load < 0.085:
						emission.append(formula*1.61)
					elif 0.065<= load < 0.075:
						emission.append(formula*1.79)
					elif 0.055<= load < 0.065:
						emission.append(formula*2.04)
					elif 0.045<= load < 0.055:
						emission.append(formula*2.44)
					elif 0.035<= load < 0.045:
						emission.append(formula*3.09)
					elif 0.025<= load < 0.035:
						emission.append(formula*4.33)
					elif 0.015<= load < 0.025:
						emission.append(formula*7.29)
					elif 0< load < 0.015:
						emission.append(formula*19.17)
					if interval[j][i+1]-interval[j][i]>600: # if ship interval>10 min, ship will remove other place by definition
						if load >=0.195:
							bias.append(formula)
						elif 0.185<= load <0.195:
							bias.append(formula*1.02)
						elif 0.175<= load <0.185:
							bias.append(formula*1.04)
						elif 0.165<= load <0.175:
							bias.append(formula*1.06)
						elif 0.155<= load <0.165:
							bias.append(formula*1.08)
						elif 0.145<= load <0.155:
							bias.append(formula*1.11)
						elif 0.135<= load <0.145:
							bias.append(formula*1.15)
						elif 0.125<= load <0.135:
							bias.append(formula*1.19)
						elif 0.115<= load <0.125:
							bias.append(formula*1.24)
						elif 0.105<= load <0.115:
							bias.append(formula*1.3)
						elif 0.095<= load <0.105:
							bias.append(formula*1.38)
						elif 0.085<= load <0.095:
							bias.append(formula*1.48)
						elif 0.075<= load <0.085:
							bias.append(formula*1.61)
						elif 0.065<= load <0.075:
							bias.append(formula*1.79)
						elif 0.055<= load <0.065:
							bias.append(formula*2.04)
						elif 0.045<= load <0.055:
							bias.append(formula*2.44)
						elif 0.035<= load <0.045:
							bias.append(formula*3.09)
						elif 0.025<= load <0.035:
							bias.append(formula*4.33)
						elif 0.015<= load <0.025:
							bias.append(formula*7.29)
						elif 0< load <0.015:
							bias.append(formula*19.17)
				bi[j]=sum(bias)		
				emi[j]=sum(emission)-bi[j]
		
	nemission.append(sum(emi))
	
# while 0 in nemission:
	# nemission.remove(0)
	
print (nemission)

write_pm25(2,nemission)

