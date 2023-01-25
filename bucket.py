class Bucket:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def get_name(self):
        return self.name

    def delete(self, s3):
        try:
            s3.Bucket(self.name).delete()
            return True
        except:
            return False