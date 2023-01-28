# File System that Interacts with AWS
Written By Ian McKechnie
For CIS4030 Cloud Computing

## Description
This program allows the user to interact with the AWS S3 file system. The user can create, delete, and list buckets. The user can also upload, download, and delete files from the buckets. The user can also list the files in a bucket. Finally, the user can also move the files between the folders in S3 The program uses the AWS SDK for Python (Boto3) to interact with the AWS S3 file system.

Note: The folders are a construct of this terminal they do not exist in the S3 file system. The folders are used to organize the files in the terminal.

## Installation
Make sure you have pip or pip3

run
```pip3 install -r requirements.txt```

## Usage
Run the program using python3 or python
```python3 main.py```

## Assumptions / Limitations
- If a bucket has only empty folder is it, it can still be deleted
- You cannot run chlocn folderNameA/FolderNameB/../FolderNameB/
     - You can go only forwards or backwards per chlocn command, you cannot mix them
- 