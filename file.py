from helpers import upload_file, download_file
import boto3

class File:

    def init_from_file_creation(self, location, size):

        self.size = size
        self.bucket = location[0]
        self.name = location[-1]

        try:
            self.path = location[1:-1]
        except:
            self.path = []

    def init_from_s3(self, name, size):
        self.bucket = name.bucket_name
        self.size = size

        elements = name.key.split("/")
        self.name = elements[-1]

        path = []
        for i in range(len(elements) - 1):
            path.append(elements[i])

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

    def is_in_directory(self, path):
        if self.bucket == path[0] and len(self.path) == len(path) - 1:
            for i in range(len(self.path)):
                if self.path[i] != path[i + 1]:
                    return False
        else:
            return False

        return True

    def self_delete(self, s3):
        path = ""
        for elem in self.path:
            path += elem + "/"
        path += self.name

        response = s3.delete_object(
            Bucket=self.bucket,
            Key=path
        )

    def get_size(self):
        return self.size

    def is_file(self, path):
        cur_path = self.path.copy()
        cur_path.insert(0, self.bucket)
        cur_path.append(self.name)

        for i in range(len(cur_path)):
            if cur_path[i] != path[i]:
                return False

        return True