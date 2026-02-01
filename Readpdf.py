from ast import Try
from pypdf import PdfReader
import re

# Create a PdfReader object by providing the path to your PDF file
reader = PdfReader('CELCAT_Timetable_IC32G.pdf')

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

pattern = r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b'

lines = all_text.splitlines()

for i, line in enumerate(lines):       # skip preliminary lines at start
    regex = re.compile(pattern, re.MULTILINE)   # look for day of week
    match = regex.match(line)
    if match != None:
        day = match
        print(match)
        start_time = line[5:12]
        print(start_time)
        stop_time = line[13:]
        print(stop_time.strip())
        i += 1
        try:
            line = lines[i]     # checking for case where day of week was on last line and therefore can't increment.  This may need to change as develop code
            if "Wks" in line:           # Multiple week event
                pass
            else:                       # Must be single week event
                date = line[-10:]
                print(date)
                i += 1
                line = lines[i]
                summary = line
                print(summary)
            i += 1
            line = lines[i]
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
        except:
            print("something screwed up")

        




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