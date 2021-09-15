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
import xlsxwriter
from new import write_so
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
# inputfile = r'E:\work\calculate emission\data2\output_20181126.csv'
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
				if ship_type > 59 and ship_type < 70:
					mmsi.append(mmsi_ship)
					nsec.append(isec)
					speed.append(speed_ship)
					lons.append(longitude)
					lats.append(latitude)
					ship_length.append(ilength)
	for i in range(len(nsec)-1):
		if nsec[i+1] < nsec[i]:
			nsec[i+1] = nsec[i+1]+86400

	river = float(river_v[m])/1.852  #river speed's unit is km/h, now convert to knot.
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
		bias    =[]
		if ifirst[j] != -1:
			il=ilast[j]
			if len(acspeed[j])>4:
				for i in range(len(acspeed[j])-1):
					c=float(nr_calls2[j]+1)/float(nr_calls2[j]) 
					formula=4.26*10**(-5)*((length[j][0])**2)*(((acspeed[j][i+1]+acspeed[j][i])*1.852/2)**3)*(interval[j][i+1]-interval[j][i])*c*(11.44)*0.56*0.98/3600
					load=((acspeed[j][i+1]+acspeed[j][i])*1.852/2/14.3)**3
					emission.append(formula)
					if interval[j][i+1]-interval[j][i]>600: # if ship interval>10 min, ship will remove other place by definition
						bias.append(formula)
				bi[j]=sum(bias)		
				emi[j]=sum(emission)-bi[j]
		
	nemission.append(sum(emi))
	
# while 0 in nemission:
	# nemission.remove(0)
	
print (nemission)

write_so(3,nemission)

