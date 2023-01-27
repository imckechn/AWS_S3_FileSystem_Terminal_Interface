
import boto3

# Function to create a bucket
# Params: s3 is the boto3 s3 client, bucket_name is the name of the bucket to create
def create_bucket(s3, bucket_name):
    try:
        answer = s3.create_bucket(Bucket=bucket_name)
    except:
        print("Failed to create bucket, " + answer)

# Function to upload a file to S3
# Params: s3 is the boto3 s3 client, local_file is the path to the file to upload, aws_file_name is the bucket name and name of the file on S3 (like a path)
def upload_file(s3, local_file, bucket, aws_file_name):
    aws_info = aws_file_name.split("/") #It's a three-tuple for some reason with index 0 being an empty string
    bucket = aws_info[1]
    file_name = ""
    for i in range(2, len(aws_info)):
        file_name += aws_info[i] + "/"

    file_name = file_name[:-1]

    try:
        response = s3.upload_file(local_file, bucket, file_name)
        return True
    except:
        print("failed to upload file, " + response)
        return False

# Function to download a file from S3
# Params: s3 is the boto3 s3 client, local_file is the path to where the file will be downloaded from, aws_file_name is the bucket name and name of the file on S3 (like a path)
def download_file(s3, aws_file_name, local_file):
    aws_info = aws_file_name.split("/") #It's a three-tuple for some reason with index 0 being an empty string

    try:
        response = s3.download_file(aws_info[1], aws_info[2], local_file)
    except:
        print("failed to download file, " + response)

def checkIfPathDoesntExists(path, bucket, folders):
    print("Given path = ")
    print(path)

    for folder in folders:
        print("Folder path = ")
        print(folder.get_path_as_list())
        if folder.get_bucket() == bucket and folder.get_path_as_list() == path:
            return False
    return True

def FolderInPath(path, bucket, folders):
    for folder in folders:
        folderList = folder.get_path_as_list()

        if folderList == path and folder.get_bucket() == bucket:
            return True
    return False