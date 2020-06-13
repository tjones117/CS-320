# project: p4
# submitter: tjones25
# partner: none

import click
from zipfile import ZipFile
from io import TextIOWrapper
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED
import csv
import socket, struct
from operator import itemgetter
import re
from collections import defaultdict
import geopandas
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.core.display import HTML

@click.command()
@click.argument('zip1')
@click.argument('zip2')
@click.argument('mod', type=click.INT)
def sample(zip1, zip2, mod):        
    with ZipFile(zip2, "w") as zf:
        new = zip2[:-3]
        new = new + "csv"
        with zf.open(new, "w") as raw:
            with TextIOWrapper(raw) as f:
                writer = csv.writer(f)
                
                reader = zip_csv_iter(zip1)
                header = next(reader)
                writer.writerow(header)
                ip_idx = header.index("ip")
                counter = 0
                for row in reader:
                    if counter % mod == 0:
                        writer.writerow(row)
                    counter += 1

#Taken from https://stackoverflow.com/questions/9590965/convert-an-ip-string-to-a-number-and-vice-versa
def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]

@click.command()
@click.argument('zip1')
@click.argument('zip2')
def sort(zip1, zip2):
    with ZipFile(zip2, "w") as zf:
        new = zip2[:-3]
        new = new + "csv"
        with zf.open(new, "w") as raw:
            with TextIOWrapper(raw) as f:
                writer = csv.writer(f)
                
                reader = zip_csv_iter(zip1)
                header = next(reader)
                writer.writerow(header)
                ip_idx = header.index("ip")
                rows = list(reader)
                for item in rows:
                    new = re.sub(r"[a-zA-Z]+$", "000", item[0])
                    item[14] = ip2long(new)
                rows = sorted(rows, key=itemgetter(14))
                for item in rows:
                    item.pop(-1)
                    writer.writerow(item)
                    
@click.command()
@click.argument('zip1')
@click.argument('zip2')
def country(zip1, zip2):
     with ZipFile(zip2, "w") as zf:
        new = zip2[:-3]
        new = new + "csv"
        with zf.open(new, "w") as raw:
            with TextIOWrapper(raw) as f:
                writer = csv.writer(f)
                
                reader = zip_csv_iter(zip1)
                header = next(reader)
                header.append('country')
                writer.writerow(header)
                rows = list(reader)
                
                IP2 = zip_csv_iterIP2("IP2LOCATION-LITE-DB1.CSV.ZIP")
                IP2rows = list(IP2)

                index = 0
                for item in rows:
                    new = re.sub(r"[a-zA-Z]+$", "000", item[0])
                    ip = ip2long(new)
                    if ip <= int(IP2rows[index][1]):
                        item.append(IP2rows[index][3])
                        writer.writerow(item)
                    else:
                        index += 1
                        while ip < int(IP2rows[index][0]):
                            index += 1
                        item.append(IP2rows[index][3])
                        writer.writerow(item)
                        
def world():
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world.set_index("name", drop=False, inplace=True)
    return world[world["continent"] != "Antarctica"]

@click.command()
@click.argument('zipname')
@click.argument('imgname')
def geo(zipname, imgname):
    # count occurences per country
    reader = zip_csv_iter(zipname)
    header = next(reader)
    cidx = header.index("country")
    counts = defaultdict(int)
    for row in reader:
        counts[row[cidx]] += 1

    # add color column that defaults gray, but set
    # to shade of red for higher request counts
    w = world()
    w["color"] = "0.7"

    for country, count in counts.items():
        # sometimes country names in IP dataset don't
        # match names in naturalearth_lowres -- skip those
        if not country in w.index:
            continue

        color = "lightsalmon" # >= 1
        if count >= 10:
            color = "orange"
        if count >= 50:
            color = "tomato"
        if count >= 100:
            color = "red"
        if count >= 1000:
            color = "brown"
        w.at[country, "color"] = color

    ax = w.plot(color=w["color"], legend=True, figsize=(16, 4))
    ax.figure.savefig(imgname, bbox_inches="tight")
    
@click.command()
@click.argument('zipname')
@click.argument('imgname')
@click.argument('hour')
def geohour(zipname, imgname, hour):
     # count occurences per country
    reader = zip_csv_iter(zipname)
    header = next(reader)
    cidx = header.index("country")
    counts = defaultdict(int)
    rows = list(reader)
    for row in rows:
        iptime = int(re.findall(r"^[0-9]+", row[2])[0])
        if iptime == int(hour):
            counts[row[cidx]] += 1

    # add color column that defaults gray, but set
    # to shade of red for higher request counts
    w = world()
    w["color"] = "0.7"

    for country, count in counts.items():
        # sometimes country names in IP dataset don't
        # match names in naturalearth_lowres -- skip those
        if not country in w.index:
            continue

        color = "lightsalmon" # >= 1
        if count >= 20:
            color = "orange"
        if count >= 40:
            color = "tomato"
        if count >= 60:
            color = "red"
        if count >= 80:
            color = "brown"
#         if count >= 100:
#             color = "black"
        w.at[country, "color"] = color

    ax = w.plot(color=w["color"], legend=True, figsize=(16, 4))
    ax.figure.savefig(imgname, bbox_inches="tight")

@click.command()
@click.argument('zipname')
@click.argument('htmlname')
def video(zipname, htmlname):
    reader = zip_csv_iter(zipname)
    header = next(reader)
    cidx = header.index("country")
    rows = list(reader)
    
    w = world()
    fig, ax = plt.subplots(figsize=(10,10))
            
    def draw_frame(frame_num):
        ax.cla()
        counts = defaultdict(int)
        for row in rows:
            iptime = int(re.findall(r"^[0-9]+", row[2])[0])
            if iptime == int(frame_num):
                counts[row[cidx]] += 1

        # add color column that defaults gray, but set
        # to shade of red for higher request counts
        
        w["color"] = "0.7"

        for country, count in counts.items():
            # sometimes country names in IP dataset don't
            # match names in naturalearth_lowres -- skip those
            if not country in w.index:
                continue

            color = "lightsalmon" # >= 1
            if count >= 20:
                color = "orange"
            if count >= 40:
                color = "tomato"
            if count >= 60:
                color = "red"
            if count >= 80:
                color = "brown"
    #         if count >= 100:
    #             color = "black"
            w.at[country, "color"] = color

        w.plot(ax=ax, color=w["color"], legend=True, figsize=(16, 4))
    
    anim = FuncAnimation(fig, draw_frame, frames=23, interval=250)
    html = anim.to_html5_video()
    
    with open(htmlname, "w") as f:
        f.write(html)

@click.group()
def commands():
    pass

def zip_csv_iter(name):
    with ZipFile(name) as zf:
        with zf.open(name.replace(".zip", ".csv")) as f:
            reader = csv.reader(TextIOWrapper(f))
            for row in reader:
                yield row
                
def zip_csv_iterIP2(name):
    with ZipFile(name) as zf:
        with zf.open(name[:-4]) as f:
            reader = csv.reader(TextIOWrapper(f))
            for row in reader:
                yield row

commands.add_command(sample)
commands.add_command(sort)
commands.add_command(country)
commands.add_command(geo)
commands.add_command(geohour)
commands.add_command(video)

if __name__ == "__main__":
    commands()