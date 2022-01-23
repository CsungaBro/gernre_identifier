#import the pyplot and wavfile modules 
from genericpath import exists
import matplotlib.pyplot as plot
from scipy.io import wavfile
from pydub import AudioSegment
import os
import re
import random
import pandas as pd
import time
import logging
import sys
import smtplib, ssl

class Email_sender:
    def __init__(self):
        self.port = 465  # For SSL
        self.smtp_server = "smtp.gmail.com"
        self.sender_email = "csunga.python.mail"  # Enter your address
        self.receiver_email = "ujvari.csenger@gmail.com"  # Enter receiver address
        self.password = input("Type your password and press enter: ")
    
    def send_mail(self,message):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, self.receiver_email, message)


class Imput_Generator:
    def __init__(self, mode="production"):
        self.mode = mode
        if self.mode == "production":
            self.audio_path = "/home/vikichan/Documents/ta_labor/fma_small"
            self.image_path = "all_files"
            self.tracks_path = "tracks_prep3.csv"
            self.genre_path = "genres_prep.csv"
        elif self.mode == "test":
            self.audio_path = "/home/vikichan/Documents/ta_labor/tester/tester/small"
            self.image_path = "/home/vikichan/Documents/ta_labor/tester/tester/all_files"
            self.tracks_path = "/home/vikichan/Documents/ta_labor/tester/tracks_prep3.csv"
            self.genre_path = "/home/vikichan/Documents/ta_labor/tester/genres_prep.csv"

class Formatter(logging.Formatter):
    def format(self, record):
        def_format = '%(name)s - %(levelname)s - %(message)s'
        if record.levelno == logging.DEBUG:
            self._style._fmt = wrapper(def_format,"\_/")
        elif record.levelno == logging.INFO:
            self._style._fmt = wrapper(def_format,"-")
        elif record.levelno == logging.ERROR:
            self._style._fmt = wrapper(def_format,"-|-")
        else:
          self._style._fmt = "%(levelname)s: %"
        return super().format(record)

def wrapper(mess,sim):
  char_mul = int(66 / len(sim))
  return sim*char_mul+"\n"+ mess+ "\n"+ sim*char_mul


class Main:
    def __init__(self,audio_path,image_path,tracks_path,genre_path):
        self.audio_path = audio_path
        self.image_path = image_path
        self.tracks = pd.read_csv(tracks_path, dtype="string")
        self.genres = pd.read_csv(genre_path, dtype="string")
        self.onlyfiles = len([os.path.join(dp, f) for dp, dn, filenames in os.walk(self.audio_path) for f in filenames if os.path.splitext(f)[1] == '.mp3'])
        self.files_converted = 0
        self.new_files_converted = 0
        self.WANTED_X_SIZE = 2 # in s
        self.X_LENGTH = 30 # in s
        self.Y_INCH_SIZE = 2 #in inch
        self.X_INCH_SIZE = 2 #in inch
        self.DPI = 128 #in pixel
        self.WANTED_NUM_OF_FILES = int(self.X_LENGTH/self.WANTED_X_SIZE)
        self.start_time = time.time()
        self.last_time = time.time()
        self.main()

    

    def image_maker(self,in_path,final_path):
        out_path = os.path.basename(os.path.basename(in_path))
        out_path_wav = re.sub(".mp3",".wav",out_path)
        out_path_png = re.sub(".mp3",".png",out_path)

        file_names = [re.sub(".wav","_{}.png".format(x+1),out_path_wav) for x in range(self.WANTED_NUM_OF_FILES)]
        files_exist = [file for file in file_names if os.path.exists(os.path.join(final_path,file))]

        if not os.path.exists(os.path.join(final_path,file_names[-1])):
            # convert wav to mp3                                                            
            audSeg = AudioSegment.from_mp3(in_path)
            audSeg = audSeg.set_channels(1)
            audSeg.export(out_path_wav, format="wav")

        if len(files_exist) != len(file_names):
            sampling_frequency, signal_data = wavfile.read(out_path_wav)
            len_of_signal_data = len(signal_data)
            wanted_signal_len = int(len_of_signal_data/(self.X_LENGTH/self.WANTED_X_SIZE))

            for counter,file in enumerate(file_names):
                x_data = signal_data[counter:wanted_signal_len*(counter+1)]
                plot.figure(figsize=(self.X_INCH_SIZE,self.Y_INCH_SIZE),dpi=self.DPI)
                plot.specgram(x_data,Fs=sampling_frequency,cmap='gray')

                plot.axis('off')
                plot.ylim([0,22000])

                plot.savefig(os.path.join(final_path,file),pad_inches=0,bbox_inches='tight')
                plot.clf()
            os.remove(out_path_wav)  


            self.new_files_converted += 1
            self.files_converted += 1
            to_log =  "Converted:{}. {} out of {} file is converted".format(out_path_wav,self.files_converted,self.onlyfiles)
            to_log += "\n"+"New Files Converted:{}".format(self.new_files_converted)
            to_log += "\n"+"Time elapsed from the last conversion: {}".format(time.time()-self.last_time)
            to_log += "\n"+"--- {} seconds ---".format(time.time() - self.start_time)
            # logger.info("Converted:{}. {} out of {} file is converted".format(out_path_wav,self.files_converted,self.onlyfiles))
            # logger.info("New Files Converted:{}".format(self.new_files_converted))
            # logger.info("Time elapsed from the last conversion: {}".format(time.time()-self.last_time))
            self.last_time = time.time()
            # logger.info("--- %s seconds ---" % (time.time() - self.start_time))
            logger.info(to_log)
        else:
            to_log =  "{} already exists".format(out_path_png)
            to_log += "\n"+"Converted:{}. {} out of {} file is converted".format(out_path_wav,self.files_converted,self.onlyfiles)
            # logging.debug(to_log)
            self.files_converted += 1
            # logger.info("{} already exists".format(out_path_png))
            # logger.info("Converted:{}. {} out of {} file is converted".format(out_path_wav,self.files_converted,self.onlyfiles))
    
    def genre_checker(self,file):
        file_name = re.sub(".mp3","",file)
        file_name = re.sub("^0*","",file_name)
        logger.debug(file_name)
        track = self.tracks[self.tracks["track_id"] == file_name]
        logger.debug("track: {}".format(track))
        track_id = track["genres"].values[0]
        track_id = re.sub(",.*","",track_id)
        logger.debug("track_id: {}".format(track_id))
        if track_id != "0":
            genre_id = self.genres[self.genres["genre_id"] == track_id]
            logger.debug("genre_id: {}".format(genre_id))
            genre_id = genre_id["top_level"].values[0]
        else:
            genre_id = 0
        return genre_id

    def folder_maker(self,list_of_files,dir_path):
        for file in list_of_files:
            genre = self.genre_checker(file)
            if genre != 0:
                genre_path = os.path.join(self.image_path,genre)
                if not os.path.exists(genre_path):
                    os.mkdir(genre_path)
                if self.new_files_converted > 30:
                    self.image_maker(os.path.join(dir_path,file),genre_path)
                else:
                    self.image_maker(os.path.join(dir_path,file),genre_path)
            else:
                os.remove(os.path.join(dir_path,file))
                logger.error("{} file was removed".format(file))
            

    def main(self):
        list_of_dirs = os.listdir(self.audio_path)
        for direc in list_of_dirs:
            if os.path.isdir(os.path.join(self.audio_path,direc)):
                dir_path = os.path.join(self.audio_path,direc)
                list_of_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
                self.folder_maker(list_of_files,dir_path)
            

if __name__ == '__main__':
    # tracker = SummaryTracker()

    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(Formatter())
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    es = Email_sender()
    IG = Imput_Generator(mode = "production")
    try:
        M = Main(IG.audio_path,IG.image_path,IG.tracks_path,IG.genre_path)
    except:
        message = f"Error in Main: {sys.exc_info()[0]}"
        print(message)
        es.send_mail(str(message))

    # tracker.print_diff()