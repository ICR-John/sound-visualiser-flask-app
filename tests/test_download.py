import glob
import os
import shutil
import sqlite3
import unittest
from Test_Audio.download_sounds import download_MIS_zip, download_NSynth_zip
from data.data_entry import insert_instrument, insert_sound, get_data


class TestInsertInstrument(unittest.TestCase):
    """Tests the function Insert Instrument"""

    @classmethod
    def setUpClass(cls):
        # Connects to the database
        cls.conn = sqlite3.connect("../data/example_test.sqlite")

    def test_a_insert(self):
        # Tests whether the function can insert data into instrument table
        data = ["test_name1", "family_1"]
        insert_instrument("../data/example_test.sqlite", data[0], data[1])
        instrument = self.conn.execute("Select * From Instruments where name = ?", (data[0],))
        instrument = list(instrument.fetchall()[0])
        self.assertEqual(data[0:1], instrument[2:3])

    def test_b_duplicate_name(self):
        # Tests if there will be duplicate instruments which shouldn't happen
        data = ["test_name1", "family_2"]
        insert_instrument("../data/example_test.sqlite", data[0], data[1])
        instrument = self.conn.execute("Select * From Instruments where name = ?", (data[0],))
        instrument = instrument.fetchall()
        self.assertEqual(len(instrument), 1)


class TestInsertSound(unittest.TestCase):
    """Tests the function Insert Sound"""
    @classmethod
    def setUpClass(cls):
        # Connects to the database
        cls.conn = sqlite3.connect("../data/example_test.sqlite")

    def test_a_insert(self):
        # Tests whether the function can insert data into sound table
        data = ["test_name1", "test_name1", "recording", "note"]
        insert_sound("../data/example_test.sqlite", data[0], data[1], data[2], data[3])
        sounds = self.conn.execute("Select * From Sounds where name = ?", (data[0],))
        sounds = list(sounds.fetchall()[0])
        self.assertEqual(sounds[1], data[0])

    def test_b_correct_instrument(self):
        # Tests if the sound has a correct instrument name
        data = ["test_name2", "a", "recording", "note"]
        insert_sound("../data/example_test.sqlite", data[0], data[1], data[2], data[3])
        sounds = self.conn.execute("Select * From Sounds where name = ?", (data[0],))
        self.assertEqual(len(sounds.fetchall()), 0)

    def test_c_duplicate_name(self):
        # Tests if there will be duplicate sounds which shouldn't happen
        data = ["test_name1", "test_name1", "recording", "note"]
        insert_sound("../data/example_test.sqlite", data[0], data[1], data[2], data[3])
        sounds = self.conn.execute("Select * From Sounds where name = ?", (data[0],))
        self.assertEqual(len(sounds.fetchall()), 1)

    @classmethod
    def tearDownClass(cls):
        # Deletes the test entries in the tables
        cls.conn = sqlite3.connect("../data/example_test.sqlite")
        cls.conn.execute("Delete From Instruments where name like '%test_name%'")
        cls.conn.execute("Delete From Sounds where name like '%test_name%' ")
        cls.conn.commit()


class TestGetData(unittest.TestCase):
    """Tests the Get Data Function"""
    @classmethod
    def setUpClass(cls):
        # Gets example_test information to test the function
        cls.MIS_info = get_data("Strings")[0]
        cls.Nsynth_info = get_data("Strings")[25]

    def test_a_instrument(self):
        # Tests whether the instrument name is correct
        self.assertEqual("Cello", self.MIS_info[3])

    def test_b_note(self):
        # Tests whether the note is correct
        self.assertEqual("A2", self.MIS_info[4])

    def test_c_filename(self):
        # Tests whether the filename is correct
        self.assertEqual("Cello.arco.ff.sulC.A2.stereo", self.MIS_info[2])

    def test_d_recording(self):
        # Test whether the recording name is correct
        self.assertEqual("..\\Test_Audio\\Strings\\Cello\\Cello.arco.ff.sulC.A2.stereo.aif",
                         self.MIS_info[1])

    def test_e_Nsynth_note(self):
        # Tests if the the Nsynth midi pitch is properly converted
        self.assertEqual("A#0", self.Nsynth_info[4])


class TestMISDownload(unittest.TestCase):
    """Tests the function Download MIS Zip"""
    @classmethod
    def setUpClass(cls):
        # Runs the function
        download_MIS_zip("http://theremin.music.uiowa.edu/MIS-Pitches-2012/MISBells2012.html")

    def test_folders(self):
        # Tests whether the data is in the correct folder group
        self.assertIn("Percussion", os.listdir("../Tests"))

    def test_instrument(self):
        # Tests if the name of the instrument is correct
        self.assertIn("Bells", os.listdir("../Tests/Percussion"))

    def test_delete_zip(self):
        # Tests if it deletes the zip folder
        self.assertEqual(len(glob.glob("../Tests/Percussion/*.zip")), 0)

    @classmethod
    def tearDownClass(cls):
        # Deletes the folder
        shutil.rmtree("../Tests/Percussion")


if __name__ == '__main__':
    unittest.main()
