import glob
import os

filename = "*.txt"
os.chdir("DelTest")
for file in glob.glob(filename):
    print(file)