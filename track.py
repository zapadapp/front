import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image, ImageTk
import os
from threading import Thread
import time
import pyaudio
from queue import Queue
import shutil

# solve local imports
import sys
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
WORKSPACE = os.path.dirname(FILE_PATH)
PARSER_PATH = os.path.join(WORKSPACE, "input_parser")

sys.path.insert(0, WORKSPACE)
from input_parser import recorder

PATH = os.path.dirname(os.path.realpath(__file__))

class Track():
    def __init__(self, track_frame, id_track):
        super().__init__()

        self.audio = pyaudio.PyAudio()
        self.id = id_track
        self.master_frame = track_frame
        self.note_switch_var = customtkinter.StringVar(value="chord") 

        self.track_label =customtkinter.CTkLabel(master=self.master_frame,text="Track #{}".format(self.id),text_color="white",text_font="Arial")
        self.track_label.grid(row=0, column=0, columnspan=1, sticky="nwse")
        self.combobox_1 = customtkinter.CTkComboBox(master=self.master_frame,
                                                    values=[ "Device 1", "Device 2"], command=self.combobox_func)
        self.combobox_1.grid(row=0, column=1, columnspan=2, pady=10, padx=20, sticky="nw")

        self.note_switch = customtkinter.CTkSwitch(master=self.master_frame,text="Note/Chord Detection",
                                   variable=self.note_switch_var, onvalue="chord", offvalue="note")
        self.note_switch.grid(row=0, column=2, columnspan=1, pady=10, padx=20, sticky="ne")

        self.note_switch.deselect()
        self.combobox_1.set("Select device")

        image = Image.open(FILE_PATH + "/img/score.png").resize((500, 200))
        #shutil.copy2(PATH +"/img/score.png", PATH + "/tmp/")
        self.bg_image = ImageTk.PhotoImage(image)

        self.image_label = customtkinter.CTkLabel(master=self.master_frame, image=self.bg_image)
        self.image_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.image_label.grid(row=1, column=0, columnspan=2, pady=10, padx=20, sticky="nwse")

        recordImg = ImageTk.PhotoImage(Image.open("img/record.png"))
        stopImg = ImageTk.PhotoImage(Image.open("img/stop.png"))
        saveImg = ImageTk.PhotoImage(Image.open("img/save.png"))
        self.deviceChoice = 0
        self.recButton = customtkinter.CTkButton(master=self.master_frame, image=recordImg, text="", command=self.record_action)
        self.recButton.grid(row=2, column=0, columnspan=1, pady=20, padx=20, sticky="nwse")

        self.stopButton = customtkinter.CTkButton(master=self.master_frame, image=stopImg, text="", command=self.stop_action)
        self.stopButton.grid(row=2, column=1, columnspan=1, pady=20, padx=20, sticky="nwse")
 
        self.saveButton = customtkinter.CTkButton(master=self.master_frame, image=saveImg, text="",command=self.save_score)
        self.saveButton.grid(row=2, column=2, columnspan=1, pady=20, padx=20, sticky="nwse")
       
        self.note_label =customtkinter.CTkLabel(master=self.master_frame,text="Acordes/Notas",text_color="white",text_font="Arial")
        self.note_label.grid(row=1, column=2, columnspan=1, pady=20, padx=20, sticky="nwse")
        
       
    def show_track(self,x):
        self.master_frame.grid(row=x, column=0, sticky="nwe", padx=5, pady=5)
        self.get_devices()

    def hide_track(self):
        self.master_frame.grid_forget()

    def combobox_func(self, choice):
        if choice == "Select device":
            return

        s = choice.split("#")
        self.deviceChoice = int(s[1])

    def get_devices(self):
        info = self.audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        newValues = []
        # show all input devices found.
        # print("Input Device id ", i, " - ", self.audio.get_device_info_by_host_api_device_index(0, i).get('name'))

        for i in range(0, numdevices):
            if (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                newValues.append("{} #{}".format(self.audio.get_device_info_by_host_api_device_index(0, i).get('name'),i))

        self.combobox_1.configure(values= newValues)        

    def record_action(self):
        self.cleanScore()
        self.note_q = Queue() 
        self.rec = recorder.Recorder("file{}.wav".format(self.id), "score{}".format(self.id))
        self.rec.setup(self.deviceChoice)

        noteThread = Thread(target = self.show_note)
        noteThread.start()

        recorderThread = Thread(target = self.rec.record, args =(self.note_q, self.note_switch_var.get()))
        recorderThread.start()

        imgUpdater = Thread(target = self.refresh_score, args = ())
        imgUpdater.start()

    def stop_action(self):    
        print("stop button")
        self.rec.reproduce()
        self.rec.stop()
        self.rec.close()

    def refresh_score(self):
        while True:
            try:
                image = Image.open(FILE_PATH + "/tmp/score{}.png".format(self.id)).resize((500, 200))
                self.bg_image = ImageTk.PhotoImage(image)

                self.image_label.configure(image=self.bg_image)
                self.image_label.image = image
            except OSError as e:
                # we do not care about this error so we just continue
                continue
        
            time.sleep(0.1)        

    def show_note(self):
        while True:
            note = self.note_q.get()
            self.note_label.configure(text="Played note: {}".format(note))
    
    def save_score(self):
        shutil.copy2(os.path.join(FILE_PATH, "tmp/score{}.png".format(self.id)), os.path.join(FILE_PATH,"files/score_{}_{}.png".format(self.id, time.time())))
        #shutil.copy2(PATH +"/img/score{}.png".format(self.id), PATH + "/tmp/")
        self.cleanScore()
       
    def cleanScore(self):
        try:
            os.remove(os.path.join(FILE_PATH, "tmp/score{}.png".format(self.id)))
        except OSError as e:
            print("could not delete score file")

        image = Image.open(FILE_PATH + "/img/score.png").resize((500, 200), Image.ANTIALIAS)
        self.bg_image = ImageTk.PhotoImage(image)

        self.image_label.configure(image=self.bg_image)  