""" Created by Ahmed Mohamud """

import glob
import urllib.request as request
from bs4 import BeautifulSoup
import re
import os
import zipfile
import shutil


def download_MIS_zip(url):
    """ Downloads the MIS data"""
    # Opens the url and downloads the zip file
    r = request.urlopen(url)
    soup = BeautifulSoup(r, "html.parser")
    file = soup.find(href=re.compile(r"/*.zip"))
    file_url = "http://theremin.music.uiowa.edu/" + file["href"].replace(" ", "%20").strip("../")
    name = file["href"].split("/")[4]
    instrument_type = file["href"].split("/")[3]
    try:
        # Makes a directory for the instrument type and puts the zip file there
        os.mkdir(instrument_type)
        zip_file = request.urlretrieve(file_url, os.path.abspath(instrument_type + "/" + name) + ".zip")[0]
    except FileExistsError:
        zip_file = request.urlretrieve(file_url, os.path.abspath(instrument_type + "/" + name) + ".zip")[0]
    # Extracts the zip file and puts the data in a folder with instrument name
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(instrument_type + "/" + name)
    # Deletes the zip file
    os.remove(zip_file)
    return


def download_NSynth_zip(url, instrument):
    """ Downloads the NSynth data"""
    # Opens the url and downloads the zip file
    r = request.urlopen(url)
    soup = BeautifulSoup(r, "html.parser")
    file = soup.find(href=re.compile(r"/nsynth/nsynth-test.jsonwav.tar.gz"))
    file_url = str(file['href'])
    zip_file = request.urlretrieve(file_url, os.path.abspath("Nsynth") + ".jsonwav.tar.gz")[0]
    # Extracts the zip file and deletes it
    shutil.unpack_archive(zip_file)
    os.remove(zip_file)
    # Moves specific Acoustic Guitar into the String folder
    # If String folder not there, it will make String folder
    for w_file in glob.glob("nsynth-test/audio/*.wav"):
        if instrument in w_file:
            if "50" in w_file.split("-")[3] and "10" in w_file.split("-")[1]:
                try:
                    os.mkdir("Strings")
                    os.mkdir("Strings/" + instrument)
                    shutil.move(w_file, "Strings/" + instrument)
                except FileExistsError:
                    shutil.move(w_file, "Strings/" + instrument)
    # Deletes the extra NSynth sounds
    shutil.rmtree("nsynth-test")
    return


if __name__ == '__main__':
    # List of instruments from MIS that will be downloaded
    instruments = ["AltoFlute", "Oboe", "Bassoon", "Bells", "Marimba", "Xylophone", "Horn"
        , "TenorTrombone", "Tuba", "Violin", "Cello"]
    download_NSynth_zip("https://magenta.tensorflow.org/datasets/nsynth", "guitar_acoustic")
    for i in instruments:
        url = "http://theremin.music.uiowa.edu/MIS-Pitches-2012/MIS" + i + "2012.html"
        download_MIS_zip(url)

