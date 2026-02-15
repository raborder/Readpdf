"""
Program description
"""

"""
Imports
"""

from ast import Try
from logging import fatal
from os import times
from sched import Event
from pypdf import PdfReader
import re
from datetime import date, timedelta, datetime
import os.path
import json
import copy

"""
Class colours

IC32V   Yr1 Group 1 2 (Sage)
        Yr1 Group 2 10 (Basil)
	    Yr2 Group 1	7 Lavender
	    Yr2 Group 2	9 Blueberry
IC32G	Group 1     
	    Group 2	
	    Group 3	
CT423	Group 1	

"""

########################
# Function definitions
########################

''' replaced by week_to_isodate
def week_to_date(current_year, week_num):
    # Combine year and week number into a string, specifying Monday (1) as the start day
    date_string = f'{current_year}-{week_num}-1'
    # Use strptime to parse the string into a datetime object
    date_object = datetime.strptime(date_string,"%Y-%W-%w")
    return date_object.date()
'''

def week_to_isodate(current_year, week_num, week_day):                  # Takes 3 integer arguments
    date_object = date.fromisocalendar(current_year, week_num, week_day)
    return date_object

def find_between(s, first_char, last_char):
    try:
        # Find the index of the first character and add its length to get the start of the desired text
        start = s.index(first_char) + len(first_char)
        # Find the index of the second character, starting the search from 'start'
        end = s.index(last_char, start)
        # Use slicing to return the text between the indices
        return s[start:end]
    except ValueError:
        # Return an empty string or handle the error if the characters are not found
        print("Couldn't find class")
        return ""

def convert_to_24hr(time_12hr_string):
  """
  Converts a time string in 12-hour format to 24-hour format.

  Args:
    time_12hr_string: A string representing time in "HH:MM AM/PM" format.

  Returns:
    A string representing the time in "HH:MM" 24-hour format.
  """
  # Parse the 12-hour time string into a datetime object
  # %I for 12-hour hour, %M for minute, %p for AM/PM indicator
  in_time = datetime.strptime(time_12hr_string, "%I:%M%p")
  
  # Format the datetime object into a 24-hour time string
  # %H for 24-hour hour
  out_time = datetime.strftime(in_time, "%H:%M")
  
  return out_time

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

# Create list of event objects
event_list = [] # List of event objects
event_count = -1
events = {}

availabilities = ""
activities = ""

group = ""  #   Needed when Classes not in event

all_event_info_collected = False

'''
Start here
'''

#############################################
#  Read pdf
#############################################

selection = input("Which cohort would you like to view?\nEnter 1 for IC32V\n2 for IC32G\n3 for CS423\n4 for CT423\nOr just enter for default file\n: ")

match (selection):
    case "1":
        # Create a PdfReader object by providing the path to your PDF file
        reader = PdfReader('CELCAT_Timetable_IC32V.pdf')
    case "2":
        # Create a PdfReader object by providing the path to your PDF file
        reader = PdfReader('CELCAT_Timetable_IC32G.pdf')
    case "3":
        # Create a PdfReader object by providing the path to your PDF file
        reader = PdfReader('CELCAT_Timetable_CS423.pdf')
    case "4":
        # Create a PdfReader object by providing the path to your PDF file
        reader = PdfReader('CELCAT_Timetable_CT423.pdf')
    case _:
        # Create a PdfReader object by providing the path to your PDF file
        reader = PdfReader('CELCAT_Timetable.pdf')

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

#############################################
#  Extract event information
#############################################

event_pattern = r'Mon|Tue|Wed|Thu|Fri|Sat|Sun|Availabilities:|Rooms:|Classes:|Staff:|Activities:|Courses:|Notes:'

# i = len(lines)
i = 1

week_list = []

while i < (len(lines) - 1):        # Loop through all lines
    i += 1
    line = lines[i]
    regex = re.compile(event_pattern)
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
                    week_pattern = r'\d{1,2}-\d{1,2}'
                    matches = re.findall(week_pattern, line) # Output: ['1-2', '12-3', '1-34', '12-34']
                    week_list.clear()
                    for index, week_range in enumerate(matches):
                        print(f"Index: {index}, Value: {week_range}")
                        index = week_range.find('-')
                        start_week = week_range[:index]
                        stop_week = week_range[index+1:]
                        print("Start_week: ",start_week)
                        print("Stop_week: ",stop_week)
                        event_date = week_to_isodate(current_year, int(start_week), day_of_week[matched_line.group()])
                        num_of_weeks = int(stop_week) - int(start_week) + 1
                        print("Recurrences: ",num_of_weeks)
                        # week_list.append((start_week,num_of_weeks))     # Store info
                        week_list.append((event_date,num_of_weeks))     # Store info
                        print("week_list: ", week_list)
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
            case "Availabilities:":
                parameter_found = False     # Loop around until next parameter, building up Availabilities string. Line with 'Availabilities' cannot be next parameter
                parameter = line
                while parameter_found == False:
                    i += 1
                    parameter = parameter + lines[i]
                    parameter_pattern = r'Rooms:|Classes:|Staff:|Activities:|Courses:|Notes:'
                    regex = re.compile(parameter_pattern)
                    match = regex.search(parameter)
                    if match != None:       # must have moved to next parameter
                        parameter_found = True
                unit_pattern = r'VU\d{5}|BSB[A-Z]{3}\d{3}|ICT[A-Z]{3}\d{3}'   # search for unit using regex
                regex = re.compile(unit_pattern)   # look for unit
                if regex.search(parameter) == None:
                    availabilities = None
                    print("Availabilities: ", "None")
                else:
                    availabilities = regex.search(parameter).group()
                    print("Availabilities: ", availabilities)
                i -= 1          # Decrement as had to go extra line to find end of Availabilities
            case "Rooms:":
                room = line[7:14].strip()
                print("Room: ",room)
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
                i -= 1          # Decrement as had to go extra line to find end of Availabilities
            case "Classes:":                 # Should be OK, 1 line only
                group = find_between(line,"(",")")
                print("Class: ", group)
            case "Staff:":
                teacher = line
                print("Staff: ",teacher)              # Should be OK, 1 line only
            case "Activities:":
                parameter_found = False     # Loop around until next parameter, building up Activity string.
                parameter = line
                while parameter_found == False:                   # Check if multiple lines
                    i += 1
                    parameter = parameter + lines[i]
                    parameter_pattern = r'Availabilities:|Rooms:|Classes:|Staff:|Courses:|Notes:'
                    regex = re.compile(parameter_pattern)   # look for day of week
                    match = regex.search(parameter)
                    if match != None:       # must have moved to next parameter
                        parameter_found = True
                unit_pattern = r'VU\d{5}|BSB[A-Z]{3}\d{3}|ICT[A-Z]{3}\d{3}'   # search for unit using regex
                regex = re.compile(unit_pattern)   # look for unit
                if regex.search(parameter) == None:
                    activities = None
                    print("Activities: ", "None")
                else:
                    activities = regex.search(parameter).group()
                    print("Activities: ", activities)
                i -= 1          # Decrement as had to go extra line to find end of Activities
            case "Courses:":
                course = line[9:14]
                print("Course: ",course)
                all_event_info_collected = True
            case "Notes:":               # event information extraction complete when get to Notes. Notes information not extracted.
                pass
            case _:
                print("Something screwed up in the field matching statement")

#############################################
#  To do: Code to make json for each schedule
#############################################

    if all_event_info_collected == True:
        event_count += 1
        event_id = "event" + str(event_count)
        event_data = {(event_id):{"summary":"","location": "B10", "class_time":"", "description": "", "color_id": 0, "start": "", "recurrence": 0}}  # Create dictionary
        if group != "":
            event_data[(event_id)]["summary"] = course + " - " + group + ", " + availabilities # Could have used availabilities or activities but they seem to be always together and list the same unit.
        else:
            event_data[(event_id)]["summary"] = course
        event_data[(event_id)]["location"] = room
        event_data[(event_id)]["class_time"] = convert_to_24hr(start_time) + " to " + convert_to_24hr(stop_time)
        if (availabilities == None) and (activities == None):
            event_data[(event_id)]["description"] = event_type
        else:
            event_data[(event_id)]["description"] = availabilities
        """
        Class colours

        IC32V   Yr1 Group 1 2 (Sage)
                Yr1 Group 2 10 (Basil)
	            Yr2 Group 1	7 Lavender
	            Yr2 Group 2	9 Blueberry
        IC32G	Group 1     5 Banana
	            Group 2 & 3	4 Flamingo
	            Group 4     6 Tangerine
        CT423	New         1 Peacock
                Continuing  3 Grape

        """
        color = 0   # Default
        match course:
            case "IC32V":
                match group:
                    case "Class 1": ############ Need to do Y1, Y2
                        color = 2
                    case "Class 2":
                        color = 10
            case "IC32G":
                match group:
                    case "Class 1":
                        color = 5
                    case "Class 2":
                        color = 4
            case "CS423":
                match group:
                    case "Class 1":
                        color = 1
                    case "Class 2":
                        color = 3
            case "CT423":       ########## Need to update groups and colours
                match group:
                    case "Class 1":
                        color = 5
                    case "Class 2":
                        color = 4
        event_data[(event_id)]["color_id"] = color

        ################
        # Do dates
        ################
        if recurring_event == False:
            event_data[(event_id)]["start"] = event_date
            event_data[(event_id)]["recurrence"] = 0
            print(event_data)
            events.update(event_data)   # add to events 
            # pprint.pprint(events, indent=4)
            print(json.dumps(events, indent=4))
        else:
            for j in range(len(week_list)):
            #for week_info in week_list:  Don't know why this doesn't work! Keeps looping!
            #    event_data[(event_id)]["start"] = week_info[0].strftime("%d/%m/%Y")
            #    event_data[(event_id)]["recurrence"] = week_info[1]
                event_data[(event_id)]["start"] = week_list[j][0].strftime("%d/%m/%Y")
                event_data[(event_id)]["recurrence"] = week_list[j][1]
                print("event_data: ", event_data)
                events.update(event_data)   # add to events 
                #pprint.pprint(events, indent=4) Don't know why this doesn't work - stopped at 9 events
                print(json.dumps(events, indent=4))
                new_event = copy.deepcopy(event_data[(event_id)])   # Reaslly iomportant to do a DEEP copy or all referred varaibles are updated.
                event_count += 1
                event_id = "event" + str(event_count)               # Shallow copy, but ok here.
                event_data[(event_id)] = new_event
                del event_data["event" + str(event_count - 1)]

            event_count -= 1
                
                #print("event_data: ", event_data)
                #events.update(event_data)   # append to events 
                #print("events: ", events)

        # Clear event information
        event_type = ""
        start_time = ""
        stop_time = ""
        availabilities = None
        room = ""
        teacher = ""
        activities = None
        course = ""
        group = ""
        
    all_event_info_collected = False
    

#############################################
#  Write json to file
#############################################

# Get the home directory path and join with the file name
file_name = 'output.json'
home_dir = os.path.expanduser("~")
home_dir = os.path.join(home_dir, "Documents")
complete_path = os.path.join(home_dir, file_name)
print("complete path: " + complete_path)

complete_path = os.path.join(home_dir, file_name)

with open(complete_path, 'w') as file:
# Dump the Python data to the file in JSON format
    json.dump(events, file, indent=4) # Using indent makes the file human-readable


    #except Exception as e:
    #    print(f"something screwed up: {e}")
        