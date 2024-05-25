# go trough all files in input_clean and check if the same file exists in inpu folder

import os

input_clean_files = []

for root, dirs, files in os.walk("input_clean"):
    #print file count per dir
    print(root, "has", len(files), "files")
    for file in files:
        input_clean_files.append(file)
        
input_files = []

for root, dirs, files in os.walk("input"):
    print(root, "has", len(files), "files")
    for file in files:
        input_files.append(file)
any_error = False
for file in input_clean_files:
    if file not in input_files:
        print("File", file, "is missing in input folder")
        any_error = True
        
print("Done")
print("Files in input_clean:", len(input_clean_files))
print("Files in input:", len(input_files))

if any_error:
    print("There are missing files CORRECT THIS")
else:
    print("All files are present HURRAY")