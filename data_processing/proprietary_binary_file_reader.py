import numpy as np


class ReadPci2Header:
    """
    Class for making header information object from .wsf waveform streaming files.
    """
    def __init__(self, file_name):
        """
        :param file_name: filepath
        :rtype file_name: str
        """
        fid = open(file_name, 'rb')

        # product id
        np.fromfile(fid, np.short, count=1)  # size_table_1
        np.fromfile(fid, np.uint8, count=1)  # product_id
        np.fromfile(fid, np.int8, count=1)  # space
        np.fromfile(fid, np.short, count=1)  # block_1
        s_model = fid.read(47)
        start_pos = np.str(s_model).find('E')
        s_ver = np.float(np.str(s_model)[start_pos+1: start_pos+5])

        # define group
        np.fromfile(fid, np.short, count=1)  # size_table_2
        # np.fromfile(fid, np.uint8, count=1)  # id212
        # np.fromfile(fid, np.uint8, count=1)  # bacgrpid
        np.fromfile(fid, np.uint8, count=1, offset=1)  # instead of previous 2 ops
        np.fromfile(fid, np.int8, count=1)  # group_number
        self.number_of_channels = np.int(np.fromfile(fid, np.int8, count=1))

        # channel_list = []
        for i in range(self.number_of_channels):
            # channel_list.append(np.fromfile(fid, np.int8, count=1))
            np.fromfile(fid, np.int8, count=1)

        # self.channel_list = channel_list
        # del channel_list

        # hardware setup
        for i in range(self.number_of_channels):
            np.fromfile(fid, np.short, count=1)  # size_table_3
            np.fromfile(fid, np.uint8, count=1, offset=1)
            np.fromfile(fid, np.short, count=1)
            np.fromfile(fid, np.int8, count=1)
            np.fromfile(fid, np.short, count=1)
            np.fromfile(fid, np.short, count=1)  # hardware_size
            np.fromfile(fid, np.int8, count=1)
            np.fromfile(fid, np.short, count=1)
            self.sample_rate = np.fromfile(fid, np.short, count=1)
            np.fromfile(fid, np.short, count=1)  # trigger_mode
            np.fromfile(fid, np.short, count=1)  # trigger_source
            np.fromfile(fid, np.short, count=1)  # pre-trigger
            np.fromfile(fid, np.short, count=1)
            self.max_voltage = np.fromfile(fid, np.short, count=1)
            np.fromfile(fid, np.short, count=1)

        np.fromfile(fid, np.short, count=1)  # size_table_4
        np.fromfile(fid, np.uint8, count=1)
        np.fromfile(fid, np.int8, count=5)
        for i in range(self.number_of_channels):
            np.fromfile(fid, np.int8, count=2)

        # ADDITIONAL HEADER INFO INCLUDED FROM VERSION AEWIN v1.53 ONWARDS
        if s_ver > 1.53:
            np.fromfile(fid, np.short, count=1)  # size_table_5
            np.fromfile(fid, np.uint8, count=1)
            np.fromfile(fid, np.int8, count=5)
            for i in range(self.number_of_channels):
                np.fromfile(fid, np.int8, count=2)

        # table 5
        if s_ver > 1.53:
            np.fromfile(fid, np.short, count=1)  # size_table_5 (also)
            np.fromfile(fid, np.uint8, count=1)
            np.fromfile(fid, np.int8, count=5)
            for i in range(self.number_of_channels):
                np.fromfile(fid, np.int8, count=7)

        # msg 137 filter
        for i in range(self.number_of_channels):
            length = int(np.fromfile(fid, np.short, count=1))
            np.fromfile(fid, np.uint8, count=1)
            np.fromfile(fid, np.int8, count=length-1)

        # masg 146 digital filter
        for i in range(self.number_of_channels):
            length = int(np.fromfile(fid, np.short, count=1))
            np.fromfile(fid, np.uint8, count=1)
            np.fromfile(fid, np.int8, count=length-1)

        # Table 6
        size_table_6 = int(np.fromfile(fid, np.short, count=1))
        np.fromfile(fid, np.uint8, count=1)
        self.time_stamp = np.str(fid.read(size_table_6-1))

        # Table 7
        np.fromfile(fid, np.short, count=1)  # size table 7
        np.fromfile(fid, np.uint8, count=1)

        # Table 8
        np.fromfile(fid, np.short, count=1)  # size table 8
        np.fromfile(fid, np.uint8, count=1)
        np.fromfile(fid, np.short, count=3)

        self.length_of_header = fid.tell()
        fid.close()


class ReadWaveforms:
    """
    Reads Voltage Values from wsf file
    """
    def __init__(self, path_name, file_name):
        self.data = dict()
        path = path_name + file_name
        header = ReadPci2Header(path)
        # todo - need to take preamp and front-end gain into account
        voltage_scale = 1000 * header.max_voltage/32767  # Convert the scale to mV

        self.fs = header.sample_rate*1e3
        # deltat_ms = 1.0 / header.sample_rate;	# deltat is the sampling interval in ms.

        fid = open(path, 'rb')
        fid.seek(header.length_of_header)

        np.fromfile(fid, np.short, count=1)  # msg_length
        fid.read(1)  # mid
        fid.read(1)  # sid
        np.fromfile(fid, np.short, count=1)  # mver
        np.fromfile(fid, np.short, count=1)  # n_channels
        # trig_time_us = []
        sample_start = []
        for i in range(header.number_of_channels):
            np.fromfile(fid, np.uint8, count=1)  # channel list[i]
            np.fromfile(fid, np.uint32, count=1)  # trigtime0_1[i]
            np.fromfile(fid, np.ushort, count=1)  # trigtime2[i]
            # trig_time_us[i] = ((4294967296.0 * trig_time_1) + trig_time_0) / 4
            sample_start.append(np.fromfile(fid, np.int64, count=1))

        waveform_index = dict()
        for i in range(header.number_of_channels):
            msg_length = np.fromfile(fid, np.short, count=1)
            fid.read(1)  # mid
            fid.read(1)  # sid
            np.fromfile(fid, np.short, count=1)  # mver
            np.fromfile(fid, np.uint32, count=1)  # sync
            chan_num = np.fromfile(fid, np.uint32, count=1)
            np.fromfile(fid, np.int64, count=1)  # fifowrite
            fifo_readm = np.fromfile(fid, np.uint32, count=1)
            fifo_readl = np.fromfile(fid, np.uint32, count=1)
            fifo_read = (fifo_readm*4294967296.0)+fifo_readl
            n_samples = int((msg_length - 28)/2)
            offset = int(sample_start[i] - (2*fifo_read))
            chunk = np.fromfile(fid, np.short, count=n_samples)
            self.data[int(chan_num)] = chunk[offset: n_samples+1] * voltage_scale
            waveform_index[int(chan_num)] = (n_samples - offset)

        n_chunks = 0
        msg_length = np.fromfile(fid, np.short, count=1)
        while msg_length.size > 0:
            if msg_length != 2076:
                fid.seek(int(msg_length), 1)
            else:
                fid.read(1)  # mid
                fid.read(1)  # sid
                np.fromfile(fid, np.short, count=1)  # mver
                np.fromfile(fid, np.uint32, count=1)  # sync
                chan_num = np.fromfile(fid, np.uint32, count=1)
                np.fromfile(fid, np.int64, count=1)  # fifowrite
                np.fromfile(fid, np.uint32, count=1)  # fifo_readm
                np.fromfile(fid, np.uint32, count=1)  # fifo_readl
                # fifo_read = (fifo_readm * 4294967296.0) + fifo_readl
                try:
                    n_samples = int((int(msg_length) - 28) / 2)
                    chunk = np.fromfile(fid, np.short, count=n_samples)
                    self.data[int(chan_num)] = np.append(self.data[int(chan_num)],
                                                         chunk[0: n_samples + 1] * voltage_scale)
                    waveform_index[int(chan_num)] = waveform_index[int(chan_num)] + n_samples
                    n_chunks += 1
                except TypeError:
                    pass

            msg_length = np.fromfile(fid, np.short, count=1)

        # n_chunks = n_chunks /number of channels
        fid.close()


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    pathname = '/Users/rmr327/Downloads/'
    filename = 'STREAM20200206-181826-468.wfs'
    data = ReadWaveforms(pathname, filename)

    plt.plot(data.data[1])
    plt.xlabel('Sample Number')
    plt.ylabel('Amplitude (mv)')
    plt.show()
