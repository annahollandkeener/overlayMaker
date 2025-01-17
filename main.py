from imports import *
from modules import merge_vector

print("HI")

#Checking for assisted mode
while True:
    assisted = input("Would you like to run assisted mode? (Y/N): ")

    if (assisted == "Y" or assisted == "N"):
        break

    print("\nEnter 'Y' or 'N'.\n")

rangeStats.printer()
    
