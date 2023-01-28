import configparser
import os
import sys
import pathlib
import boto3
import helpers
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

except:
    print("Welcome to the AWS S3 Storage Shell(S5)")
    print("You could not be connected to your S3 storage")
    print("Please review procedures for authenticating your account on AWS S3")
    quit()

#Get all the buckets and store them in memory
buckets, files, folders = helpers.get_buckets_files_folders(s3, s3_res)

#The current working directory, this includes the current bucket if applicable
directory = []
userInput = ""

while(userInput != "exit" or userInput != 'quit'):
    userInput = input("S5> ")

    #Create a new bucket in s3
    if userInput[:13] == "create_bucket":
        answer = helpers.create_bucket(s3_res, userInput, buckets)

    elif userInput[:6] == "cwlocn":
        answer = helpers.get_current_location(directory)

    #Change location
    elif userInput[:6] == "chlocn":
            answer = helpers.change_location(userInput, directory, buckets, folders)

    elif len(directory) > 0:

        if userInput[:7] == "locs3cp":
            answer = helpers.copy_local_file_to_s3(userInput, s3, files, folders)

        elif userInput[:7] == "s3loccp":
            answer = helpers.copy_s3_file_to_local(userInput, s3, buckets, directory)

        elif userInput[:13] == "create_folder":
            answer = helpers.create_folder(userInput, buckets, folders, directory)
            continue

        elif userInput[:4] == "list":
            answer = helpers.list_files_and_folders(userInput, files, folders, directory)
            continue

        elif userInput[:6] == "S3copy":
            answer = helpers.copy_s3_file_to_s3(userInput, buckets, directory, files, s3_res)

        elif userInput[:8] == "s3delete":
            answer = helpers.delete_file(userInput, files, directory,s3)

        elif userInput[:13] == "delete_bucket":
            answer = helpers.delete_bucket(userInput, directory, buckets, s3_res)

    else:
        print("Error: Command not recognized or you are not in a bucket")

print("Goodbye")
exit()


# HELPERS
# chlocn /tempbucketforcisclassguelph
# create_folder /test/temp/hello/world
# chlocn /images/cats

# locs3cp downloaded/temp.txt /tempbucketforcisclassguelph/images/cats/help.txt

# cwlocn
# s3loccp cis4010-a1-ianmckechnie/temp.txt downloaded/new.txt
# s3loccp tempbucketforcisclassguelph/images/cats/a.txt few.txt
# list /tempbucketforcisclassguelph/images/cats
# list -l /tempbucketforcisclassguelph/images/cats
# s3copy /cis4010b01/images/cats/pichappycat.png pic001.png
# s3copy pic001.png /cis4010b1/backups/pic001.png

# TO DO
# Make code function based intead of if statement based
# Get all functions to return 1 or 0 depending on success/failure
# Instead of having cases for relative postion and full position, why not just change them all to full posiiotns?


# Copying files
# chlocn /tempbucketforcisclassguelph
# S3copy test.txt /tempbucketforcisclassguelph/images/text2.txt
# S3copy /tempbucketforcisclassguelph/images/text2.txt /tempbucketforcisclassguelph/images/text3.txt
# S3copy /tempbucketforcisclassguelph/images/text3.txt /tempbucketforcisclassguelph/images/cats/text4.txt
# S3copy /tempbucketforcisclassguelph/images/cats/text4.txt text5.txt
# chlocn /images/cats
# S3copy text4.txt /tempbucketforcisclassguelph/images/cats/text6.txt
# S3copy /tempbucketforcisclassguelph/images/cats/text6.txt /tempbucketforcisclassguelph/text7.txt
# s3delete text7.txt
# s3delete /tempbucketforcisclassguelph/images/cats/text6.txt
# delete_bucket /cis4010-a1-ianmckechnie

# Copying cloud file to local system
# chlocn /tempbucketforcisclassguelph
# s3loccp text5.txt downloaded/text5.txt
