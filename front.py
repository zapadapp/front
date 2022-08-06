import tkinter
import tkinter.messagebox
from tkinter import ttk, filedialog
from turtle import bgcolor
import customtkinter
from PIL import Image, ImageTk
import os
from threading import Thread
import time
import pyaudio
from queue import Queue
import shutil
import track


# solve local imports
import sys
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
WORKSPACE = os.path.dirname(FILE_PATH)

sys.path.insert(0, WORKSPACE)
from input_parser import recorder

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

PATH = os.path.dirname(os.path.realpath(__file__))

class App(customtkinter.CTk):

    WIDTH = 1024
    HEIGHT = 780

    def __init__(self):
        super().__init__()
        self.idTrack = 0
        self.tracks = []
        self.audio = pyaudio.PyAudio()
        self.title("zapadapp")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        # ============ frame_left ============

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        # self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
        #                                       text="ZAPADAPP",
        #                                       text_font=("Roboto Medium", -16))  # font name and size in px
        # self.label_1.grid(row=1, column=0, pady=10, padx=10)

        logoImg = Image.open(PATH + "/img/zapadapp-logo.jpeg").resize((160, 90))
        self.logo = ImageTk.PhotoImage(logoImg)

        self.logo_label = tkinter.Label(master=self.frame_left, image=self.logo)
        self.logo_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.logo_label.grid(row=1, column=0, pady=10, padx=10)


        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Play!",
                                                command=self.playBtnEvent)
        self.button_1.grid(row=2, column=0, pady=10, padx=20)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Saved",
                                                command=self.savedBtnEvent)
        self.button_2.grid(row=3, column=0, pady=10, padx=20)

        self.label_mode = customtkinter.CTkLabel(master=self.frame_left, text="Appearance Mode:")
        self.label_mode.grid(row=9, column=0, pady=0, padx=20, sticky="w")

        self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                        values=["Light", "Dark", "System"],
                                                        command=self.change_appearance_mode)
        self.optionmenu_1.grid(row=10, column=0, pady=10, padx=20, sticky="w")

        # ============ frame_right ============

        self.frame_right.rowconfigure(0, weight=0)
        self.frame_right.rowconfigure(1, weight=1)
        self.frame_right.columnconfigure(0, weight=1)
        #self.frame_right.columnconfigure((0, 1), weight=1)
        #self.frame_right.columnconfigure(2, weight=0)

        # saved_frame will be gridded when pressing Saved button
        self.saved_frame = customtkinter.CTkFrame(master=self.frame_right)

        # add_delete_frame will be gridded when pressing Play! button
        self.add_delete_frame = customtkinter.CTkFrame(master=self.frame_right)

        # tracks_frame will be gridded when pressing Play! button
        self.tracks_frame = customtkinter.CTkFrame(master=self.frame_right)
        

        self.tracks_canvas = customtkinter.CTkCanvas(master=self.tracks_frame,bg='#303030')
        self.tracks_canvas.grid(row=0,column=0,sticky='nwse')
        self.tracks_canvas.rowconfigure(0, weight=1)
        self.tracks_canvas.columnconfigure(0, weight=1)

        #### scrollbar

        self.scroll = ttk.Scrollbar(master=self.tracks_frame, orient='vertical', command=self.tracks_canvas.yview)
        self.scroll.grid(row=0,column=1,sticky='ns')
        self.tracks_canvas.configure(yscrollcommand=self.scroll.set)

        self.tracks_subframe = customtkinter.CTkFrame(master=self.tracks_canvas)
        self.tracks_subframe.grid(row=0, column=0, sticky='nwse')
        self.tracks_subframe.rowconfigure(0, weight=1)
        self.tracks_subframe.columnconfigure(0, weight=1)

        self.tracks_canvas.create_window((0,0), window=self.tracks_subframe, anchor='nw')

        self.tracks_subframe.update_idletasks()  

        self.addImgRaw = Image.open("img/add.png")
        self.addImg = ImageTk.PhotoImage(self.addImgRaw, Image.ANTIALIAS)

        self.addButton = customtkinter.CTkButton(master=self.add_delete_frame,image=self.addImg, text="",command=self.add_track)
        self.addButton.grid(row=0, column=0, columnspan=1, pady=20, padx=20, sticky="nwse")

        deleteImg = ImageTk.PhotoImage(Image.open("img/delete.png"))

        self.deleteButton = customtkinter.CTkButton(master=self.add_delete_frame, image=deleteImg, text="", bg_color="#FFF", command=self.delete_track)
        self.deleteButton.grid(row=0, column=1, columnspan=1, pady=20, padx=20, sticky="nwse")



        self.openSavedButton = customtkinter.CTkButton(master=self.saved_frame, text="Select saved score", command=self.openSavedImgEvent)
        self.openSavedButton.grid(row=0, column=0, columnspan=1, pady=20, padx=20, sticky="nwse")

        self.savedImgLabel = customtkinter.CTkLabel(master=self.saved_frame, text="")
        self.savedImgLabel.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.savedImgLabel.grid(row=1, column=0, columnspan=3, sticky="nwse")


        self.optionmenu_1.set("Dark")

    
    def on_closing(self, event=0):
        self.destroy()

    def button_event(self):
        print("button pressed")   

    def delete_track(self):
        deletedTrack = self.tracks.pop()
        deletedTrack.hide_track()
        
    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def add_track(self):
        track_frame = customtkinter.CTkFrame(master=self.tracks_subframe)
        track_frame.rowconfigure((0,1,2,3), weight=1)
        track_frame.columnconfigure((0,1,2), weight=1)

        trk = track.Track(track_frame, self.idTrack)
        self.idTrack += 1
        trk.show_track(len(self.tracks)+1)
        self.tracks.append(trk)
        self.bbox = self.tracks_canvas.bbox("all") 
        self.tracks_canvas.configure(scrollregion=self.bbox)

    def savedBtnEvent(self):
        print("saved")
        self.add_delete_frame.grid_forget()
        self.tracks_frame.grid_forget()

        self.saved_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='nwse')
        self.saved_frame.rowconfigure(0, weight=4)
        self.saved_frame.columnconfigure(0, weight=4)  

    def playBtnEvent(self):
        print("play")  
        self.saved_frame.grid_forget()
        
        self.add_delete_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='nwse')
        self.add_delete_frame.rowconfigure(0, weight=1)
        self.add_delete_frame.columnconfigure((0,1), weight=1)  
        
        self.tracks_frame.grid(row=1, column=0, columnspan=3, sticky='nwse')
        self.tracks_frame.rowconfigure(0, weight=1)
        self.tracks_frame.columnconfigure(0, weight=1)

    def openSavedImgEvent(self):
        filename = filedialog.askopenfilename(title='open')

        image = Image.open(filename).resize((self.saved_frame.winfo_width()-10, 200), Image.ANTIALIAS)
        self.savedImg = ImageTk.PhotoImage(image)
        self.savedImgLabel.configure(image=self.savedImg)
     
        


    # def resizeButton(self, e):
    #     rawImg = Image.open("img/save.png")
    #     resImg =rawImg.resize((e.width,e.height), Image.ANTIALIAS)
    #     self.addImg = ImageTk.PhotoImage(resImg)
    #     self.label1.configure(image = resImg)  
        
    
    
if __name__ == "__main__":
    app = App()
    app.mainloop()