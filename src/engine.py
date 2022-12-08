import pandas as pd
import names, os, yaml, random
from random import randint, choice

# loads the config file
with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Generates the fake staff including their names, employee numbers, regular days off and work days
def create_staff():
    staff_num = config['number_of_employees']
    emp_num_length = 6
    i = 0
    name_list = []
    while i < staff_num: 
        day_list = [0,1,2,3,4,5,6]

        # creates a dict to hold all of the employees information that will be turned into a pandas dataframe
        name_dict = {}
        name_dict['First_Name'] = names.get_first_name()
        name_dict['Last_Name'] = names.get_last_name()
        name_dict['Full_Name'] = name_dict['Last_Name'] + ', ' +name_dict['First_Name']
        name_dict['Empl_Num'] = ''.join(["{}".format(randint(0, 9)) for num in range(0, emp_num_length)])

        # randomly selects days off
        rdo = random.choice(day_list)
        if rdo+1 == 7:
            rdo2 = 0
        else:
            rdo2 = rdo+1
        day_list.remove(rdo)
        day_list.remove(rdo2)

        name_dict['Weekday'] = day_list

        # randomly decides if the employee works am or pm shift
        start = randint(1,2)
        if start == 1:
            name_dict['AMPM'] = 'AM'
        else:
            name_dict['AMPM'] = 'PM'
        name_list.append(name_dict)
        i += 1
        df = pd.DataFrame(name_list)
        df = df.explode('Weekday').reset_index(drop=True)
    return df

# Generates random cargo weight data depending on the aircraft type
def get_cargo(ac):
    if config['aircraft'][ac]['weight']['max'] == 0:
        weight = 0
    else:
        min = config['aircraft'][ac]['weight']['min']
        max = config['aircraft'][ac]['weight']['max']
        weight = randint(min, max)
    return weight

# Generates random bag count data depending on the aircraft type
def get_bags(ac):
    min_bag = config['aircraft'][ac]['bags']['min']
    max_bag = config['aircraft'][ac]['bags']['max']
    bags = randint(min_bag, max_bag)
    return bags

# Cleaning up the raw delay data
def merge_raw():
    # Loops through all of the raw data files and concats them together
    file_list = []
    for i in os.listdir('data/raw_stats'):
        if i == '.DS_Store':
            pass
        else:
            f = os.path.join('data/raw_stats/', i)
            file_list.append(f)
    df = pd.concat(map(pd.read_csv, file_list), ignore_index=True)
    df.dropna(subset=['Flight Number'], inplace=True)
    ac = pd.read_excel('data/aircraft-database.xlsx')
    ac.dropna(subset='AC_Type', inplace=True)

    # Merges the aircraft type data with delay data based on the tail number
    df = df.merge(ac, how='left', left_on='Tail Number', right_on='Tail_Num')

    # list of some of the known aircraft types for the selected airline
    ac_list = ['737','757','767','777','A319','A320','A321','A330','A350','EMB-175','ERJ 170','CL-600']
    for i in ac_list:
        df.loc[df['AC_Type'].str.contains(i, na=False), 'AC_Type'] = i
    df.loc[df['AC_Type'].str.contains('BD-500', na=False), 'AC_Type'] = 'A220'
    df.loc[df['AC_Type'].str.contains('BCS1', na=False), 'AC_Type'] = 'A220'
    df.loc[df['AC_Type'].str.contains('EMB-175', na=False), 'AC_Type'] = 'E175'
    df.loc[df['AC_Type'].str.contains('ERJ 170', na=False), 'AC_Type'] = 'E170'
    df.loc[df['AC_Type'].str.contains('A-321', na=False), 'AC_Type'] = 'A321'

    df = df.rename(columns={'Carrier Code':'Carrier','Date (MM/DD/YYYY)':'Flt_Date','Flight Number':'Flt_Num','Tail Number':'Tail_Num',
        'Destination Airport':'Dest','Scheduled departure time':'Schd_Dep_Time','Actual departure time':'Actl_Dep_Time',
        'Departure delay (Minutes)':'Delay_Minutes','Delay Carrier (Minutes)':'Delay_Carrier',
        'Delay Weather (Minutes)':'Delay_Weather','Delay Late Aircraft Arrival (Minutes)':'Delay_Late_Arrival',
        'Delay National Aviation System (Minutes)':'Delay_NAS','Delay Security (Minutes)':'Delay_Security'})

    df['Origin'] = config['origin_city']

    # gets the cargo weight data
    df['Crg_Weight'] = df['AC_Type'].apply(get_cargo)

    # gets the bag count data
    df['Bag_Count'] = df['AC_Type'].apply(get_bags)
    df['Flt_Date'] = pd.to_datetime(df['Flt_Date'])
    df['Month'] = df['Flt_Date'].dt.strftime('%m')
    df['Weekday'] = df['Flt_Date'].dt.weekday
    df['Hour'] = df['Actl_Dep_Time'].str.split(':').str[0].astype(int)
    df.loc[(df['Hour'] >= 3) & (df['Hour'] < 15), 'AMPM'] = 'AM'
    df.loc[(df['Hour'] >= 15) & (df['Hour'] <= 23), 'AMPM'] = 'PM'
    df.loc[(df['Hour'] >= 0) & (df['Hour'] < 3), 'AMPM'] = 'PM'
    df = df.loc[:,~df.columns.duplicated()].copy()
    df['Unique_Flt'] = df['Flt_Date'].dt.strftime('%Y-%m-%d-') + str(df['Flt_Num'].astype(int)).lstrip('0') + 'SEA' + df['Dest']
    return df

# splits the flight data into AM and PM groups
def flt_break_up(df):
    am = df.loc[df['AMPM'] == 'AM']
    pm = df.loc[df['AMPM'] == 'PM']
    am_list = dict(tuple(am.groupby('Weekday')))
    pm_list = dict(tuple(pm.groupby('Weekday')))
    return am_list, pm_list

# splits the employee data up into AM and PM groups
def staff_break_up(df):
    am = df.loc[df['AMPM'] == 'AM']
    pm = df.loc[df['AMPM'] == 'PM']
    am_list = dict(tuple(am.groupby('Weekday')))
    pm_list = dict(tuple(pm.groupby('Weekday')))
    return am_list, pm_list

# randomly assigns the employees to the flights during their work days and shift times
def assign_agent(flt, staff):
    flt_am, flt_pm = flt_break_up(flt)
    staff_am, staff_pm = staff_break_up(staff)
    for i in range(0,7):
        flt_am[i]['Empl_Num'] = flt_am[i].apply(lambda x: list(staff_am[i]['Empl_Num'].sample(n=1))[0], axis=1)
        flt_pm[i]['Empl_Num'] = flt_pm[i].apply(lambda x: list(staff_pm[i]['Empl_Num'].sample(n=1))[0], axis=1)
    df_am = pd.concat(flt_am)
    df_pm = pd.concat(flt_pm)
    df = pd.concat([df_am,df_pm])
    df = df.merge(staff, on=['Empl_Num','Weekday','AMPM'])
    return df

# creates random KPI data for employee performance
def create_kpi(df):
    df['Scan_Start_Min'] = df.apply(lambda x: randint(30,55), axis=1)
    df['Crg_Door_Close'] = df.apply(lambda x: randint(0,10), axis=1)
    df['Nmbr_Sent'] = df.apply(lambda x: randint(0,10), axis=1)
    df['Loaded_97'] = df.apply(lambda x: randint(7,20), axis=1)
    return df

# saves the data
def save_data(df):
    df.to_excel(config['save_location'], index=False)