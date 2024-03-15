""" Created by Ahmed Mohamud """

import glob
import os
import sqlite3
import pretty_midi


def get_data(group):
    """Gets the data from the sounds in the Test_Audio folder
     to place into database"""
    info = []
    path = "..\\Test_Audio\\" + group
    # Gets a list of instruments in the folder
    instruments = os.listdir(path)
    for i in instruments:
        for j in glob.glob(path + "\\" + i + "\\*.aif") or glob.glob(path + "\\" + i + "\\*.wav"):
            filename = j.split("\\")[4]
            recording = j
            # the .aif files come from the Iowa database
            if ".aif" in filename:
                filename = filename.strip(".aif")
                i_name = os.path.basename(os.path.dirname(j))
                note = filename.split(".")[-2]
            # The wav files come from NSynth
            if ".wav" in filename:
                i_name = filename.split("_")[1].capitalize() + " " + filename.split("_")[0].capitalize()
                filename = filename.strip(".wav")
                # Converts Midi Pitch into notes
                midi = filename.split("-")[1]
                note = pretty_midi.note_number_to_name(int(midi))
            info.append([group, recording, filename, i_name, note])
    return info


def insert_instrument(sqlite, instruments, family):
    """Inserts the Instrument data into Instrument table"""
    try:
        # Connects to the database
        conn = sqlite3.connect(sqlite)
        c = conn.cursor()
        # Checks whether Instrument is already there
        if len(c.execute("SELECT * FROM Instruments where name = ?", (instruments,)).fetchall()) == 0:
            c.execute("""INSERT INTO Instruments(name,family) VALUES (?,?) """, (instruments, family))
            conn.commit()
            c.close()
    # Error message if it doesn't insert
    except sqlite3.Error as error:
        print("Failed to insert data into Instruments", error)
    finally:
        if conn:
            conn.close()


def insert_sound(sqlite, sound_name, instrument_name, recording, note):
    """Inserts the Sound data into Sounds table"""
    try:
        # Connects to the database
        conn = sqlite3.connect(sqlite)
        c = conn.cursor()
        # Accounts for the foreign key
        conn.execute("PRAGMA foreign_keys = 1")
        try:
            # Checks for the Instrument id in Instrument table
            # with the same instrument name
            instrument_id = c.execute("""Select instrument_id from Instruments where name = ?""", (instrument_name,))
            instrument_id = instrument_id.fetchone()[0]
            # Checks whether Sound is already there
            if len(c.execute("SELECT * FROM Sounds where name = ?", (sound_name,)).fetchall()) == 0:
                c.execute("""INSERT INTO Sounds(name, recording, instrument_id,note) VALUES (?,?,?,?) """, (
                    sound_name, recording, instrument_id, note))
                conn.commit()
                c.close()
        # Error message if sound's instrument is not there
        except TypeError:
            print("Instrument doesnt exist")
    # Error message if it doesn't insert
    except sqlite3.Error as error:
        print("Failed to insert data into Sounds", error)

    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    groups = ["Brass", "Percussion", "Strings", "Woodwinds"]
    for i in groups:
        i_data = get_data(i)
        for j in i_data:
            insert_instrument("example.sqlite",j[3], j[0])
            insert_sound("example.sqlite",j[2], j[3], j[1], j[4])
