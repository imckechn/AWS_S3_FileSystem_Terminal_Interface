import configparser
import os
import sys
import pathlib
import boto3

config = configparser.ConfigParser()
config.read("S5-S3.conf")
aws_access_key_id = config['prof' ]['aws_access_key_id' ]
aws_secret_access_key = config['prof']['aws_secret_access_key']

try:
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    s3 = session.client('s3')
    s3_res = session.resource('s3')
    print("Welcome to S3 storage session Demo")


    buckets = []
    response = s3.list_buckets ()
    for bucket in response['Buckets']:
        buckets.append(bucket [ "Name" ])

    for bucket in buckets:
        print ( bucket )
except:
    print("Cannot connect to s3")