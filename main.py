# This is a Python script to convert OpenTX telemetry logs and prepare them to
# be used as overlays for Dashware.
# Author Michael - Michael (at) believeinrealty.com
# Version 0.1

import os
import csv
import math



def haversine(lat1, lon1, lat2, lon2):
    r = 6372800  # Earth radius in meters

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))



filenames = os.listdir()  # Read oll files in the directory to find the CSV file

b = 0
for i in filenames:
    if filenames[b][-3:] == "csv":      # Check for  if last 3 digits of each
                                        # list items with filenames machtes
                                        #  csv
        currentfile = filenames[b]
        print("CSV file found, try to import " + currentfile)

        with open(currentfile) as csv_file:
            csv_reader = list(csv.reader(csv_file, delimiter=','))   # import csv file and create list of csv lines
            numcolumn = len(csv_reader[0])                          # determine columns in csv file
            line_count = 0
            for row in csv_reader:                  # Split up GPS coordinates for each
                if line_count == 0:                 # Prepare header row
                    csv_reader[line_count].insert(2, "Time of video (s)")       # Insert Time of video
                    csv_reader[line_count].insert(4, "GPS Latitude")        # Insert GPS Latitude
                    csv_reader[line_count].insert(5, "GPS Longitude")       # Insert GPS Longitude
                    csv_reader[line_count].insert(6, "GPS dist home (m)")   # Insert GPS dist home
                    csv_reader[line_count].insert(7, "GPS dist trav (m)")  # Insert GPS distance traveled home
                    csv_reader[line_count].insert(26, "Motor Watts (VA)")  # Insert Motor Watts
                    csv_reader[line_count][32] = "Throttle %"               # Throttle in %

                if line_count == 1:
                    csv_reader[line_count].insert(2, float(0.0))  # Time calculation
                    csv_reader[line_count].insert(4, csv_reader[line_count][3][:10])   # GPS latitude separation
                    csv_reader[line_count].insert(5, csv_reader[line_count][3][-10:])  # GPS latitude separation
                    csv_reader[line_count].insert(6, "0.0")                            # Initial Home distance set to 0
                    csv_reader[line_count].insert(7, "0.0")                       # Initial travel distance set to 0
                    csv_reader[line_count].insert(26,
                                                  round(float(csv_reader[line_count][24]) *
                                                        float(csv_reader[line_count][25]), 2))  # Calculate Motor Watts
                    csv_reader[line_count][32] = round(float(float(csv_reader[line_count][32])
                                                             + 1024.0)/20.48, 2)  # convert throttle to %

                if line_count >= 2:
                    csv_reader[line_count].insert(2, (round(float(0.1)+csv_reader[line_count-1][2], 2)))  # Time calc.
                    csv_reader[line_count].insert(4, csv_reader[line_count][3][:10])  # GPS latitude separation
                    csv_reader[line_count].insert(5, csv_reader[line_count][3][-10:])  # GPS latitude separation
                    csv_reader[line_count].insert(6, (haversine(float(csv_reader[1][4]),
                                                                float(csv_reader[1][5]),
                                                                float(csv_reader[line_count-1][4]),
                                                                float(csv_reader[line_count-1][5])))
                                                  )  # Using the GPS coordinate form line 2 as the home point
                    csv_reader[line_count].insert(7, (float(haversine(float(csv_reader[line_count][4]),
                                                                      float(csv_reader[line_count][5]),
                                                                float(csv_reader[line_count - 1][4]),
                                                                float(csv_reader[line_count - 1][5])))) +
                                                  float(csv_reader[line_count-1][7])
                                                  )  # Using the GPS coordinate to caclculate distance traveled
                    csv_reader[line_count].insert(26, round(
                        float(csv_reader[line_count][24]) *
                        float(csv_reader[line_count][25]), 2))  # Calculate Motor Watts
                    csv_reader[line_count][32] = round(float(
                        float(csv_reader[line_count][32]) + 1024.0) / 20.48,2)  # convert Throttle to %
                line_count += 1

        line_count = 0
        with open('{0}_converted.csv'.format(currentfile[:-4]), mode='w') as output_file:       # add _converted to output filename
                output_file = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for row in csv_reader:
                    output_file.writerow(csv_reader[line_count])
                    line_count += 1
        print("Converting successful")
    b += 1   # check next file




