import boto3

class Folder:

    def __init__(self, bucket, path):
        self.path = path #Treating path as an array of each folder that is in the path
        self.files = []
        self.bucket = bucket

    def __str__(self):
        return self.bucket + "/" + self.path

    def get_path(self):
        return self.path

    def get_files(self):
        return self.files

    def add_file(self, file):
        self.files.append(file)

    def get_bucket(self):
        return self.bucket

    def move_file(self, file_name, new_folder, s3):
        success = False

        for file in self.files:
            if file.get_name() == file_name:

                #Remove file from current folder
                self.files.remove(file)

                #Set new path on the file
                success = file.set_path(new_folder.get_bucket(), new_folder.get_path(), s3)
                if success == False:
                    return False

                #Add file to new folder
                new_folder.add_file(file)

                success = True
                break

        return success


