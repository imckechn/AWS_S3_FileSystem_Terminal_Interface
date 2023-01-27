
import boto3

# Function to create a bucket
# Params: s3 is the boto3 s3 client, bucket_name is the name of the bucket to create
def create_bucket(s3, bucket_name):
    try:
        answer = s3.create_bucket(Bucket=bucket_name)
    except Exception as e: 
        print("Error, ", e)

# Function to upload a file to S3
# Params: s3 is the boto3 s3 client, local_file is the path to the file to upload, aws_file_name is the bucket name and name of the file on S3 (like a path)
def upload_file(s3, local_file, bucket, aws_file_name):
    response = ""
    try:
        response = s3.upload_file(local_file, bucket, aws_file_name)
        return True
    except Exception as e: 
        print("Error, ", e)
        return False

# Function to download a file from S3
# Params: s3 is the boto3 s3 client, local_file is the path to where the file will be downloaded from, aws_file_name is the bucket name and name of the file on S3 (like a path)
def download_file(s3, local_file, bucket, aws_file_name):
    try:
        print("bucket", bucket)
        print("aws_file_name", aws_file_name)
        print("local_file", local_file)
        s3.download_file(bucket, aws_file_name, local_file)
    except Exception as e: 
        print("Error, ", e)

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