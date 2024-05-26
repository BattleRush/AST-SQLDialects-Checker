# go trough all files in input_clean and check if the same file exists in inpu folder

import os

input_clean_files = []

for root, dirs, files in os.walk("input_clean"):
    #print file count per dir
    print(root, "has", len(files), "files")
    for file in files:
        input_clean_files.append(os.path.join(root, file).replace("input_clean/", ""))
        
input_files = []

for root, dirs, files in os.walk("input"):
    print(root, "has", len(files), "files")
    for file in files:
        input_files.append(os.path.join(root, file).replace("input/", ""))
        
any_error = False
for clean_file in input_clean_files:
    if clean_file not in input_files:
        print("File", clean_file, "is missing in input folder")
        any_error = True
    else:
        # if the file is present then check if the content is the same, if not then pull from input/ to input_clean/
        with open(f"input_clean/{clean_file}", "r", encoding="utf-8", errors='ignore') as f:
            content_clean = f.read()
            
        normal_file = clean_file.replace("input_clean/", "input/")
        with open(f"input/{normal_file}", "r", encoding="utf-8", errors='ignore') as f:
            content = f.read()
            
        if content_clean != content:
            print("File", clean_file, "is different in input folder")
            #any_error = True
            
            with open(f"input/{normal_file}", "r", encoding="utf-8", errors='ignore') as f:
                content = f.read()
            with open(f"input_clean/{clean_file}", "w", encoding="utf-8", errors='ignore') as f:
                f.write(content)
        
print("Done")
print("Files in input_clean:", len(input_clean_files))
print("Files in input:", len(input_files))

if any_error:
    print("There are missing files CORRECT THIS")
else:
    print("All files are present HURRAY")