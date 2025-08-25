from datetime import datetime

def getDatetimeFromStr(date:str, time:str):
    '''returns datetime obj

    asserts that formats of input are
        - date: YYYY-MM-DD
        - time: hh:mm:ss

    '''
    date_str = date.split('-')
    date_int = list(map(int,date_str))
    time_str = time.split(':')
    time_int = list(map(int,time_str))
    return datetime(*date_int,*time_int)

def stripDatetime(datetime_str:str):
    '''returns datetime representation of input.
    asserts the format of datetime_str to be: YYYY-MM-DDThh:mm:ss.[XXX]
    '''
    index_endOfDate = datetime_str.index('T')
    index_endOfTime = datetime_str.index('.')
    return getDatetimeFromStr(datetime_str[:index_endOfDate],datetime_str[index_endOfDate+1:index_endOfTime])

def getData(data:dict):
    """returns: a tuple (departures, ref_time)
        - departures is a dictionary, keys are platform_numbers, entries are a list of the next departures on that platform
        - ref_time: datetime obj, servertime in data
    """
    departures:dict[int,list] = {}
    monitor_keys = range(len(data['data']['monitors']))

    for monitor_key in monitor_keys:
        line_data_array = data['data']['monitors'][monitor_key]['lines']
        for line_data in line_data_array:
            dep_data_array = line_data['departures']['departure']
            default_platform_nr = line_data['platform']
            default_towards_raw = line_data['towards']
            line = line_data['name']
            
            for dep_data in dep_data_array:
                if not 'departureTime' in dep_data.keys():
                    print("departureTime not found in data", dep_data)
                    continue
                platform_nr = default_platform_nr
                towards_raw = default_towards_raw
                folding_ramp = False
                if 'vehicle' in dep_data.keys(): 
                    platform_nr = dep_data['vehicle']['platform']
                    towards_raw:str = dep_data['vehicle']['towards']
                    line = dep_data['vehicle']['name']
                    if 'foldingRamp' in dep_data['vehicle']:
                        folding_ramp = dep_data['vehicle']['foldingRamp']
                
                dep_time_str:str = dep_data['departureTime']['timeReal'] if 'timeReal' in dep_data['departureTime'] else dep_data['departureTime']['timePlanned']
                index_endOfDate = dep_time_str.index('T')
                index_endOfTime = dep_time_str.index('.')
                dep_time = getDatetimeFromStr(dep_time_str[:index_endOfDate],dep_time_str[index_endOfDate+1:index_endOfTime])
                towards = towards_raw.upper().strip()

                #append to departures
                toAppend = {"towards":towards,"time":dep_time,"foldingRamp":folding_ramp,"line":line}
                if platform_nr not in departures:
                    departures[platform_nr] = [toAppend]
                    continue
                departures[platform_nr].append(toAppend)
    #assertion that format of reftime_str is YYYY-MM-DDThh:mm:ss.xxx
    reftime_str:str = data['message']['serverTime']
    index_endOfDate = reftime_str.index('T')
    index_endOfTime = reftime_str.index('.')
    reftime = getDatetimeFromStr(reftime_str[:index_endOfDate],reftime_str[index_endOfDate+1:index_endOfTime])
    return departures, reftime
    