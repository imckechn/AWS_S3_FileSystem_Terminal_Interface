import configparser
import os
import sys
import pathlib
import boto3
from helpers import create_bucket, download_file, upload_file
from folder import Folder
from file import File
from bucket import Bucket


config = configparser.ConfigParser()
config.read("S5-S3.conf")
aws_access_key_id = config['prof' ]['aws_access_key_id' ]
aws_secret_access_key = config['prof']['aws_secret_access_key']
connected = False

#Try making a connection to S3 using boto3
try:
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    s3 = session.client('s3')
    s3_res = session.resource('s3')
    print("Welcome to the AWS S3 Storage Shell(S5)")
    print("You are now conneced to your S3 storage")
    connected = True

    buckets = []
    response = s3.list_buckets()
    for bucket in response['Buckets']:

        buckets.append(bucket [ "Name" ])

except:
    print("Welcome to the AWS S3 Storage Shell(S5)")
    print("You could not be connected to your S3 storage")
    print("Please review procedures for authenticating your account on AWS S3")
    quit()


#Get all the buckets and store them in memory
buckets = []
for bucket in response['Buckets']:
    buck = Bucket(bucket["Name"])
    buckets.append(buck)

#Get all the files and store them in memory
files = []
for bucket in buckets:

    #Get the buckets in the S3 storage from the names we already have
    s3_bucket = s3_res.Bucket(bucket.get_name())

    #Loop through the objects in the bucket and create a file object for each one
    objects = s3_bucket.objects.all()
    for elem in objects:
        file = File()
        file.init_from_s3(elem)
        files.append(file)

#Get the folders from the files and store them in memory
folders = []
for file in files:

    #Create folders from the files
    bucket = file.get_bucket()
    full_path = file.get_path()

    broken_up_path = full_path.split("/")
    broken_up_path.insert(0, "")

    #Loop through each folder one at a time
    for i in range(len(broken_up_path) - 1):

        #Create a folder starting at the root and going down
        path = ""
        for j in range(i):
            path += broken_up_path[j] + "/"
        new_folder = Folder(file.get_bucket(), path)

        #Check if a folder aleady exists
        for folder in folders:
            if folder.get_path() == new_folder.get_path() and folder.get_bucket() == new_folder.get_bucket():
                new_folder = None
                break

    folders.append(new_folder)

#The current working directory, this includes the current bucket if applicable
directory = []
userInput = ""

while(userInput != "exit" or userInput != 'quit'):
    userInput = input("S5> ")

    if userInput[:13] == "create_bucket":
        values= userInput.split("/")

        exists = False
        for bucket in buckets:
            if bucket.get_name() == values[1]:
                print("Failure: Bucket already exists")
                exists = True
                break

        if exists == False:
            try:
                create_bucket(s3, values[1])
                buck = Bucket(values[1])
                buckets.append(buck)
            except:
                print("Failure: Could not create bucket")

    elif userInput[:6] == "cwlocn":
        if directory == []:
            print("/")
        else:
            path = ""
            for folder in directory:
                path += "/" + folder
            print(path)

    elif userInput[:6] == "chlocn":
            # Identify if the user is trying to go backwards
            if userInput == "chlocn /" or userInput == "chlocn ~":
                directory = []

            elif userInput == "chlocn ..":
                directory.pop()

            elif userInput == "chlocn ":
                print("Error, need to enter in a destination")
                continue

            else:
                old_directory = directory.copy()

                userInput = userInput[len("chlocn "):]
                path_values = userInput.split("/")
                if path_values[0] == '':
                    path_values.pop(0)

                #identify if it's a fill or relative path
                isFullPath = False

                for bucket in buckets:
                    if bucket.get_name() == path_values[0]:     #it's the full path
                        isFullPath = True
                        directory = []

                        #Set the working directory to the one specified by the user
                        for i in range(len(path_values)):
                            directory.append(path_values[i])

                if isFullPath == False:  #it's a relative path
                    for folder in path_values:
                        if folder == "..":
                            directory.pop()
                        else:
                            directory.append(folder)

                # --- Checking that the current directory exists ---

                # Get the current directory MINUS the bucket
                cur_der = ""
                for i in range(1, len(directory)):
                    cur_der += directory[i] + "/"


                cur_der = cur_der[:-1]  #Pop the last '/' off

                print("cur_der: " + cur_der)

                exists = False
                for folder in folders:
                    print("folder being checked")
                    print(folder.get_path()[1:])

                    if folder.get_bucket() == directory[0]: #Check that the bucket matches
                        if cur_der == folder.get_path():
                            exists = True
                            break

                if exists != True:
                    directory = old_directory
                    print("Error: Directory doesnt exist")

    elif len(directory) > 0:

        if userInput[:6] == "cwlocn":
            if directory == []:
                print("/")
            else:
                path = ""
                for folder in directory:
                    path += "/" + folder
                print(path)



        if "locs3cp" in userInput:
            values = userInput.split(" ")

            ans = upload_file(s3, values[1], values[2])

            if ans == True:
                file = File()
                file.init_from_file_creation(values[2])
                files.append(file)



        if "s3loccp" in userInput:
            values = userInput.split(" ")
            download_file(s3, values[1], values[2])



        if userInput[:13] == "create_folder":
            path = userInput.split("/")

            #identify if it's a fill or relative path
            isFullPath = False
            for i in range(len(buckets)):
                if buckets[i].get_name() == directory[0]:
                    isFullPath = True
                    new_folder = Folder(path[0], path[1:])

                    # -- Need to add a checker incase the new path is like 6 folders longer than what already exists
                    folders.append(new_folder)

            if isFullPath == False: #it's a relative path
                


            if path[0] in bucketNames:    #full path
                if path in folders:
                    print("Failure: Folder already exists")
                else:
                    folders.append(path)

            else:   # Relative path
                current_path = ""
                for folder in directory:
                    current_path += folder + "/"

                folders.append(current_path + path)



    else:
        print("Error: Command not recognized or you are not in a bucket")

print("Goodbye")
exit()

# chlocn cis4010-a1-ianmckechnie




while(connected):
    userInput = input("S5> ")

    if userInput == "dir":
        print("Directory")
        print(directory)
        print("folders")
        print(folders)

    if userInput == "exit" or userInput == 'quit':
        print("Goodbye")
        quit()


    if len(directory) == 0:
        if "cd" in userInput:
            values = userInput.split(" ")
            if values[1] in bucketNames:
                directory.append(values[1])
                print("Directory changed to: " + values[1])
            else:
                print("Failure: Directory does not exist")

    if userInput[:6] == "cwlocn":
        if directory == []:
            print("/")
        else:
            path = ""
            for folder in directory:
                path += "/" + folder
            print(path)

    if userInput[:4] == "list":
        if userInput == "list":
            if directory == []: #If you're in the home directory, list the buckets
                for name in bucketNames:
                    print(name)

            else:   #if you in a bucket or a bucket and a folder, list the contents of your spot
                bucket = s3_res.Bucket(directory[0])

                for obj in bucket.objects.all():
                    print(obj)
                    name = obj.key
                    elems = name.split("/")
                    match = True

                    if len(elems) <= len(directory):
                        for i in range(len(elems) - 1):
                            if elems[i] != directory[i + 1]:
                                match = False
                                break
                    else:
                        match = False

                    print("Matches:")
                    if match:
                        print(elems[len(elems) - 1])

                    duplicates = []

                    print("Folders")
                    print(folders)

                    #Now going to print the avalible folders
                    for elem in folders:
                        components = elem.split("/")

                        #Make sure the lenght of the folder path is at least as long as the length of the current directory path
                        if len(directory) >= len(components):

                            #Make sure there's no duplicate directories being printed
                            if components[len(directory)] not in duplicates:
                                areEqual = True

                                #Loop through the component parts and make sure they are equal to the current directory and are in the same order
                                for i in range(len(directory)):
                                    if components[i] != directory[i]:   #Make sure the directory and the current folder matches
                                        areEqual ==  False

                                #If there is a folder in the current directory, print the next folder name
                                if areEqual:
                                    duplicates.append(components[len(directory)])
                                    print(components[len(directory)] + "/")


        elif userInput[6:7] == "-I":
            continue

        else:
            values = userInput.split("/")
            print(values)

            if values[1] in bucketNames: #It's an absolute path
                bucket = s3_res.Bucket(values[1])
            else: #it's a relative path
                bucket = s3_res.Bucket(directory[0])

            for obj in bucket.objects.all():
                print(obj)


    else:
        if userInput == "ls":
            files = os.listdir('.')
            for filename in files:
                print(filename)

        if "locs3cp" in userInput:
            values = userInput.split(" ")
            print(values)
            #upload_file(s3, values[1], values[2])

        if "s3loccp" in userInput:
            values = userInput.split(" ")
            download_file(s3, values[1], values[2])

        if "create_folder" in userInput:
            path_values = userInput.split("/")
            path = userInput[len("create_folder/"):]

            #identify if it's a fill or relative path
            if path_values[1] in bucketNames:    #full path
                if path in folders:
                    print("Failure: Folder already exists")
                else:
                    folders.append(path)

            else:   # Relative path
                current_path = ""
                for folder in directory:
                    current_path += folder + "/"

                folders.append(current_path + path)

        if "chlocn" in userInput:
            # Identify if the user is trying to go backwards
            if userInput == "chlocn /" or userInput == "chlocn ~":
                directory = []

            elif userInput == "chlocn ..":
                directory.pop()

            elif userInput == "chlocn ":
                continue

            else:
                old_directory = directory.copy()

                userInput = userInput[len("chlocn "):]
                path_values = userInput.split("/")
                if path_values[0] == '':
                    path_values.pop(0)

                #identify if it's a fill or relative path
                if path_values[0] in bucketNames:    #full path
                    if path in folders:
                        for i in range(len(directory), len(path_values)):
                            if path_values[i] == "..":
                                directory.pop()
                            else:
                                directory.append(path_values[i])

                else:  # Relative path
                    for folder in path_values:
                        if folder == "..":
                            directory.pop()
                        else:
                            directory.append(folder)

                #Check that the current directory exists
                cur_der = ""
                for fold in directory:
                    cur_der += fold + "/"

                cur_der = cur_der[:-1]  #Pop the last '/' off

                exists = False
                for folder in folders:
                    if cur_der in folder:
                        exists = True
                        break

                if exists != True:
                    directory = old_directory
                    print("Error: Directory doesnt exist")




# HELPERS
# locs3cp upload/temp2/temp2.txt /cis4010-a1-ianmckechnie/temp.txt
# s3loccp /cis4010-a1-ianmckechnie/temp.txt downloaded/temp.txt
# create_bucket/cis4010b01-ianmckechnie

# create_folder/temp
# create_folder/temp2/temp3
# create_folder/cis4010-a1-ianmckechnie/temp3

# chlocn /temp
# chlocn /
# chlocn ..
# chlocn ../..
# chlocn /temp2
# chlocn ../temp2/temp3

# list /cis4010/images/cats


#LATEST
# cd cis4010-a1-ianmckechnie
# create_folder/temp3
# create_folder/temp2/temp3
# chlocn /temp2