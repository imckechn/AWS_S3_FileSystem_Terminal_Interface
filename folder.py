import boto3

class Folder:

    def __init__(self, bucket, path):
        if type(path) != list:
            print("ERROR, Wrong format for the folder path")
        self.path = path #Treating path as an array of each folder that is in the path
        #self.files = []
        self.bucket = bucket

    def __str__(self):
        return self.bucket + "/" + self.path

    def get_path_as_string(self):
        fullPath = ""
        for elem in self.path:
            fullPath += elem + "/"
        return fullPath

    def get_path_as_list(self):
        return self.path

    # def get_files(self):
    #     return self.files

    # def add_file(self, file):
    #     self.files.append(file)

    def get_bucket(self):
        return self.bucket

    def move_file(self, file_name, new_folder, s3):
        success = False

        for file in self.files:
            if file.get_name() == file_name:

                #Remove file from current folder
                self.files.remove(file)

                #Set new path on the file
                success = file.set_path(new_folder.get_bucket(), new_folder.get_path_as_list(), s3)
                if success == False:
                    return False

                #Add file to new folder
                new_folder.add_file(file)

                success = True
                break

        return success

    def is_in_directory(self, path):
        #The bucket name should be the first element in the given path
        #The lenth of the current path (only folders, not bucket) should be the same as the given path (which includes the bucket)
        if self.bucket == path[0] and len(self.path) == len(path):
            #Minus one because self.path[-1] is the bucket we are trying to get the name of
            for i in range (len(self.path) - 1):
                if self.path[i] != path[i + 1]:
                    #print("Failed A")
                    return False
        else:
            #print("Failed B")
            return False

        return True

    def print_next_folder(self, path):
        print(self.path[-1] + "/")