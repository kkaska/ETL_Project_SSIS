import glob
import os
import requests

def remove_headers():
    # removes all lines beginning with #
    for file in glob.glob('W3SVC1/*.log'):
        with open(file, 'r+') as f:
            text = f.readlines()
            list = []
            list.append(text[3])
            for x in text:
                if (x[0] != "#"):
                    list.append(x)
        f = open(file, "w+")
        for item in list:
            f.write(item)

    f.close()

def sort_files():
    #identify different types of files
    for file in glob.glob('W3SVC1/*.log'):
        with open(file, 'r+') as f:
            text = f.readlines()
        if len(text[3].split(' ')) == 14:
            os.rename(file, file.replace('u', '1'))
        else:
            os.rename(file, file.replace('u', '2'))
    f.close()

def ip_2_geo():
    ip_geo = []

    for file in glob.glob('W3SVC1/*.log'):
        with open(file, 'r+') as f:
            text = f.readlines()

        for i in range(1, len(text)):
            try:
                ip = text[i].split(' ')[8]
            except (IndexError, KeyError, TypeError):
                ip = "NA"

            ip_position = []  # diff name
            for j in range(len(ip_geo)):
                if ip == ip_geo[j][0]:
                    ip_position = j
            if ip_position != []:
                add_ip = [ip, ' ', ip_geo[ip_position][2], ' ', ip_geo[ip_position][4], ' ',
                                    ip_geo[ip_position][6], ' ', ip_geo[ip_position][8]]
            else:
                try:
                    translate = requests.get(
                        "http://api.ipstack.com/" + ip + "?access_key=80e1205ad999f3ea260de0846b9ea90c&format=1")
                    ip_geo.append([ip, ',', translate.json()["country_name"], ',', translate.json()["region_name"], ',', translate.json()["city"], ',',translate.json()["zip"]])
                    add_ip = [ip, ',', translate.json()["country_name"], ',', translate.json()["region_name"], ',', translate.json()["city"], ',', translate.json()["zip"]]
                except (IndexError, KeyError, TypeError):
                    ip_geo.append([ip])
                    add_ip = [ip]

                print(ip_geo[-1])
                if (add_ip) is not None:
                    f2 = open("geolocation.txt", "a", encoding="utf-8")
                    f2.write(" ".join(map(str, ip_geo[-1])))
                    f2.write("\n")
    f.close()

def fix_column_number():
    # Iteratively open through all log files in the folder
    for file in glob.glob('W3SVC1/*.log'):
        with open(file, 'r+') as f:
            log = f.readlines()

            #create two files to contain the lines from the log files and the files that encountered errors
            combined_logs = open("combinedlogs.log", "a", encoding="utf-8")
            error_logs = open("errors.log", "a", encoding="utf-8")

            # check type 1 files that have 12 columns
            # if they have the normal amount of splits, add the missing columns at the appropriate split
            # if they do not have the normal amount of splits, send to the errors file to be dealt with later
            if "1_" in file:
                for i in range(len(log)):
                    if len(log[i].split(' ')) == 14:
                        line = log[i].split(' ')[0:10]
                        line.extend(["cs(Cookie)", "cs(Referer)"])
                        line.extend(log[i].split(' ')[10:13])
                        line.extend(["sc-bytes", "cs-bytes"])
                        line.append(log[i].split(' ')[13])
                        combined_logs.write(" ".join(map(str, line)))
                    else:
                        error_logs.write(file + '\n')
                        line = log[i].split(' ')
                        error_logs.write(' '.join(map(str, line)))

            # check type 2 files that have 15 columns
            # if they have the right amount of splits, send them to the combined logs file.
            # if they have the wrong amount of splits, send them to the errors log file to be dealth with later.
            elif "2_" in file:
                for i in range(1, len(log)):
                    if len(log[i].split(' ')) == 18:
                        line = log[i].split(' ')
                        combined_logs.write(' '.join(map(str, line)))
                    else:
                        error_logs.write(file + '\n')
                        line = log[i].split(' ')
                        error_logs.write(' '.join(map(str, line)))
    combined_logs.close()
    error_logs.close()
    f.close()

    # fix errors
    for file in glob.glob('errors.log'):
        with open(file, 'r+') as f:
            log = f.readlines()
            combined_logs = open("combinedlogs.log", "a", encoding="utf-8")
            unsolved_errors = open("unsolvederrors.log", "a", encoding="utf-8")
            for i in range(len(log)):
                if "W3SVC1" not in log[i]:
                    if len(log[i].split(' ')) == 18:
                        error = log[i].split(' ')
                        combined_logs.write(" ".join(map(str, error)))
                    else:
                        unsolved_errors.write(" ".join(map(str,log[i].split(' '))))
    unsolved_errors.close()
    combined_logs.close()
    f.close()

def robots():
    robo_list = []
    unique_robo = []
    robots = open("robots.txt", "a", encoding="utf-8")

    with open('combinedlogs.log', 'r+') as logs:
        log = logs.readlines()

        for i in range(1, len(log)):
            try:
                ip = log[i].split(' ')[8]
            except (IndexError, KeyError, TypeError):
                ip = "NA"

            if ("robots.txt" in log[i]):
                robo_list.append(ip)

            for item in robo_list:
                if item not in unique_robo:
                    unique_robo.append(item)

            if ip in unique_robo:
                robots.write("".join("robot") + "\n")
                print(i)
                print('robot')
            else:
                robots.write("".join("human") + "\n")
                print(i)
                print('human')

    robots.close()
    logs.close()

def append_robots():
    logs = ""
    robots = ""
    combined = []

    with open('combinedlogs.log', 'r+', encoding="utf-8") as input, open('robots.txt', 'r+', encoding="utf-8") as robot_text:
        logs = input.readlines()
        logs = logs[:-1]
        robots = robot_text.readlines()
        for i in range(1, len(logs)):
            combined.append(logs[i].rstrip() + ' ' + robots[i].rstrip() + '\n')
    input.close()
    robot_text.close()

    # replace file contents with the new appended lines
    with open("combinedlogs.log", "w") as output:
        output.write(''.join(map(str, combined)))
    output.close()

def append_geolocation():
    logs = ""
    geolocations = ""
    combined = []
    counter = 0

    with open('combinedlogs.log', 'r+', encoding="utf-8") as input, open('geolocation.txt', 'r+', encoding="utf-8") as geolocation:
        logs = input.readlines()
        geolocations = geolocation.readlines()

        for i in range(1, len(logs)):

            counter += 1
            percentage = counter / len(logs) * 100
            print("%.2f" % percentage + '%')

            for k in range(1, len(geolocations)):

                if (geolocations[k].split(',')[0].rstrip() == logs[i].split(' ')[8].rstrip()):
                    combined.append(logs[i].rstrip() + ',' + geolocations[k].split(',')[1].rstrip()
                                            + ',' + geolocations[k].split(',')[2].rstrip()
                                            + ',' + geolocations[k].split(',')[3].rstrip()
                                            + ',' + geolocations[k].split(',')[4].rstrip()
                                            + "\n")

        input.close()
        geolocation.close()

    # replace file contents with the new appended lines
    with open("combinedlogs.log", "w", encoding="utf-8") as output:
        output.write(''.join(map(str, combined)))
        output.close()

# remove_headers()
# sort_files()
#ip_2_geo()
#fix_column_number()
#robots()
#append_robots()
#append_geolocation()

