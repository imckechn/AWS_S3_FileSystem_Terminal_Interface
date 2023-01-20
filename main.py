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

currentBucket = None
bucketNames = []
response = s3.list_buckets()
for bucket in response['Buckets']:
    bucketNames.append(bucket["Name"])

while(connected):
    userInput = input("S5> ")

    if userInput == "exit" or userInput == 'quit':
        print("Goodbye")
        quit()

    if currentBucket == None:

        if userInput == 'list':
            for name in bucketNames:
                print(name)

        elif userInput[:2] == "cd":
            if userInput[3:] == "..":
                print("Cannot go back")

            if userInput[3:] in bucketNames:
                print("Changing to bucket: " + userInput[3:])
                currentBucket = userInput[3:]
            else:
                print("Directory does not exist")

        elif userInput[:5] == "mkdir":
            if userInput[6:] in bucketNames:
                print("Bucket already exists")

            else:
                create_bucket(userInput[6:], "ca-central-1")
        else:
            print("Command not recognized")


    elif currentBucket:
        if userInput == "ls":
            files = os.listdir('.')
            for filename in files:
                print(filename)

        if "locs3cp" in userInput:
            values= userInput.split(" ")
            upload_file(s3, values[1], values[2])

        if "s3loccp" in userInput:
            values= userInput.split(" ")
            download_file(s3, values[1], values[2])





#HERLPS
# cd cis4010-a1-ianmckechnie
# locs3cp upload/temp.txt /cis4010-a1-ianmckechnie/temp.txt
# s3loccp /cis4010-a1-ianmckechnie/temp.txt downloaded/temp.txt