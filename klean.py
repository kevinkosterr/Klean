import glob
import os


os.chdir("DelTest")
for file in glob.glob("*.txt"):
    print(file)