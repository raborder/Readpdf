"""
Program description
"""

"""
Imports
"""

from ast import Try
from pypdf import PdfReader
import re
from datetime import date, timedelta, datetime

"""
Create functions
"""

''' replaced by week_to_isodate
def week_to_date(current_year, week_num):
    # Combine year and week number into a string, specifying Monday (1) as the start day
    date_string = f'{current_year}-{week_num}-1'
    # Use strptime to parse the string into a datetime object
    date_object = datetime.strptime(date_string,"%Y-%W-%w")
    return date_object.date()
'''

def week_to_isodate(current_year, week_num, week_day):
    date_object = date.fromisocalendar(current_year, week_num, week_day)
    return date_object

"""
Main program
"""

'''
Initialise variables
'''

current_year = date.today().year
day_of_week = {'Mon':1,
               'Tue':2,
               'Wed':3,
               'Thu':4,
               'Fri':5,
               'Sat':6,
               'Sun':7}

'''
Start here
'''

# Create a PdfReader object by providing the path to your PDF file
reader = PdfReader('CELCAT_Timetable_CT423.pdf')

# Get the total number of pages
num_pages = len(reader.pages)
print(f"Total pages: {num_pages}")

# Extract text from a specific page (e.g., the first page, which is index 0)
page = reader.pages[0]
text = page.extract_text()
# print(text)

# To extract text from all pages, you can loop through them
all_text = ""
for page in reader.pages:
    all_text += page.extract_text() + "\n"
print(all_text)

lines = all_text.splitlines()

pattern = r'Mon|Tue|Wed|Thu|Fri|Sat|Sun|Rooms:|Classes:|Staff:|Activities:|Courses:|Notes:'

for i, line in enumerate(lines):        # Loop through all lines
    regex = re.compile(pattern)
    matched_line = regex.match(line)
    if not matched_line == None:
        match (matched_line.group()):
            case "Mon"|"Tue"|"Wed"|"Thu"|"Fri"|"Sat"|"Sun":
                print(matched_line.group())
                start_time = line[5:12]
                print(start_time)
                stop_time = line[13:]
                print(stop_time.strip())
                #######################################
                # Scheduling information
                #######################################
                i += 1
                line = lines[i]     # checking for case where day of week was on last line and therefore can't increment.  This may need to change as develop code
                if not "Wks" in line:           # Single week event
                    week_num = int(line[3:4].strip())
                    event_date = week_to_isodate(current_year, week_num, day_of_week[matched_line.group()])
                    print(event_date.strftime("%d/%m/%Y"))
                    i += 1
                    line = lines[i]
                    event_type = line       # next line must be event type (Orientation or Teaching)
                    recurring_event = False
                else:                       # Must be multiple week event (wks)
                    # get all lines up to event type so they can be analysed
                    while not (("Teaching" in line) or ("Orientation" in line)):
                        i += 1
                        line = line + lines[i] 
                    pattern = r'\d{1,2}-\d{1,2}'
                    matches = re.findall(pattern, line) # Output: ['1-2', '12-3', '1-34', '12-34']
                    for index, week_range in enumerate(matches):
                        print(f"Index: {index}, Value: {week_range}")
                        index = week_range.find('-')
                        start_week = week_range[:index]
                        stop_week = week_range[index+1:]
                        print("Start_week: ",start_week)
                        print("Stop_week: ",stop_week)
                        event_date = week_to_isodate(current_year, int(start_week), day_of_week)
                        num_of_weeks = int(stop_week) - int(start_week) + 1
                        print("Recurrences: ",num_of_weeks)
                        ################## store this information #############################
                    print(matches)
                    if "Teaching" in line:
                        event_type = "Teaching"
                    elif "Orientation" in line:
                        event_type = "Orientation"
                    else:
                        print("Something screwed up")
                    recurring_event = True
                print(event_type)
                #######################################
                # Event information
                #######################################
                i += 1                      # Advance to next line for processing
                line = lines[i]
            case "Availabilities":
                parameter_found = False     # Loop around until next parameter, building up Availabilities string. Line with 'Availabilities' cannot be next parameter
                parameter = line
                while parameter_found == False:
                    i += 1
                    line = lines[i]
                    parameter_pattern = r'Rooms:|Classes:|Staff:|Activities:|Courses:|Notes:'
                    regex = re.compile(parameter_pattern)   # look for day of week
                    match = regex.match(line)
                    if match != None:       # must have moved to next parameter
                        parameter_found = True
                    else:
                        parameter = parameter + line
                unit_pattern = r'VU\d{5}|BSB[A-Z]{3}\d{3}|ICT[A-Z]{3}\d{3}'   # search for unit using regex
                regex = re.compile(unit_pattern)   # look for unit
                availabilities = regex.search(line)
                print(availabilities)
            case "Rooms":
                room = line[7:14].strip()
                print(room)
                parameter_found = False     # Loop around until next parameter, building up Rooms string.
                parameter = line
                while parameter_found == False:                   # Check if multiple lines
                    i += 1
                    line = lines[i]
                    parameter_pattern = r'Availabilities:|Classes:|Staff:|Activities:|Courses:|Notes:'
                    regex = re.compile(parameter_pattern)
                    match = regex.match(line)
                    if match != None:       # must have moved to next parameter
                        parameter_found = True
                    else:
                        parameter = parameter + line
            case "Classes":                 # Should be OK, 1 line only
                group = line[0]
                print(group)
                i += 1
                line = lines[i]
            case "Staff":
                teacher = line
                print(teacher)              # Should be OK, 1 line only
                i += 1
                line = lines[i]
            case "Activities":              ################# Update to get all activities ##################
                parameter_found = False     # Loop around until next parameter, building up Activity string.
                parameter = line
                while parameter_found == False:                   # Check if multiple lines
                    i += 1
                    line = lines[i]
                    parameter_pattern = r'Availabilities:|Rooms:|Classes:|Staff:|Courses:|Notes:'
                    regex = re.compile(parameter_pattern)   # look for day of week
                    match = regex.match(line)
                    if match != None:       # must have moved to next parameter
                        parameter_found = True
                    else:
                        parameter = parameter + line
                unit_pattern = r'VU\d{5}|BSB[A-Z]{3}\d{3}|ICT[A-Z]{3}\d{3}'   # search for unit using regex
                regex = re.compile(unit_pattern)   # look for unit
                availabilities = regex.search(parameter)
                print(availabilities)
            case "Courses":
                course = line[9:14]
                print(course)
                i += 1
                line = lines[i]
            case "Notes":               # event information extraction complete when get to Notes. Notes information not extracted.
                gathering_info = False
                i += 1
                line = lines[i]
            case _:
                i += 1                      # Advance to next line for processing
                line = lines[i]

    '''
    if 'Rooms' in line:             # Unit not listed
        pass
    else:                           # Event must start with Availabilities
        availabilities = line
        while not ('Rooms' in line):
            i += 1 
            line = lines[i]
            availabilitiies = availabilities + line
            print(availabilities)
        room = "B10." + line[11:13].strip()
    '''
    #except Exception as e:
    #    print(f"something screwed up: {e}")
        




"""
for line in lines:
    regex = re.compile(pattern, re.MULTILINE)
    match = regex.match(line)
    print(match)
    day = match
    if match != None:
        start_time = line[5:12]
        print(start_time)
        stop_time = line[13:]
        print(stop_time)
    line = 
"""

'''
 if match != None:
        day = match.group()             # To extract the matched string, you use the .group() method
        print(match)
        match day:
            case 'Mon':
                day_of_week = 1
            case 'Tue':
                day_of_week = 2
            case 'Wed':
                day_of_week = 3
            case 'Thu':
                day_of_week = 4
            case 'Fri':
                day_of_week = 5
            case 'Sat':
                day_of_week = 6
            case _:
                day_of_week = 7
        

   
    gathering_info = True
    while gathering_info:
'''