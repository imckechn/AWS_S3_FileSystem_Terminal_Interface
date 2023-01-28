import os
from folder import Folder
from file import File

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