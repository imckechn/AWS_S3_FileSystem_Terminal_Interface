import configparser
import os
import sys
import pathlib
import boto3
from helpers import create_bucket, download_file, upload_file

config = configparser.ConfigParser()
config.read("S5-S3.conf")
aws_access_key_id = config['prof' ]['aws_access_key_id' ]
aws_secret_access_key = config['prof']['aws_secret_access_key']
connected = False

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
    response = s3.list_buckets ()
    for bucket in response['Buckets']:
        buckets.append(bucket [ "Name" ])

    for bucket in buckets:
        print ( bucket )
except:
    print("Welcome to the AWS S3 Storage Shell(S5)")
    print("You could not be connected to your S3 storage")
    print("Please review procedures for authenticating your account on AWS S3")
    quit()

directory = []
folders = []
bucketNames = []
response = s3.list_buckets()

for bucket in response['Buckets']:
    bucketNames.append(bucket["Name"])

while(connected):
    userInput = input("S5> ")

    if userInput == "exit" or userInput == 'quit':
        print("Goodbye")
        quit()

    if "create_bucket" in userInput:
        values= userInput.split("/")
        if values[1] in bucketNames:
            print("Failure: Bucket already exists")

        else:
            create_bucket(s3, values[1])

    if len(directory) == 0:

        if userInput == 'list':
            for name in bucketNames:
                print(name)

        if "cd" in userInput:
            values = userInput.split(" ")
            if values[1] in bucketNames:
                directory.append(values[1])
                print("Directory changed to: " + values[1])
            else:
                print("Failure: Directory does not exist")

    else:
        if userInput == "ls":
            files = os.listdir('.')
            for filename in files:
                print(filename)

        if "locs3cp" in userInput:
            values = userInput.split(" ")
            upload_file(s3, values[1], values[2])

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

                if cur_der not in folders:
                    directory = old_directory







# HELPERS
# cd cis4010-a1-ianmckechnie
# locs3cp upload/temp.txt /cis4010-a1-ianmckechnie/temp.txt
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
