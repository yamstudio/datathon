import csv
import re
import pickle
#from simpledbf import Dbf5


fips = [{} for _ in range(57)]
cities = {}
state_names_to_codes = {}
state_codes_to_fips = {}
state_fips_to_codes = {}
final = {}
census_data = {}


def gen_fips():
    with open('demographics_data/states.csv', 'r', encoding='mac_roman') as csvfile:
        for x in csv.reader(csvfile):
            state_names_to_codes[x[0]] = x[1]
    with open('demographics_data/fips_codes.csv', 'r', encoding='mac_roman') as csvfile:
        raw_fips = [[int(x[1]), x[2].zfill(3), x[5].lower(), x[0]] for x in csv.reader(csvfile) if x[6].lower() in ['county', 'borough', 'parish', 'city']]
        for j in raw_fips:
            state_codes_to_fips[j[3]] = j[0]
            state_fips_to_codes[j[0]] = j[3]
            fips[j[0]][j[2]] = str(j[0]) + j[1]


def parse2000(x):
    try:
        code = state_codes_to_fips[state_names_to_codes[x[1]]]
        return [state_names_to_codes[x[1]], x[2].lower(), fips[code][x[2].lower()], x[8], x[7], sum([0 if j == '.' else int(j) for j in x[9: 24]]), '2000']
    except KeyError:
        if x[1] == 'STATE':
            return ['STATE', 'COUNTY', 'FIPS', 'DEM', 'GOP', 'OTH', 'YEAR']
        return None


def data2000():
    # http://www.american.edu/spa/ccps/Data-Sets.cfm
    with open('demographics_data/county_2000.csv', 'r', encoding='mac_roman') as csvfile:
        data = list(map(parse2000, csv.reader(csvfile)))
        with open('demographics_data/out_2000.csv', 'w', encoding='utf-8', newline='') as outfile:
            csvwriter = csv.writer(outfile)
            for x in data:
                if x:
                    csvwriter.writerow(x)


def parse2004(x):
    try:
        county = re.sub(r'\d', '', x[5]).lower().replace(' county', '').replace(' parish', '').replace('state house district , ', '')
        if x[4] == 'AK':
            county = county.split('-')[0]
        return [x[4], county, fips[state_codes_to_fips[x[4]]][county], x[8], x[9], x[10], '2004']
    except KeyError:
        if x[4] == 'STATE':
            return ['STATE', 'COUNTY', 'FIPS', 'DEM', 'GOP', 'OTH', 'YEAR']
        return None


def data2004():
    # https://catalog.data.gov/dataset/2004-presidential-general-election-county-results-direct-download
    # Dbf5('demographics_data/county_2004.dbf').to_csv('demographics_data/county_2004.csv')
    with open('demographics_data/county_2004.csv', 'r') as csvfile:
        data = list(map(parse2004, csv.reader(csvfile)))
        with open('demographics_data/out_2004.csv', 'w', encoding='utf-8', newline='') as outfile:
            csvwriter = csv.writer(outfile)
            for x in data:
                if x:
                    csvwriter.writerow(x)


def parse20082016(x):
    try:
        x[1] = x[1].replace(' County', '').lower()
        x[0] = state_fips_to_codes[int(x[2][:-3])]
    except KeyError:
        x
    except ValueError:
        x
    return x


def data20082016():
    with open('demographics_data/county_2008_2016.csv', 'r', encoding='mac_roman') as csvfile:
        data = list(csv.reader(csvfile))
        with open('demographics_data/out_2008.csv', 'w', encoding='utf-8', newline='') as outfile:
            csvwriter = csv.writer(outfile)
            for x in data:
                csvwriter.writerow(parse20082016([x[i] for i in [1, 1, 0, 3, 4, 5]]) + [2008])
        with open('demographics_data/out_2012.csv', 'w', encoding='utf-8', newline='') as outfile:
            csvwriter = csv.writer(outfile)
            for x in data:
                csvwriter.writerow(parse20082016([x[i] for i in [1, 1, 0, 7, 8, 9]]) + [2012])
        with open('demographics_data/out_2016.csv', 'w', encoding='utf-8', newline='') as outfile:
            csvwriter = csv.writer(outfile)
            for x in data:
                csvwriter.writerow(parse20082016([x[i] for i in [1, 1, 0, 11, 12, 13]]) + [2016])


def query(qfips):
    fp = str(qfips)
    for c in map(str, [2000, 2004, 2008, 2012, 2016]):
        with open('demographics_data/out_' + c + '.csv', encoding='utf-8') as csvfile:
            print('Year ' + c + ':')
            for x in csv.reader(csvfile):
                if x[2] == fp:
                    print(x)
                    continue
            print('Not found')


def gen_cities():
    gen_fips()
    for v in state_names_to_codes.values():
        cities[v] = {}
    with open('demographics_data/fips_codes.csv', 'r', encoding='mac_roman') as csvfile:
        for x in csv.reader(csvfile):
            if x[6].lower() in ['city', 'town', 'township']:
                try:
                    cities[x[0]][x[5]] = final[int(x[1] + x[2])]
                except KeyError:
                    print(int(x[1] + x[2]))
    cities['NY']['New York City'] = cities['NY']['New York']
    for k, v in state_names_to_codes.items():
        cities[k] = cities[v]


def dump():
    for c in map(str, [2000, 2004, 2008, 2012, 2016]):
        with open('demographics_data/out_' + c + '.csv', encoding='utf-8') as csvfile:
            for x in csv.reader(csvfile):
                try:
                    final[int(x[2])].append(x)
                except KeyError:
                    final[int(x[2])] = [x]
                except ValueError:
                    continue
    gen_cities()
    print(cities['CA']['San Francisco'])
    with open('cities', 'wb') as f:
        pickle.dump(cities, f)


def census():
    gen_fips()
    for v in state_names_to_codes.values():
        census_data[v] = {}
    with open('demographics_data/POP01A-Table 1.csv', 'r', encoding='mac_roman') as csvfile:
        data = [x[0].split(', ') + [x[31], x[35]] for x in csv.reader(csvfile) if x[0][-4] == ',']
    for x in data:
        census_data[x[1]][x[0]] = x
    with open('demographics_data/PopulationEstimates.csv', 'r', encoding='mac_roman') as csvfile:
        for x in csv.reader(csvfile):
            if not x[3]:
                continue
            try:
                county = x[2].replace(' County', '').replace(' Census Area', '').replace(' Parish', '')
                census_data[x[1]][county].append(x[15].replace(',', ''))
            except KeyError:
                continue
    print(census_data['NY']['New York'])
    with open('census_data', 'wb') as f:
        pickle.dump(census_data, f)
