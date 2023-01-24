from helpers import upload_file, download_file
import boto3

class File:

    #def __init__(self, bucket, path, name, s3, localFile):
    #    self.path = path
    #    self.name = name
    #    self.bucket = bucket

    #    upload_file(s3, localFile, path + "/" + name)

    def init_from_s3(self, name):
        self.bucket = name.bucket_name

        elements = name.key.split("/")
        self.name = elements[-1]

        path = ""
        for i in range(len(elements) - 1):
            path += elements[i] + "/"

        self.path = path

    def __str__(self):
        return self.bucket + "/" + self.path + "/" + self.name

    def get_path(self):
        return self.path

    def get_name(self):
        return self.name

    def get_bucket(self):
        return self.bucket

    def set_path(self, new_bucket, new_path, s3):
        try:
            #Change the path on S3
            s3.Object(self. new_bucket, new_path).copy_from(CopySource=self.bucket+"/"+self.path+"/"+self.name)
            s3.Object(self.bucket,self.bucket+"/"+self.path+"/"+self.name).delete()

            #update the instance variables
            self.path = new_path
            self.bucket = new_bucket

            return True
        except :
            return False