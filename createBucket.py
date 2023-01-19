#!/usr/bin/env python3
#
#  Libraries and Modules
#
import configparser
import os 
import sys 
import pathlib
import boto3
import s3Functions as s3f
#

#
#  Find AWS access key id and secret access key information
#  from configuration file
#
config = configparser.ConfigParser()
config.read("S5-S3.conf")
aws_access_key_id = config['prof']['aws_access_key_id']
aws_secret_access_key = config['prof']['aws_secret_access_key']
try:
#
#  Establish an AWS session
#
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
#
#  Set up client and resources
#
    s3 = session.client('s3')
    s3_res = session.resource('s3')

    print ( "Welcome to the S3 Storage Demo - Create a Bucket" )

#
#  List buckets - before create
#
    print ( "S3 Buckets before createBucket performed: ")
    ret = s3f.list_buckets ( s3 )

    bname = sys.argv[1]
    try:
        s3.create_bucket(Bucket=bname, CreateBucketConfiguration={'LocationConstraint': 'ca-central-1'})
        print ( "Current S3 Buckets" ) 
        ret = s3f.list_buckets ( s3 )
    except :
        print ( "Cannot create bucket ",bname )
except:
    print ( "cannot connect to s3" )

