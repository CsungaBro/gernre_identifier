#import the pyplot and wavfile modules 
import matplotlib.pyplot as plot
from scipy.io import wavfile
from pydub import AudioSegment
import os
import re
import random
import pandas as pd
import time
import logging
from  sys import getsizeof 
# Read the wav file (mono)

# PATH = "/home/vikichan/Documents/ta_labor/fma_small/000/000010.mp3"
# PATH = "/home/vikichan/Documents/ta_labor/fma_small/000/"
# from pympler.tracker import SummaryTracker



class Imput_Generator:
    def __init__(self, mode="production"):
        self.mode = mode
        if self.mode == "production":
            self.audio_path = "fma_small"
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
        self.start_time = time.time()
        self.last_time = time.time()
        self.main()

    def image_maker(self,in_path,final_path):
        out_path = os.path.basename(os.path.basename(in_path))
        out_path_wav = re.sub(".mp3",".wav",out_path)
        out_path_png = re.sub(".mp3",".png",out_path)

        if not os.path.isfile(os.path.join(final_path,out_path_png)):
            # convert wav to mp3                                                            
            audSeg = AudioSegment.from_mp3(in_path)
            audSeg = audSeg.set_channels(1)
            # logger.debug("audioSeg size: {}".format(getsizeof(audSeg)))
            audSeg.export(out_path_wav, format="wav")
            sampling_frequency, signal_data = wavfile.read(out_path_wav)

            len_of_signal_data = len(signal_data)
            # Setting up the postprocessed data
            wanted_x_size = 2 # in s
            x_length = 30 # in s
            wanted_signal_len = len_of_signal_data/(x_length/wanted_x_size)
            y_inch_size = 2 #in inch
            x_inch_size = 2 #in inch
            dpi = 128 #in pixel

            for i in range(int(x_length/wanted_x_size)):
                x_data = signal_data[i:wanted_signal_len*(i+1)]
                curr_out_path_wav = f"{out_path_wav}_{i+1}" 
                plot.figure(figsize=(x_inch_size,y_inch_size),dpi=dpi)
                plot.specgram(x_data,Fs=sampling_frequency,cmap='gray')

                plot.axis('off')
                plot.ylim([0,22000])

                plot.savefig(re.sub(".wav",".png",os.path.join(final_path,curr_out_path_wav)),pad_inches=0,bbox_inches='tight')
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

    IG = Imput_Generator(mode = "production")
    M = Main(IG.audio_path,IG.image_path,IG.tracks_path,IG.genre_path)

    # tracker.print_diff()