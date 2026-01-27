from pypdf import PdfReader

# Create a PdfReader object by providing the path to your PDF file
reader = PdfReader('CELCAT_Timetable_IC32V.pdf')

# Get the total number of pages
num_pages = len(reader.pages)
print(f"Total pages: {num_pages}")

# Extract text from a specific page (e.g., the first page, which is index 0)
page = reader.pages[0]
text = page.extract_text()
print(text)

# To extract text from all pages, you can loop through them
all_text = ""
for page in reader.pages:
    all_text += page.extract_text() + "\n"
# print(all_text)

