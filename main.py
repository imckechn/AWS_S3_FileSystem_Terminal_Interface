import configparser
import os
import sys
import pathlib
import boto3
from helpers import create_bucket, download_file, upload_file, checkIfPathDoesntExists, FolderInPath
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
files = []
folders = []

for bucket in response['Buckets']:
    buck = Bucket(bucket["Name"])
    buckets.append(buck)

#Get all the files and store them in memory
for bucket in buckets:
    #Get the buckets in the S3 storage from the names we already have
    s3_bucket = s3_res.Bucket(bucket.get_name())

    #Loop through the objects in the bucket and create a file object for each one
    objects = s3_bucket.objects.all()

    #If there are no objects in the bucket, then we need to create a folder for the bucket
    for elem in objects:
        file = File()
        file.init_from_s3(elem)
        files.append(file)


#Get the folders from the files and store them in memory
for file in files:

    #Create folders from the files
    bucket = file.get_bucket()
    path = file.get_path()

    #Loop through each folder one at a time
    for i in range(len(path)):

        new_folder = Folder(file.get_bucket(), path[:i + 1])

        #Check if a folder aleady exists
        for folder in folders:
            if folder.get_path_as_list() == new_folder.get_path_as_list() and folder.get_bucket() == new_folder.get_bucket():
                new_folder = None
                break

        if new_folder:
            folders.append(new_folder)


#The current working directory, this includes the current bucket if applicable
directory = []
userInput = ""

print("Available buckets:")
for bucket in buckets:
    print(bucket.get_name())

while(userInput != "exit" or userInput != 'quit'):
    print("Folders")
    for folder in folders:
        print(folder.get_path_as_list())
    userInput = input("S5> ")

    #Create a new bucket in s3
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
                create_bucket(s3_res, values[1])
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

    #Change location
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

                        #Check if the user is just navigating into a bucket
                        if len(path_values) == 1:
                            bucketExists = False
                            for bucket in buckets:
                                if bucket.get_name() == path_values[0]:
                                    directory.append(bucket.get_name())
                                    bucketExists = True
                                    break

                            if bucketExists == False:
                                print("Error: Bucket does not exist")
                                directory = old_directory.copy()
                                break

                        else:
                            if FolderInPath(path_values[1:], path_values[0], folders):
                                directory = path_values
                                break
                            else:
                                print("Error: Folder does not exist")
                            break

                if isFullPath == False:  #it's a relative path
                    full_path = directory.copy() + path_values

                    if FolderInPath(full_path[1:], full_path[0], folders):
                        directory = full_path

                    else:
                        print("Error: Folder does not exist")


    elif len(directory) > 0:

        if "locs3cp" in userInput:
            values = userInput.split(" ")

            print("values[2]")
            print(values[2])

            aws_info = values[2].split("/") #It's a three-tuple for some reason with index 0 being an empty string
            bucket = aws_info[1]
            file_name = ""
            for i in range(2, len(aws_info)):
                file_name += aws_info[i] + "/"

            file_name = file_name[:-1]

            ans = upload_file(s3, values[1], bucket, file_name)

            if ans == True:
                file = File()
                file.init_from_file_creation(values[2])
                files.append(file)

                #Create a new folder for it if neccessary
                new_folder = Folder(file.get_bucket(), file.get_path())

                #Check if a folder aleady exists
                for folder in folders:
                    if folder.get_path_as_list() == new_folder.get_path_as_list() and folder.get_bucket() == new_folder.get_bucket():
                        new_folder = None
                    break

                folders.append(new_folder)



        elif "s3loccp" in userInput:
            values = userInput.split(" ")
            download_file(s3, values[1], values[2])



        elif userInput[:13] == "create_folder":
            path = userInput.split(" ")
            path = path[1].split("/")

            if path[0] == '':
                path.pop(0)

            #identify if it's a fill path
            isFullPath = False
            for i in range(len(buckets)):
                if buckets[i].get_name() == path[0]:
                    isFullPath = True

                    for i in range(len(path)):
                        if checkIfPathDoesntExists(path[:i], path[0], folders):
                            new_folder = Folder(path[0], path[1:i])
                            folders.append(new_folder)

            if isFullPath == False: #it's a relative path
                print("relative")
                for i in range(1, len(path) + 1):
                    full_path = directory[1:].copy()
                    for j in range(i):
                        full_path.append(path[j])

                    if checkIfPathDoesntExists(full_path, directory[0], folders):
                        new_folder = Folder(directory[0], full_path)
                        folders.append(new_folder)

        elif userInput[:4] == "list":

            #List the current directory
            if userInput == "list" or userInput == "list /":
                #List the files
                for file in files:
                    if file.is_in_directory(directory):
                        print(file.get_name())

                #List the folders
                for folder in folders:
                    if folder.is_in_directory(directory):
                       folder.print_next_folder(directory)

            elif "-l" in userInput:
                # ----------- NEEDS TO BE WORKED ON -------------
                print("TBD")

            else:
                elements = userInput.split("/")
                elements.pop(0)

                #List the files
                for file in files:
                    for file in files:
                        if file.is_in_directory(elements):
                            file.get_name()

                #List the folders
                for folder in folders:
                    if folder.is_in_directory(elements):
                        folder.print_next_folder(elements)

        elif userInput[:6] == "S3copy":
            parts = userInput.split(" ")
            starting_location = parts[1]
            ending_location = parts[2]

            #Change to correct format
            start = starting_location.split("/")
            end = ending_location.split("/")

            #add the bucket to the start
            start.insert(0, directory[0])

            for file in files:
                if file.is_in_directory(start):
                    file.set_path(directory[0], end, s3)

        elif userInput[:8] == "s3delete":
            parts = userInput.split(" ")
            location = parts[1].split("/")

            if len(location) == 1:
                #Delete the file
                for file in files:
                    if file.get_name() == location[0] and file.get_bucket() == directory[0] and file.is_in_directory(directory):
                        try:
                            file.self_delete(s3)
                            files.remove(file)
                        except:
                            print("Error: Could not delete file")
                        break
            else:
                for file in files:
                    if file.is_in_directory(location):
                        try:
                            file.delete(s3)
                            files.remove(file)
                        except:
                            print("Error: Could not delete file")
        elif userInput[:13] == "delete_bucket":
            parts = userInput.split(" ")
            bucket_name = parts[1]

            for bucket in buckets:
                if bucket.get_name() == bucket_name:
                    try:
                        bucket.delete(s3)
                        buckets.remove(bucket)
                    except:
                        print("Error: Could not delete bucket")
                    break

    else:
        print("Error: Command not recognized or you are not in a bucket")

print("Goodbye")
exit()


# HELPERS
# chlocn /tempbucketforcisclassguelph
# create_folder /test/temp/hello/world
# chlocn /test/temp
# locs3cp downloaded/temp.txt /tempbucketforcisclassguelph/images/cats/temp.txt