#!/usr/bin/env python
# coding: utf-8

# In[285]:


# project: p2
# submitter: tjones25
# partner: none


# In[286]:


from math import sin, cos, asin, sqrt, pi
import pandas as pd
from zipfile import ZipFile
from datetime import datetime

def haversine_miles(lat1, lon1, lat2, lon2):
    """Calculates the distance between two points on earth using the
    harversine distance (distance between points on a sphere)
    See: https://en.wikipedia.org/wiki/Haversine_formula

    :param lat1: latitude of point 1
    :param lon1: longitude of point 1
    :param lat2: latitude of point 2
    :param lon2: longitude of point 2
    :return: distance in miles between points
    """
    lat1, lon1, lat2, lon2 = (a/180*pi for a in [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon/2) ** 2
    c = 2 * asin(min(1, sqrt(a)))
    d = 3956 * c
    return d


class Location:
    """Location class to convert lat/lon pairs to
    flat earth projection centered around capitol
    """
    capital_lat = 43.074683
    capital_lon = -89.384261

    def __init__(self, latlon=None, xy=None):
        if xy is not None:
            self.x, self.y = xy
        else:
            # If no latitude/longitude pair is given, use the capitol's
            if latlon is None:
                latlon = (Location.capital_lat, Location.capital_lon)

            # Calculate the x and y distance from the capital
            self.x = haversine_miles(Location.capital_lat, Location.capital_lon,
                                     Location.capital_lat, latlon[1])
            self.y = haversine_miles(Location.capital_lat, Location.capital_lon,
                                     latlon[0], Location.capital_lon)

            # Flip the sign of the x/y coordinates based on location
            if latlon[1] < Location.capital_lon:
                self.x *= -1

            if latlon[0] < Location.capital_lat:
                self.y *= -1

    def dist(self, other):
        """Calculate straight line distance between self and other"""
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __repr__(self):
        return "Location(xy=(%0.2f, %0.2f))" % (self.x, self.y)


# In[361]:


class BusDay:
    def __init__(self, date):
        str_date = int(date.strftime("%Y") + date.strftime("%m") + date.strftime("%d"))
        day = date.weekday()
        with ZipFile('mmt_gtfs.zip') as zf:
            with zf.open("calendar.txt") as f:
                df = pd.read_csv(f)
                self.service_ids = []
                for index, row in df.iterrows():
                    if row[9] <= str_date and row[10] >= str_date:
                        if row[day+2] == 1:
                            self.service_ids.append(row[0])
                    
    def service_ids(self):
        return repr(self.service_ids)
    
    def get_trips(self, id=None):
        with ZipFile('mmt_gtfs.zip') as zf:
            with zf.open("trips.txt") as f:
                df = pd.read_csv(f)
                self.trips = []
                
                ids = df[df["service_id"].isin(self.service_ids)]
                
                for index, row in ids.iterrows():    
                    if id == None:
                        if row[13] == 1:
                            bikes = True
                        elif row[13] == 0:
                            bikes == False
                        trip = Trip(row[3], row[1], bikes)
                        self.trips.append(trip)

                    else:
                        if row[1] == id:
                            if row[13] == 1:
                                bikes = True
                            elif row[13] == 0:
                                bikes == False
                            trip = Trip(row[3], row[1], bikes)
                            self.trips.append(trip)
                                    
        t = sorted(self.trips, key = lambda x: (x.trip_id))                            
        return t
    
    def get_stops(self):
        with ZipFile('mmt_gtfs.zip') as zf:
            with zf.open("stop_times.txt") as f:
                df = pd.read_csv(f)
                trips2 = []
                trips = self.get_trips()
                for i in trips:
                    trips2.append(i.trip_id)
                    
                trans = df[df["trip_id"].isin(trips2)]
                temp = []
                for index, row in trans.iterrows():
                    temp.append(row[2])
                                  
            with zf.open("stops.txt") as g:
                df = pd.read_csv(g)
                self.stops = []
                
                new = df[df["stop_id"].isin(temp)]
                
                for index, row in new.iterrows():
                    loc = Location(latlon = (row[4], row[5]))
                    if row[12] == 1:
                        wheelchairs = True
                    else:
                        wheelchairs = False
                    stop = Stop(row[0], loc, wheelchairs)
                    self.stops.append(stop)
        
        final = sorted(self.stops, key = lambda s: s.stop_id)
        return final
    
    def get_stops_rect(self, x, y):
        if x[0] < x[1]:
            self.x1 = x[0]
            self.x2 = x[1]
        else:
            self.x1 = x[1]
            self.x2 = x[0]
            
        if y[0] < y[1]:
            self.y1 = y[0]
            self.y2 = y[1]
        else:
            self.y1 = y[1]
            self.y2 = y[0]
            
        final = []
        
        stops = self.get_stops()
        
        for s in stops:
            if s.loc_x >= self.x1 and s.loc_x <= self.x2: 
                if s.loc_y >= self.y1 and s.loc_y <= self.y2:
                    final.append(s)
            else:
                pass
        
#         nodes = Node(self.get_stops())
#         nodes_l = nodes.left_child
#         nodes_r = nodes.right_child
        
#         inner_l = nodes_l[-1]
#         inner_r = nodes_r[0]
        
#         if self.children != None:
#             nodes = nodes.left_child
#             self.get_stops_rect(nodes.left_child, (self.x1, self.x2), (self.y1, self.y2))
#         else:
#             nodes = 
        
        return final
        
        
    def get_stops_circ(self, coord, radius):
        self.x = coord[0]
        self.y = coord[1]
        self.radius = radius
        
        rect = self.get_stops_rect(((self.x - self.radius), (self.x + self.radius)), ((self.y - self.radius), (self.y + self.radius)))
        
        final = []
        for stop in rect:
            dist = ((stop.loc_x-self.x)**2 + (stop.loc_y-self.y)**2)**(0.5)
            if dist <= self.radius:
                final.append(stop)
        
        return final


# In[362]:


class Trip:
    def __init__(self, trip_id, route_id, bikes_allowed):
        self.trip_id = trip_id
        self.route_id = route_id
        self.bikes_allowed = bikes_allowed
        
    def __repr__(self):
        return "Trip(" + repr(self.trip_id) + ", " + repr(self.route_id) + ", " + repr(self.bikes_allowed) + ")"


# In[363]:


class Stop:
    def __init__(self, stop_id, loc, wheelchair_boarding):
        self.stop_id = stop_id
        self.loc = loc
        self.loc_x = loc.x
        self.loc_y = loc.y
        self.wheelchair_boarding = wheelchair_boarding
        
    def __repr__(self):
        return "Stop(" + repr(self.stop_id) + ", " + repr(self.loc) + ", " + repr(self.wheelchair_boarding) + ")"


# In[364]:


class Node:
    def __init__(self, vals, level = None):
        self.vals = vals
        self.children = []
        self.left_child = None
        self.right_child = None
        self.level = level
        
        if self.level == None:
            self.level = 0
        else:
            self.level += 1
        
        if self.level < 6:
            if (self.level % 2) == 0:
                new_vals = sorted(vals, key = lambda s: s.loc_y)
            else:
                new_vals = sorted(vals, key = lambda s: s.loc_x)
                
            self.left_child = Node(new_vals[:len(new_vals)//2], self.level)
            self.right_child = Node(new_vals[len(new_vals)//2:], self.level)
            self.children.append(self.left_child)
            self.children.append(self.right_child)
            
    def __repr__(self):
        return ("Node level " + str(self.counter))


# In[366]:


# fri = BusDay(datetime(2020, 2, 21))
# rect = fri.get_stops_rect((0, 2), (0.5, 0.25))
# rect
# fri = BusDay(datetime(2020, 2, 22))
# rect = fri.get_stops_rect((-2, -2), (-1.75, -1.75))
# print(len(rect))


# In[367]:


# circ = fri.get_stops_circ((-1,1), 3)
# circ


# In[ ]:




