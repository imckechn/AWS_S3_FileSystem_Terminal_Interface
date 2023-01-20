
import boto3

def create_bucket(bucket_name, region=None):

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except:
        return False
    return True

# Function to upload a file to S3
# Params: s3 is the boto3 s3 client, local_file is the path to the file to upload, aws_file_name is the bucket name and name of the file on S3 (like a path)
# Returns True on Success, False on Failure
def upload_file(s3, local_file, aws_file_name):
    aws_info = aws_file_name.split("/") #It's a three-tuple for some reason with index 0 being an empty string

    try:
        response = s3.upload_file(local_file, aws_info[1], aws_info[2])
    except:
        print("failed to upload file, " + response)
        return False

    print("Succeeded in uploading file")
    return True

# Function to download a file from S3
# Params: s3 is the boto3 s3 client, local_file is the path to where the file will be downloaded from, aws_file_name is the bucket name and name of the file on S3 (like a path)
# Returns True on Success, False on Failure
def download_file(s3, local_file, aws_file_name):
    aws_info = aws_file_name.split("/") #It's a three-tuple for some reason with index 0 being an empty string

    try:
        response = s3.download_file(aws_info[1], aws_info[2], local_file)
    except:
        print("failed to download file, " + response)
        return False

    print("Succeeded in downloading file")
    return True

