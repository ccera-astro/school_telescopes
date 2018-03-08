#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: School Telescope V1
# Generated: Wed Mar  7 18:39:15 2018
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr
import school_helper  # embedded python module
import threading
import time


class school_telescope_v1(gr.top_block):

    def __init__(self, expname="TESTING", freq=1420.4058e6, latitude=44.9, longitude=-76.03, lstore="/mnt/data/astro_data", rstore=''):
        gr.top_block.__init__(self, "School Telescope V1")

        ##################################################
        # Parameters
        ##################################################
        self.expname = expname
        self.freq = freq
        self.latitude = latitude
        self.longitude = longitude
        self.lstore = lstore
        self.rstore = rstore

        ##################################################
        # Variables
        ##################################################
        self.fftsize = fftsize = 2048
        self.samp_rate = samp_rate = int(6.0e6)
        self.probe_result = probe_result = [0.1]*fftsize
        self.log_status = log_status = school_helper.log(probe_result,longitude,latitude,lstore,rstore,expname,freq,samp_rate)
        self.frate = frate = int(samp_rate/fftsize)

        ##################################################
        # Blocks
        ##################################################
        self.fft_probe = blocks.probe_signal_vf(fftsize)
        self.single_pole_iir_filter_xx_0 = filter.single_pole_iir_filter_ff(1.0/(frate*10), fftsize)

        def _probe_result_probe():
            while True:
                val = self.fft_probe.level()
                try:
                    self.set_probe_result(val)
                except AttributeError:
                    pass
                time.sleep(1.0 / (1.0))
        _probe_result_thread = threading.Thread(target=_probe_result_probe)
        _probe_result_thread.daemon = True
        _probe_result_thread.start()

        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + 'airspy=0,pack=1' )
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(950e6, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(20, 0)
        self.osmosdr_source_0.set_if_gain(10, 0)
        self.osmosdr_source_0.set_bb_gain(10, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)

        self.fft_vxx_0 = fft.fft_vcc(fftsize, True, (window.blackmanharris(fftsize)), False, 1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fftsize)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_float*fftsize, frate*2)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(fftsize)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.single_pole_iir_filter_xx_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.fft_probe, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.single_pole_iir_filter_xx_0, 0), (self.blocks_keep_one_in_n_0, 0))

    def get_expname(self):
        return self.expname

    def set_expname(self, expname):
        self.expname = expname
        self.set_log_status(school_helper.log(self.probe_result,self.longitude,self.latitude,self.lstore,self.rstore,self.expname,self.freq,self.samp_rate))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.set_log_status(school_helper.log(self.probe_result,self.longitude,self.latitude,self.lstore,self.rstore,self.expname,self.freq,self.samp_rate))

    def get_latitude(self):
        return self.latitude

    def set_latitude(self, latitude):
        self.latitude = latitude
        self.set_log_status(school_helper.log(self.probe_result,self.longitude,self.latitude,self.lstore,self.rstore,self.expname,self.freq,self.samp_rate))

    def get_longitude(self):
        return self.longitude

    def set_longitude(self, longitude):
        self.longitude = longitude
        self.set_log_status(school_helper.log(self.probe_result,self.longitude,self.latitude,self.lstore,self.rstore,self.expname,self.freq,self.samp_rate))

    def get_lstore(self):
        return self.lstore

    def set_lstore(self, lstore):
        self.lstore = lstore
        self.set_log_status(school_helper.log(self.probe_result,self.longitude,self.latitude,self.lstore,self.rstore,self.expname,self.freq,self.samp_rate))

    def get_rstore(self):
        return self.rstore

    def set_rstore(self, rstore):
        self.rstore = rstore
        self.set_log_status(school_helper.log(self.probe_result,self.longitude,self.latitude,self.lstore,self.rstore,self.expname,self.freq,self.samp_rate))

    def get_fftsize(self):
        return self.fftsize

    def set_fftsize(self, fftsize):
        self.fftsize = fftsize
        self.set_frate(int(self.samp_rate/self.fftsize))
        self.set_probe_result([0.1]*self.fftsize)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_frate(int(self.samp_rate/self.fftsize))
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.set_log_status(school_helper.log(self.probe_result,self.longitude,self.latitude,self.lstore,self.rstore,self.expname,self.freq,self.samp_rate))

    def get_probe_result(self):
        return self.probe_result

    def set_probe_result(self, probe_result):
        self.probe_result = probe_result
        self.set_log_status(school_helper.log(self.probe_result,self.longitude,self.latitude,self.lstore,self.rstore,self.expname,self.freq,self.samp_rate))

    def get_log_status(self):
        return self.log_status

    def set_log_status(self, log_status):
        self.log_status = log_status

    def get_frate(self):
        return self.frate

    def set_frate(self, frate):
        self.frate = frate
        self.single_pole_iir_filter_xx_0.set_taps(1.0/(self.frate*10))
        self.blocks_keep_one_in_n_0.set_n(self.frate*2)


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "", "--expname", dest="expname", type="string", default="TESTING",
        help="Set Experiment Name [default=%default]")
    parser.add_option(
        "", "--freq", dest="freq", type="eng_float", default=eng_notation.num_to_str(1420.4058e6),
        help="Set Frequency [default=%default]")
    parser.add_option(
        "", "--latitude", dest="latitude", type="eng_float", default=eng_notation.num_to_str(44.9),
        help="Set Local Latitude [default=%default]")
    parser.add_option(
        "", "--longitude", dest="longitude", type="eng_float", default=eng_notation.num_to_str(-76.03),
        help="Set Local Longitude [default=%default]")
    parser.add_option(
        "", "--lstore", dest="lstore", type="string", default="/mnt/data/astro_data",
        help="Set Local Storage Location [default=%default]")
    parser.add_option(
        "", "--rstore", dest="rstore", type="string", default='',
        help="Set Remote Storage Location [default=%default]")
    return parser


def main(top_block_cls=school_telescope_v1, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(expname=options.expname, freq=options.freq, latitude=options.latitude, longitude=options.longitude, lstore=options.lstore, rstore=options.rstore)
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
