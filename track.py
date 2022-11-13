import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image, ImageTk
import os
from threading import Thread
import time
from datetime import datetime
import pyaudio
from queue import Queue
import shutil
import turtle

# solve local imports
import sys

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
WORKSPACE = os.path.dirname(FILE_PATH)
PARSER_PATH = os.path.join(WORKSPACE, "input_parser")

sys.path.insert(0, WORKSPACE)
from input_parser import recorder, drawer

PATH = os.path.dirname(os.path.realpath(__file__))

class Track():
    def __init__(self, track_frame, id_track):
        super().__init__()

        self.audio = pyaudio.PyAudio()
        self.id = id_track
        self.master_frame = track_frame
        self.note_switch_var = customtkinter.StringVar(value="chord")
        self.flute_switch_var = customtkinter.StringVar(value="on")
        self.showingNote = False

        self.info_subframe = customtkinter.CTkFrame(master=self.master_frame)
      
        self.info_subframe.grid(row=0, column=0, sticky='nwse')

        self.track_label =customtkinter.CTkLabel(master=self.info_subframe,text="Track #{}".format(self.id),text_color="white",text_font="Arial")
        self.track_label.grid(row=0, column=1, sticky="nwse")
        self.combobox_1 = customtkinter.CTkComboBox(master=self.info_subframe,
                                                    values=[ "Device 1", "Device 2"], command=self.combobox_func)
        self.combobox_1.grid(row=0, column=2)

        self.combobox_1.set("Elegir dispositivo")

        # image = Image.open(FILE_PATH + "/img/score.png").resize((500, 200))
        # self.bg_image = ImageTk.PhotoImage(image)

        # self.image_label = customtkinter.CTkLabel(master=self.master_frame, image=self.bg_image)
        # self.image_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        # self.image_label.grid(row=2, column=0, columnspan=2, pady=10, sticky="nwse")
        
        canvas_w = 1600
        canvas_h = 300
        self.score_canvas = turtle.ScrolledCanvas(self.master_frame,width = canvas_w, height = canvas_h)
        #screen = turtle.TurtleScreen(self.score_canvas)
        self.score_canvas.grid(row=1, column=0, columnspan=2, pady=10, sticky="nwse")
        # t = turtle.Turtle(screen)

        self.score_screen = turtle.TurtleScreen(self.score_canvas)
        self.score_screen.delay(0)
        self.score_screen.screensize(canvas_w+5000,canvas_h+10000) #added by me
        t = turtle.RawTurtle(self.score_screen)
        t2 = turtle.RawTurtle(self.score_screen)
        self.scoreDrawer = drawer.Drawer(t, t2, canvas_w, canvas_h)

        self.check_var = customtkinter.StringVar(value="on") 

        checkbox = customtkinter.CTkCheckBox(master=self.info_subframe, text="",
                                     variable=self.check_var, onvalue="on", offvalue="off")

        checkbox.grid(row=0, column=0)
        
        self.note_label =customtkinter.CTkLabel(master=self.info_subframe,text="Nota tocada:",text_color="white",text_font="Arial")
        self.note_label.grid(row=0, column=6,  sticky="nwse")

        self.note_switch = customtkinter.CTkSwitch(master=self.info_subframe,text="Nota/Acorde",
                                   variable=self.note_switch_var, onvalue="chord", offvalue="note")
        self.note_switch.grid(row=0, column=7, pady=20, padx=15, sticky="nswe")

        self.note_switch.deselect()

        self.flute_switch = customtkinter.CTkSwitch(master=self.info_subframe,text="Mejorar mic",
                                   variable=self.flute_switch_var, onvalue="on", offvalue="off")
        self.flute_switch.grid(row=0, column=8, pady=20, padx=15, sticky="nswe")

        self.flute_switch.deselect()
        
       
    def show_track(self,x):
        self.master_frame.grid(row=x, column=0, sticky="nwe", padx=5, pady=5)
        self.get_devices()

    def hide_track(self):
        self.master_frame.grid_forget()

    def combobox_func(self, choice):
        if choice == "Elegir dispositivo":
            return

        s = choice.split("#")
        # self.deviceChoice = int(s[0])
        # self.channelChoice = int(s[2])
        self.deviceChoice = int(s[1])


    def get_devices(self):
        info = self.audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        newValues = []
        # show all input devices found.
        # print("Input Device id ", i, " - ", self.audio.get_device_info_by_host_api_device_index(0, i).get('name'))

        # func to detect channels
        # for i in range(0, numdevices):
        #     if (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0 and (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) < 4:
        #         for j in range(self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')):
        #             newValues.append("{}# {} - Channel #{}".format(i, self.audio.get_device_info_by_host_api_device_index(0, i).get('name'), j+1))

        for i in range(0, numdevices):
            if (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0: #and (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) < 4:
                #for j in range(self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')):
                newValues.append("{} #{}".format(self.audio.get_device_info_by_host_api_device_index(0, i).get('name'), i))

        self.combobox_1.configure(values= newValues)        

    def record_action(self):
        # we stop just in case user did not stop before starting to record again
        self.stop_action()
        self.cleanScore()
        self.note_q = Queue() 
        self.rec = recorder.Recorder("file{}.wav".format(self.id), "score{}".format(self.id))
        self.rec.setup(self.deviceChoice)
        
        self.showingNote = True
        self.noteThread = Thread(target = self.show_note)
        self.noteThread.start()

        noteSwitch = self.note_switch_var.get()
        fluteSwitch = False
        if self.flute_switch_var.get() == "on":
            fluteSwitch = True

        print("flute switch: {}".format(fluteSwitch))
        self.recorderThread = Thread(target = self.rec.record, args =(self.note_q, noteSwitch, self.scoreDrawer, fluteSwitch))
        self.recorderThread.start()

        #self.imgUpdater = Thread(target = self.refresh_score, args = ())
        #self.imgUpdater.start()

    def stop_action(self):    
        self.showingNote == False
        try:
            self.rec.stop()
            self.rec.close()
        except:
            print("")      

    def show_note(self):
        while self.showingNote == True:
            note = self.note_q.get()
            self.note_label.configure(text="Played note: {}".format(note))
    
    def save_score(self):
        now = datetime.now() # current date and time
        timestamp = now.strftime("%d%m%Y-%H%M%S")
        fileName = "score_{}".format(timestamp)
        try:
            os.mkdir(os.path.join("files",fileName))
        except:
            print("could not create path")    
        self.rec.saveScore(os.path.join("files",fileName,fileName))
        self.rec.saveMidi(fileName)
        # self.score_canvas.postscript(file=os.path.join("files","score_{}.ps".format(timestamp)), colormode='color')
        self.clearUnwantedFiles()
        self.cleanScore()
        return

    def play_score(self):
        self.rec.reproduce()    
       
    def cleanScore(self):
        # try:
        #     os.remove(os.path.join(FILE_PATH, "tmp/score{}.png".format(self.id)))
        # except OSError as e:
        #     print("could not delete score file")

        # image = Image.open(FILE_PATH + "/img/score.png").resize((500, 200), Image.ANTIALIAS)
        # self.bg_image = ImageTk.PhotoImage(image)

        # self.image_label.configure(image=self.bg_image)  
        self.scoreDrawer.clearScore()
        return

    def clearUnwantedFiles(self):
        for root, dirs, files in os.walk(os.path.join(FILE_PATH, "files"), topdown=False):
            for name in files:
                fileParts = os.path.splitext(name)
                if len(fileParts) == 2:
                    if ".png" != fileParts[1] and ".ps" != fileParts[1] and ".mid" != fileParts[1]:
                        try:
                            os.remove(os.path.join(root, name))
                        except OSError as e:
                            print("could not delete score file")

    def isSelected(self):
        return self.check_var.get() == "on"    