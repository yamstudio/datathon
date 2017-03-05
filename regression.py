import numpy as np
from scipy import polyfit
import csv


def linear():
    x = []
    y = []
    with open('demographics_data/FINAL_CRIME_DATA.csv', 'r', encoding='mac_roman') as csvfile:
        for c in csv.reader(csvfile):
            try:
                # 'violent', 'murder', 'rape', 'robbery', 'assault', 'property', 'burglary', 'larceny', 'vehicle'
                v = np.array(c[-9:]).astype(np.float)
                if float(c[23]) < 100:
                    x.append(v)
                    y.append(float(c[23]) + float(c[24]))
            except KeyError:
                continue
            except ValueError:
                continue
    x = np.array(x)
    y = np.array(y)
    print(x)
    print(y)
    l = np.linalg.lstsq(x, y)
    print(l[0])
