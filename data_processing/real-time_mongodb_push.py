# By Rakeen Rouf
import pandas as pd
import os
import platform
from pymongo import MongoClient
import glob


class MongoJsonUpload:
    """This class can be used to upload data processed at the Fog layer to the Cloud MongoDB Server """
    def __init__(self, file_path, data_file, host, username='tamgadmin', password='Memmech1g',
                 authmechanism='SCRAM-SHA-256', authsource='admin'):

        self.f_path = '{}{}'.format(file_path, data_file)

        # My cloud DB
        self.mongo_client = MongoClient(host=[host])
        db = self.mongo_client.shm_data

        self.acoustic_data = db.acoustic_data_test_1_28

    def data_loader(self):
        data = pd.read_feather(self.f_path)
        data = data.rename(columns={'SSSSSSSS.mmmuuun': 'time'})  # new method

        self.acoustic_data.insert_many(data.to_dict('records'))

        self.mongo_client.close()

    def modification_date(self):
        """Checks for the last modification date of the file"""

        if platform.system() == 'Windows':
            return os.path.getmtime(self.f_path)
        else:
            stat = os.stat(self.f_path)
            return stat.st_mtime


if __name__ == '__main__':
    # data path
    path = '/media/jetson/XavierSSD512/data_store/'

    # data processing stuff
    datafile = r'{}'
    iteration = 0
    mod_time = 0
    mongo_upload = MongoJsonUpload(path, datafile.format(iteration))
    print('Waiting For Data...')
    
    # Watchdog logic to keep the code running
    while True:
        if os.path.exists(mongo_upload.f_path):
            print('Test Initiated')
            mongo_upload.data_loader()
            break

    while True:
        ff = '{}{}*'.format(path, datafile.format(iteration + 1))
        if glob.glob(ff):
            iteration += 1
            plotter = MongoJsonUpload(path, datafile.format(iteration))
            while True:
                try:
                    plotter.data_loader()
                    break
                except Exception as r:
                    print(r)
                    pass
        else:
            continue
