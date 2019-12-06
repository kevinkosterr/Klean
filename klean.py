import glob, os
os.chdir("/mydir")
for file in glob.glob("*.txt"):
    print(file)