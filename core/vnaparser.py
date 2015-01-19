# -*- coding: utf-8 -*-

from db.schema import ExpVNA
from db.schema import ExpSmith

class VNADataParser(object):
    def __init__(self, exp_id, filename):
        self._exp_id = exp_id
        self._filename = filename
        self._vna_properties = None
        self._vna_data = []

    @property
    def vna_data(self):
        return self._vna_data
    @property
    def vna_properties(self):
        return self._vna_properties

    def parse(self):
        file = open(self._filename)
        properties = {}

        while True:
            line = file.readline()
            if not line:
                break
            if line.startswith("\""):
                line = line.replace('"', '')
                arr = line.split(':')
                if len(arr) == 2:
                    properties[arr[0].replace(' ', '_').lower().strip()] = arr[1].strip()

            arr = line.split('\t')
            if len(arr) != 5:
                pass
            else:
                try:
                    freq = float(arr[0])
                    re = float(arr[1])
                    im = float(arr[2])
                    mem_re = float(arr[3])
                    mem_im = float(arr[4])
                    smith = ExpSmith(self._exp_id, freq, re, im, mem_re, mem_im)
                    self._vna_data.append(smith)
                except ValueError:
                    pass
        self._vna_properties = ExpVNA(
            self._exp_id,
            float(properties['if_bandwidth'].replace(' kHz', '')), 
            int(properties['number_of_points']), 
            properties['format_type'], 
            properties['sweep_type'], 
            int(properties['channel']), 
            float(properties['source_power'].replace(' dBm', '')), 
            properties['measure_type'], 
            float(properties['sweep_time'].replace(' ms', ''))
        )