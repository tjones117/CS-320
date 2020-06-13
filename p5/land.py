# project: p5
# submitter: tjones25
# partner: none

#!/usr/bin/env python
# coding: utf-8
from zipfile import ZipFile
import sqlite3
import os
import pandas as pd
import io
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap

def open(name):
    obj = Connection(name)
    return obj

class Connection:
    def __init__(self, name):
        self.db = sqlite3.connect(name+".db")
        self.zf = ZipFile(name+".zip")
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        pass

    def close(self):
        self.db.close()
        self.zf.close()
        
    def list_images(self):
        read = pd.read_sql("SELECT image FROM images GROUP By image", self.db)
        return read['image'].tolist()
    
    def image_year(self, name):
        read = pd.read_sql("SELECT * FROM images", self.db)
        return int(read.loc[read['image'] == name]['year'])
    
    def image_name(self, name):
        read = pd.read_sql("SELECT * FROM images", self.db)
        index = int(read.loc[read['image'] == name]['place_id'])
        read = pd.read_sql("SELECT * FROM places", self.db)
        exit = read.loc[read['place_id'] == index]
        return exit.iloc[0]['name']
    
    def image_load(self, name):
        with self.zf.open(name) as f:
            buf = io.BytesIO(f.read())
            out = np.load(buf)
        return out[:,:]
    
    def lat_regression(self, use_code, ax=None):
        read = pd.read_sql("SELECT * FROM places", self.db)
        sample_ids = []
        lat = []
        for index, row in read.iterrows():
            if row['name'][:4] == 'samp':
                sample_ids.append(row['place_id'])
                lat.append(row['lat'])
                
        read = pd.read_sql("SELECT * FROM images", self.db)
        percent = []
        for item in sample_ids:
            area = read.loc[read['place_id'] == item]
            name = area.iloc[0]['image']
            array = self.image_load(name)
            total_code = array[np.isin(array, [use_code])].size
            percentage = (total_code/array.size) * 100
            percent.append(percentage)
        
        lat_array = np.array(lat)
        lat_array = lat_array.reshape(-1, 1)
        lin = LinearRegression().fit(lat_array, np.array(percent))
        coef = lin.coef_[0]
        interc = lin.intercept_
        final = [coef, interc]
        
        if ax != None:
            ax.scatter(lat, percent)
            ax.plot(lat, (coef*lat_array) + interc)
        return tuple(final)
    
    def year_regression(self, place, codes, ax=None):
        read = pd.read_sql("SELECT * FROM places", self.db)
        place_id = read.loc[read['name'] == place].iloc[0]['place_id']
                
        read = pd.read_sql("SELECT * FROM images", self.db)
        percent = []
        years = []
        area = read.loc[read['place_id'] == place_id]
        for index, row in area.iterrows():
            years.append(row['year'])
            name = row['image']
            array = self.image_load(name)
            total_code = array[np.isin(array, [codes])].size
            percentage = (total_code/array.size) * 100
            percent.append(percentage)
        
        years_array = np.array(years)
        years_array = years_array.reshape(-1, 1)
        lin = LinearRegression().fit(years_array, np.array(percent))
        coef = lin.coef_[0]
        interc = lin.intercept_
        final = [coef, interc]
        
        if ax!= None:
            ax.scatter(years, percent)
            ax.plot(years, (coef*years_array) + interc)
        return tuple(final)
    
    def animate(self, place):
        read = pd.read_sql("SELECT * FROM places", self.db)
        place_id = read.loc[read['name'] == place].iloc[0]['place_id']
                
        read = pd.read_sql("SELECT * FROM images", self.db)
        images = []
        years = []
        area = read.loc[read['place_id'] == place_id]
        for index, row in area.iterrows():
            years.append(row['year'])
            name = row['image']
            array = self.image_load(name)
            images.append(array)
            
        fig, ax = plt.subplots(figsize=(8, 8))
        
        def draw_frame(frame_num):
            use_cmap = np.zeros(shape=(256,4))
            use_cmap[:,-1] = 1
            uses = np.array([
                [0, 0.00000000000, 0.00000000000, 0.00000000000],
                [11, 0.27843137255, 0.41960784314, 0.62745098039],
                [12, 0.81960784314, 0.86666666667, 0.97647058824],
                [21, 0.86666666667, 0.78823529412, 0.78823529412],
                [22, 0.84705882353, 0.57647058824, 0.50980392157],
                [23, 0.92941176471, 0.00000000000, 0.00000000000],
                [24, 0.66666666667, 0.00000000000, 0.00000000000],
                [31, 0.69803921569, 0.67843137255, 0.63921568628],
                [41, 0.40784313726, 0.66666666667, 0.38823529412],
                [42, 0.10980392157, 0.38823529412, 0.18823529412],
                [43, 0.70980392157, 0.78823529412, 0.55686274510],
                [51, 0.64705882353, 0.54901960784, 0.18823529412],
                [52, 0.80000000000, 0.72941176471, 0.48627450980],
                [71, 0.88627450980, 0.88627450980, 0.75686274510],
                [72, 0.78823529412, 0.78823529412, 0.46666666667],
                [73, 0.60000000000, 0.75686274510, 0.27843137255],
                [74, 0.46666666667, 0.67843137255, 0.57647058824],
                [81, 0.85882352941, 0.84705882353, 0.23921568628],
                [82, 0.66666666667, 0.43921568628, 0.15686274510],
                [90, 0.72941176471, 0.84705882353, 0.91764705882],
                [95, 0.43921568628, 0.63921568628, 0.72941176471],
            ])
            for row in uses:
                use_cmap[int(row[0]),:-1] = row[1:]
            use_cmap = ListedColormap(use_cmap)
            plt.imshow(images[frame_num], cmap=use_cmap, vmin=0, vmax=255)
            plt.title(years[frame_num])

        anim = FuncAnimation(fig, draw_frame, frames=len(years), interval=1000)
        html = anim.to_html5_video()
        plt.close(fig)
        return html