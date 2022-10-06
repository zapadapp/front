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
        self.showingNote = False

        self.info_subframe = customtkinter.CTkFrame(master=self.master_frame)
      
        self.info_subframe.grid(row=0, column=0, sticky='nwse')

        self.track_label =customtkinter.CTkLabel(master=self.info_subframe,text="Track #{}".format(self.id),text_color="white",text_font="Arial")
        self.track_label.grid(row=0, column=1, sticky="nwse")
        self.combobox_1 = customtkinter.CTkComboBox(master=self.info_subframe,
                                                    values=[ "Device 1", "Device 2"], command=self.combobox_func)
        self.combobox_1.grid(row=0, column=2)

        # self.note_switch = customtkinter.CTkSwitch(master=self.master_frame,text="Note/Chord",
        #                            variable=self.note_switch_var, onvalue="chord", offvalue="note")
        # self.note_switch.grid(row=0, column=2, pady=20, padx=15, sticky="nswe")

        # self.note_switch.deselect()
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
        self.score_screen.screensize(canvas_w+1000,canvas_h+500) #added by me
        t = turtle.RawTurtle(self.score_screen)
        t2 = turtle.RawTurtle(self.score_screen)
        self.scoreDrawer = drawer.Drawer(t, t2, canvas_w, canvas_h)

        self.check_var = customtkinter.StringVar(value="on") 

        checkbox = customtkinter.CTkCheckBox(master=self.info_subframe, text="", command=self.refresh_score,
                                     variable=self.check_var, onvalue="on", offvalue="off")

        checkbox.grid(row=0, column=0)
        # self.buttons_frame = customtkinter.CTkFrame(master=self.master_frame)
        # self.buttons_frame.rowconfigure((0), weight=1)
        # self.buttons_frame.columnconfigure((0,1,2,3), weight=5)
        # self.buttons_frame.grid(row=0, column=1, sticky="nwse")

        # recordImg = ImageTk.PhotoImage(Image.open("img/record.png").resize((40,40)))
        # stopImg = ImageTk.PhotoImage(Image.open("img/stop.png").resize((30,30)))
        # saveImg = ImageTk.PhotoImage(Image.open("img/save.png").resize((30,30)))
        # playImg = ImageTk.PhotoImage(Image.open("img/play.png").resize((30,30)))

        # self.deviceChoice = 0
        # self.recButton = customtkinter.CTkButton(master=self.buttons_frame, image=recordImg, fg_color="#353638", hover_color="#222325",
        #                                         width=50,height=50,text="", command=self.record_action)
        # self.recButton.grid(row=0, column=0,  sticky="nwse")

        # self.stopButton = customtkinter.CTkButton(master=self.buttons_frame, image=stopImg, fg_color="#353638", hover_color="#222325",
        #                                         width=50,height=50,text="", command=self.stop_action)
        # self.stopButton.grid(row=0, column=1, sticky="nwse")
 
        # self.saveButton = customtkinter.CTkButton(master=self.buttons_frame, image=saveImg, fg_color="#353638", hover_color="#222325",
        #                                         width=50,height=50,text="",command=self.save_score)
        # self.saveButton.grid(row=0, column=2, sticky="nwse")

        # self.playButton = customtkinter.CTkButton(master=self.buttons_frame, image=playImg, fg_color="#353638", hover_color="#222325",
        #                                         width=50,height=50,text="",command=self.play_score)
        # self.playButton.grid(row=0, column=3,  sticky="nwse")
       
        self.note_label =customtkinter.CTkLabel(master=self.info_subframe,text="Nota tocada:",text_color="white",text_font="Arial")
        self.note_label.grid(row=0, column=6,  sticky="nwse")
        
       
    def show_track(self,x):
        self.master_frame.grid(row=x, column=0, sticky="nwe", padx=5, pady=5)
        self.get_devices()

    def hide_track(self):
        self.master_frame.grid_forget()

    def combobox_func(self, choice):
        if choice == "Elegir dispositivo":
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

    def record_action(self, noteChordSwitch):
        self.cleanScore()
        self.note_q = Queue() 
        self.rec = recorder.Recorder("file{}.wav".format(self.id), "score{}".format(self.id))
        self.rec.setup(self.deviceChoice)
        
        self.showingNote = True
        self.noteThread = Thread(target = self.show_note)
        self.noteThread.start()

        self.recorderThread = Thread(target = self.rec.record, args =(self.note_q, noteChordSwitch, self.scoreDrawer))
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

    def refresh_score(self):
        # while True:
        #     try:
        #         image = Image.open(FILE_PATH + "/tmp/score{}.png".format(self.id)).resize((500, 200))
        #         self.bg_image = ImageTk.PhotoImage(image)

        #         self.image_label.configure(image=self.bg_image)
        #         self.image_label.image = image
        #     except OSError as e:
        #         # we do not care about this error so we just continue
        #         continue
        
        #     time.sleep(0.1)  
        return      

    def show_note(self):
        while self.showingNote == True:
            note = self.note_q.get()
            self.note_label.configure(text="Played note: {}".format(note))
    
    def save_score(self):
        self.rec.saveScore(os.path.join("files","new_score{}".format(time.time())))
        self.score_canvas.postscript(file=os.path.join("files","score{}.ps".format(time.time())), colormode='color')
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

    def isSelected(self):
        return self.check_var.get() == "on"    