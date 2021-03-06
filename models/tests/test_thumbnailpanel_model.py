"""test_thumbnailpanel_model.py - tests the thumbnailpanel_model module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
import models.thumbnailpanel_model as model
from utils.skiptest import skipIfModuleNotInstalled
import h5py
from matplotlib.figure import Figure
import numpy as np
import wx
import hashlib
from multiprocessing import Process, Pipe, freeze_support
import os
import unittest
import random
import StringIO


class TestThumbnailPanelModel(unittest.TestCase):
    """Tests the thumbnailpanel model functions"""

    def setUp(self):
        random_data = [random.uniform(-100, 100) for i in range(25)]
        self.sample_data = np.array(random_data)
        self.sample_data_file = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "sample.dat"))
        #np.savetxt(self.sample_data_file, self.sample_data)
        with h5py.File(self.sample_data_file, 'w') as fidout:
            fidout.create_dataset(os.path.basename(self.sample_data_file), data=self.sample_data)

    def test_create_plot(self):
        """Verify plot function returns a matplotlib Figure"""
        self.assertTrue(isinstance(model.create_plot(self.sample_data,
                                                     title="Plot Title",
                                                     width=3, height=3),
                                   Figure))

    def test_plot_stream(self):
        """Verify plot_stream function returns a StringIO StringIO instance"""
        self.assertTrue(isinstance(model.plot_stream(self.sample_data,
                                                     title="Plot Title",
                                                     width=5, height=5),
                                   StringIO.StringIO))
    @skipIfModuleNotInstalled("tcunittest")
    def test_plot_pipe(self):
        """Verify plot_pipe function writes a StringIO instance of the
        plot to a specified multiprocess Pipe.
        """
        in_conn, out_conn = Pipe()
        plot_proc = Process(target=model.plot_pipe,
                            args=(self.sample_data, os.path.basename(self.sample_data_file)),
                            kwargs={'width': 7, 'height': 2, 'pipe': out_conn})
        plot_proc.start()
        img_stream = in_conn.recv()
        plot_proc.join()
        self.assertTrue(isinstance(img_stream, StringIO.StringIO))

    @skipIfModuleNotInstalled("tcunittest")
    def test_multiprocess_plot(self):
        """Verify multiprocess_plot function returns a wx Bitmap instance"""
        app = wx.PySimpleApp()
        plot_bmp = model.multiprocess_plot(self.sample_data_file, width=10,
                                           height=19)
        self.assertTrue(isinstance(plot_bmp, wx.Bitmap))

    def test_gen_thumbnail(self):
        """Verify gen_thumbnail function returns a wx Bitmap instance"""
        app = wx.PySimpleApp()
        img_stream = model.plot_stream(self.sample_data, "Plot Title", width=14, height=11)
        plot_bmp = model.gen_thumbnail(img_stream, self.sample_data_file)
        self.assertTrue(isinstance(plot_bmp, wx.Bitmap))

    def test_thumbnail_name(self):
        """Verify thumbnail_name function returns the proper thumbnail filename"""
        m = hashlib.md5(self.sample_data_file)
        expected_thumb_name = os.path.join(pathfinder.thumbnails_path(), m.hexdigest() + '.png')
        self.assertEqual(expected_thumb_name, model.thumbnail_name(self.sample_data_file))

    def tearDown(self):
        if os.path.exists(self.sample_data_file):
            os.remove(self.sample_data_file)
        thumbnail_name = model.thumbnail_name(self.sample_data_file)
        if os.path.exists(thumbnail_name):
            os.remove(thumbnail_name)


if __name__ == "__main__":
    freeze_support()
    random.seed()
    unittest.main()