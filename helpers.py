
import configparser
import os
import sys
import pathlib
import boto3
from folder import Folder
from file import File
from bucket import Bucket

# Function to upload a file to S3
# Params: s3 is the boto3 s3 client, local_file is the path to the file to upload, aws_file_name is the bucket name and name of the file on S3 (like a path)
def upload_file(s3, local_file, bucket, aws_file_name):
    try:
        s3.upload_file(local_file, bucket, aws_file_name)
        return True
    except Exception as e:
        print("Error, ", e)
        return False

# Function to download a file from S3
# Params: s3 is the boto3 s3 client, local_file is the path to where the file will be downloaded from, aws_file_name is the bucket name and name of the file on S3 (like a path)
def download_file(s3, local_file, bucket, aws_file_name):
    try:
        s3.download_file(bucket, aws_file_name, local_file)
        return True
    except Exception as e:
        print("Error, ", e)
        return False

def checkIfPathDoesntExists(path, bucket, folders):
    for folder in folders:
        if folder.get_bucket() == bucket and folder.get_path_as_list() == path:
            return False
    return True

def folderInPath(path, bucket, folders):
    for folder in folders:
        folderList = folder.get_path_as_list()

        if folderList == path and folder.get_bucket() == bucket:
            return True
    return False

def get_buckets_files_folders(s3, s3_res):
    buckets = []
    files = []
    folders = []
    response = s3.list_buckets()

    for bucket in response['Buckets']:
        if bucket["Name"] == "cis4010-a1-ianmckechnie":
            continue
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
            response = s3.head_object(Bucket=elem.bucket_name, Key=elem.key)
            size = response['ContentLength']
            file = File()
            file.init_from_s3(elem, size)
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

    return buckets, files, folders


def create_bucket(s3_res, userInput, buckets):
    values = userInput.split("/")

    for bucket in buckets:
        if bucket.get_name() == values[1]:
            print("Failure: Bucket already exists")
            return 1

    try:
        s3_res.create_bucket(Bucket=values[1])
        buck = Bucket(values[1])
        buckets.append(buck)
        return 0

    except Exception as e: 
        print("Error, ", e)
        return 1

def get_current_location(directory):
    if directory == []:
        print("/")
    else:
        path = ""
        for folder in directory:
            path += "/" + folder
        print(path)

    return 0

def change_location(userInput, directory, buckets, folders):
    # Identify if the user is trying to go backwards
    if userInput == "chlocn /" or userInput == "chlocn ~":
        for i in range(len(directory)):
            directory.pop()
        return 0

    elif userInput == "chlocn ..":
        directory.pop()
        return 0


    elif userInput == "chlocn ":
        print("Error, need to enter in a destination")
        return 1

    else:
        old_directory = directory.copy()

        userInput = userInput[len("chlocn "):]
        path_values = userInput.split("/")
        if path_values[0] == '':
            path_values.pop(0)

        if len(path_values) == 0:
            print("Error: Invalid path")
            return 1

        #identify if it's a fill or relative path
        isFullPath = False
        for bucket in buckets:
            if bucket.get_name() == path_values[0]:     #it's the full path
                isFullPath = True

                for i in range(len(directory)):
                    directory.pop()

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
                        directory = old_directory.copy() #This doesnt work but it will reset it when it breaks out of this function
                        break

                else:
                    if folderInPath(path_values[1:], path_values[0], folders):
                        for p in path_values:
                            directory.append(p)
                        break
                    else:
                        print("Error: Folder does not exist")
                    break

        if isFullPath == False:  #it's a relative path
            full_path = directory.copy() + path_values

            if folderInPath(full_path[1:], full_path[0], folders):
                for p in path_values:
                    directory.append(p)

            else:
                print("Error: Folder does not exist")

def copy_local_file_to_s3(userInput, s3, files, folders):
    values = userInput.split(" ")

    if len(values) != 3:
        print("Error: Invalid number of arguments")
        return 1

    local_destination = values[1]

    aws_info = values[2].split("/") #It's a three-tuple for some reason with index 0 being an empty string

    if aws_info[0] == '':
        aws_info.pop(0)

    bucket = aws_info[0]
    file_name = ""
    for i in range(1, len(aws_info)):
        file_name += aws_info[i] + "/"

    file_name = file_name[:-1]

    file_size = os.path.getsize(local_destination)

    ans = upload_file(s3, local_destination, bucket, file_name)

    if ans == True:
        file = File()
        file.init_from_file_creation(values[2].split("/"), file_size)
        files.append(file)

        #Create a new folder for it if neccessary
        new_folder = Folder(file.get_bucket(), file.get_path())

        #Check if a folder aleady exists
        for folder in folders:
            if folder.get_path_as_list() == new_folder.get_path_as_list() and folder.get_bucket() == new_folder.get_bucket():
                new_folder = None
            break

        if new_folder:
            folders.append(new_folder)
        return 0

    else:
        return 1

def copy_s3_file_to_local(userInput, s3, buckets, directory):
    #check if it's a fulll path or relative path, if relative, make it full
    parts = userInput.split(' ')

    cloud_path_list = parts[1].split('/')
    local_path_list = parts[2].split('/')

    if cloud_path_list[0] == '':
        cloud_path_list.pop(0)

    if local_path_list[0] == '':
        local_path_list.pop(0)

    isFullPath = False
    for bucket in buckets:
        if bucket.get_name() == cloud_path_list[0]:
            isFullPath = True
            break

    if isFullPath == False:
        cloud_path_list = directory.copy() + cloud_path_list


    #Get the bucket name, the cloud path, and the local path
    bucket = cloud_path_list[0]
    cloud_path = ""
    for i in range(1, len(cloud_path_list)):
        cloud_path += cloud_path_list[i] + "/"
    cloud_path = cloud_path[:-1]

    local_path = ""
    for i in range(0, len(local_path_list)):
        local_path += local_path_list[i] + "/"
    local_path = local_path[:-1]

    #Call download function
    ans = download_file(s3, local_path, bucket, cloud_path)

    if ans == False:
        return 1
    return 0

def create_folder(userInput, buckets, folders, directory):
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
                    return 0

    if isFullPath == False: #it's a relative path
        for i in range(1, len(path) + 1):
            full_path = directory[1:].copy()
            for j in range(i):
                full_path.append(path[j])

            if checkIfPathDoesntExists(full_path, directory[0], folders):
                new_folder = Folder(directory[0], full_path)
                folders.append(new_folder)
                return 0

    print("Error: Folder already exists")
    return 1

def copy_folder(userInput, buckets, directory, files, s3_res):
    parts = userInput.split(" ")
    starting_location = parts[1]
    ending_location = parts[2]

    #Change to correct format
    start = starting_location.split("/")
    end = ending_location.split("/")

    if end[0] == "":
        end.pop(0)
    if start[0] == "":
        start.pop(0)

    #If start position is a relative position, change it to be the full position
    start_is_rel = True
    end_is_rel = True

    for bucket in buckets:
        if bucket.get_name() == start[0]:
            start_is_rel = False

        if bucket.get_name() == end[0]:
            end_is_rel = False

    if start_is_rel:
        start = directory.copy() + start
    if end_is_rel:
        end = directory.copy() + end

    #Copy the file to the end position
    success_copying = False
    for file in files:
        if file.is_file(start):
            success_copying = True
            #Set the local file objects path to the new directory
            new_file = File()
            new_file.init_from_file_creation(end, file.get_size())
            files.append(new_file)

            # --- Copy the file over on S3 ---
            #turn the end position into a string
            start_string = ""
            for i in range(1, len(start)):
                start_string += start[i] + "/"

            start_string = start_string[:-1]

            end_string = ""
            for i in range(1, len(end)):
                end_string += end[i] + "/"
            end_string = end_string[:-1]

            copy_source = {
                'Bucket': start[0],
                'Key': start_string
            }
            try:
                s3_res.meta.client.copy(copy_source, end[0], end_string)
            except Exception as e:
                print("Error, ", e)
                files.pop()
                return 1

    #Error message if there was an error copying a file
    if success_copying == False:
        print("Error: Could not copy file")
        return 1
    return 0

def delete_file(userInput, files, directory,s3):
    parts = userInput.split(" ")
    location = parts[1].split("/")

    if location[0] == "":
        location.pop(0)

    if len(location) == 1:
        #Delete the file
        for file in files:
            if file.get_name() == location[0] and file.get_bucket() == directory[0] and file.is_in_directory(directory):
                try:
                    file.self_delete(s3)
                    files.remove(file)
                except:
                    print("Error: Could not delete file")
                    return 1
                break
    else:
        for file in files:
            if file.is_file(location):
                try:
                    file.self_delete(s3)
                    files.remove(file)
                except:
                    print("Error: Could not delete file")
                    return 1
    return 0

def delete_bucket(userInput, directory, buckets, s3_res):
    parts = userInput.split("/")

    bucket_name = parts[1]

    if bucket_name == directory[0]:
        print("Error, you cannot delete the bucket you are currently in")
        return 1

    removed = False
    for bucket in buckets:
        if bucket.get_name() == bucket_name:
            try:
                bucket.delete(s3_res)
                buckets.remove(bucket)
                removed = True
                return 0
            except Exception as e: 
                print("Error, ", e)
                return 1

    if removed == False:
        print("Error: Could not find bucket")
        return 1

def list_files_and_folders(userInput, files, folders, directory):
    #List the current directory
    if userInput == "list" or userInput == "list /":
        # List the files
        for file in files:
            if file.is_in_directory(directory):
                print(file.get_name())

        # List the folders
        for folder in folders:
            if folder.is_in_directory(directory):
                folder.print_next_folder(directory)

    elif "-l" in userInput:
        # ----------- NEEDS TO BE WORKED ON -------------
        elements = userInput.split("/")

        if userInput == "list -l":  #if it's just "list -l", ie. the current directory
            # List the files
            for file in files:
                if file.is_in_directory(directory):
                    print(file.get_name() + " " + str(file.get_size()) + "bytes")

            # List the folders
            for folder in folders:
                if folder.is_in_directory(directory):
                    folder.print_next_folder(directory)

        else:   #if it's "list -l /path/to/folder"
            elements.pop(0)

            # List the files
            for file in files:
                if file.is_in_directory(elements):
                    print(file.get_name() + " " + str(file.get_size()) + "bytes")

            # List the folders
            for folder in folders:
                if folder.is_in_directory(elements):
                    folder.print_next_folder(elements)

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
