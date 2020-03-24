# By Rakeen Rouf
import pandas as pd
import os
import platform
import time
from noise_cluster import NoiseCluster


class TxtToFeather:
    """The Fog device reads in the chunked .TXT saved by the DAQ/s from a locally shared folder. This process is
    governed by utilizing a custom Watchdog. The purpose of the Watchdog is to delegate the incoming data and make
    sure no data is left unread (No Data Loss). The Watchdog keeps on processing the same .TXT file repeatedly until
    a new .TXT file is available in the shared folder. Once a new file emerges, it signals the Watchdog that no new
    data will be appended to the old file. As a redundancy routine, the watchdog checks the old .TXT file once again
    (for modifications) before moving on to the new file. And this process continues. Once a file passes the Watchdog,
    all new data (data not available in previous iterations) is parsed. Each new file gets an object
    (from object-oriented programming) of its own, and within the object different states (last line read, rows to skip)
     pertaining to the file is stored. As a new file emerges, the old file’s object is deleted (garbage collection) to
     avoid memory buildup.  The parsed data (Pandas Dataframe) is then passed through on-line clustering/classification
     models and saved in a binary file format known as Feather. Feather is chosen as the file dump format since it is a
     fast, lightweight, and easy-to-use binary file format for storing data frames and can be directly read back in as
     a data frame in concurrent/future processes."""

    def __init__(self,  cluster, data_file=r'livedata', skip_rows=9):
        self.data = pd.DataFrame()
        self.data_file = '/media/jetson/XavierSSD512/ae/test/{}.TXT'.format(data_file)
        self.skip_rows = skip_rows
        self.cluster = cluster
        self.path = '/media/jetson/XavierSSD512/data_store/{}'

    def parse_columns(self):
        """
        Parses joint columns to a more readable format
        """
        self.data['ID'], self.data['SSSSSSSS.mmmuuun'] = self.data['ID     SSSSSSSS.mmmuuun'].str.split('    ', 1).str
        self.data['SSSSSSSS.mmmuuun'] = self.data['SSSSSSSS.mmmuuun'].astype(str).str.strip()

    def read_txt(self, widths=[3, 21, 4, 6, 4, 6, 12, 12]):
        """
        Reads appropriate columns from the ae data text file
        """
        cols = ['ID', 'SSSSSSSS.mmmuuun', 'AMP', 'THR', 'A-FRQ', 'R-FRQ', 'SIG STRNGTH', 'ABS-ENERGY']

        widths = widths
        self.data = pd.read_fwf(self.data_file, widths=widths, header=None, skiprows=self.skip_rows)
        self.data.columns = cols

        self.data = self.data.loc[self.data['ID'] == 1]
        self.skip_rows += len(self.data)

    def get_file_data(self):
        try:
            self.read_txt()
        except KeyError:
            self.data = pd.read_fwf(self.data_file)

            for i in range(len(self.data)):
                if self.data.iloc[:, 0][i] == 'ID     SSSSSSSS.mmmuuun':
                    self.skip_rows = i + 1
                    break

            self.read_txt()

        self.data = self.data[['SSSSSSSS.mmmuuun', 'AMP', 'THR', 'A-FRQ', 'R-FRQ', 'SIG STRNGTH', 'ABS-ENERGY']]

    @staticmethod
    def fog_file_writer(data, location, count):
        """Writes data to files for fog visualizations"""

        data.to_csv(location.format(str(count % 2000) + '.txt'))
        count += 1

        return count

    def loaddata(self, file_numb):
        self.get_file_data()
        new_data = self.data
        plot_data = new_data[['SSSSSSSS.mmmuuun', 'AMP', 'THR', 'A-FRQ', 'R-FRQ', 'SIG STRNGTH', 'ABS-ENERGY']]
        labels = self.cluster.cluster_now(plot_data[['AMP', 'THR', 'SIG STRNGTH', 'ABS-ENERGY']])
        plot_data['labels'] = labels

        plot_data.reset_index(drop=True, inplace=True)
        plot_data.to_feather(self.path.format(file_numb))

    def modification_date(self):

        if platform.system() == 'Windows':
            return os.path.getmtime(self.data_file)
        else:
            stat = os.stat(self.data_file)
            return stat.st_mtime


if __name__ == '__main__':
    # data processing stuff
    file_num = 0
    datafile = r'load_{}'
    iteration = 0
    mod_time = 0
    noise_cluster = NoiseCluster('4_trained_model_SVM_ct2024.joblib')
    txt_to_f = TxtToFeather(noise_cluster, data_file=datafile.format(iteration))
    print('Waiting For Data...')

    # Watchdog logic to keep the loop iterating 
    while True:
        if mod_time == 0:
            if os.path.exists(txt_to_f.data_file):
                print('Test Initiated')
            else:
                continue

        cur_mod_time = txt_to_f.modification_date()
        if mod_time < cur_mod_time:
            time.sleep(0.01)
            try:
                txt_to_f.loaddata(file_num)
                file_num += 1
            except Exception as r:
                print(repr(r))
                pass
            mod_time = cur_mod_time
        elif mod_time == cur_mod_time:
            ff = '/media/jetson/XavierSSD512/ae/test/{}.TXT'.format(datafile.format(iteration + 1))
            if os.path.exists(ff) and os.stat(ff).st_size != 0:
                iteration += 1
                txt_to_csv = TxtToFeather(noise_cluster, data_file=datafile.format(iteration), skip_rows=0)
                try:
                    txt_to_f.loaddata(file_num)
                    file_num += 1
                except Exception as r:
                    print(r)
                    pass
                mod_time = cur_mod_time
            else:
                pass
