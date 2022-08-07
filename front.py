import tkinter
import tkinter.messagebox
from tkinter import ttk, filedialog
import customtkinter
from PIL import Image, ImageTk
import os
import track

# solve local imports
import sys
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
WORKSPACE = os.path.dirname(FILE_PATH)

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

PATH = os.path.dirname(os.path.realpath(__file__))

class App(customtkinter.CTk):

    WIDTH = 950
    HEIGHT = 1100

    def __init__(self):
        super().__init__()

        # tracks related variables
        self.idTrack = 0
        self.tracks = []

        # basic app definitions
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
        # This frame contains our logo, menu and theme picker.

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(6, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        # create logo image
        logoImg = Image.open(PATH + "/img/logo.png").resize((160, 90)).convert('RGBA')
        self.logo = ImageTk.PhotoImage(logoImg)

        # create canvas for our logo
        self.logo_canvas = tkinter.Canvas(master=self.frame_left, bg="#292d2e", width=160, height=100, highlightthickness=0)
        self.logo_canvas.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.logo_canvas.grid(row=1, column=0, pady=10, padx=10)
        self.logo_canvas.create_image(80,50, image=self.logo)

        # create play menu button to select the tracks view
        self.play_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Play!",
                                                command=self.playBtnEvent)
        self.play_button.grid(row=2, column=0, pady=10, padx=20)

        # create saved menu button to select the saved files view
        self.saved_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Saved",
                                                command=self.savedBtnEvent)
        self.saved_button.grid(row=3, column=0, pady=10, padx=20)

        # create add track menu button to add tracks
        self.add_track_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Add track",
                                                fg_color="#00A90B",
                                                hover_color="#009C0A",
                                                command=self.add_track)

        # create delete track menu button to delete tracks
        self.delete_track_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Delete track",
                                                fg_color="#AF0000",
                                                hover_color="#9C0000",
                                                command=self.delete_track)

        self.label_mode = customtkinter.CTkLabel(master=self.frame_left, text="Appearance Mode:")
        self.label_mode.grid(row=9, column=0, pady=0, padx=20, sticky="w")

        self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                        values=["Light", "Dark", "System"],
                                                        command=self.change_appearance_mode)
        self.optionmenu_1.grid(row=10, column=0, pady=10, padx=20, sticky="w")

        # ============ frame_right ============
        # This frame contains the buttons to add and delete tracks, and the frames for the tracks.

        # Configure the frame as 1x2 with more weight on the second row (the frames one)
        self.frame_right.rowconfigure(0, weight=0)
        self.frame_right.rowconfigure(1, weight=1)
        self.frame_right.columnconfigure(0, weight=1)

        # saved_frame will be gridded when pressing Saved button
        self.saved_frame = customtkinter.CTkFrame(master=self.frame_right)

        # add_delete_frame will be gridded when pressing Play! button
        #self.add_delete_frame = customtkinter.CTkFrame(master=self.frame_right)

        # tracks_frame will be gridded when pressing Play! button
        # create frame for add and delete tracks button. This frame will be gridded when play button.
        #self.add_delete_frame = customtkinter.CTkFrame(master=self.frame_right)
      
        # create tracks frame
        self.tracks_frame = customtkinter.CTkFrame(master=self.frame_right)
        

        # create tracks canvas inside tracks frame. We need to use canvas to be able to use a scrollbar
        # canvas gets gridded when a tracks is added.
        self.tracks_canvas = customtkinter.CTkCanvas(master=self.tracks_frame,bg='#292d2e')
      
        # create scrollbar to scroll across multiple tracks
        self.scroll = ttk.Scrollbar(master=self.tracks_frame, orient='vertical', command=self.tracks_canvas.yview)
        self.scroll.grid(row=0,column=1,sticky='ns')
        self.tracks_canvas.configure(yscrollcommand=self.scroll.set)

        # create a frame inside the tracks canvas so that we can create a scrollable window on it
        self.tracks_subframe = customtkinter.CTkFrame(master=self.tracks_canvas)
        self.tracks_subframe.grid(row=0, column=0, sticky='nwse',pady=50, padx=50)
        self.tracks_subframe.rowconfigure(0, weight=1)
        self.tracks_subframe.columnconfigure(0, weight=1)

        # create scrollable window
        self.tracks_canvas.create_window((0,0), window=self.tracks_subframe, anchor='nw')

        # we need this to render the window
        self.tracks_subframe.update_idletasks()  

        # create add track image
        #self.addImgRaw = Image.open("img/add.png")
        #self.addImg = ImageTk.PhotoImage(self.addImgRaw, Image.ANTIALIAS)

        # create add track button
        #self.addButton = customtkinter.CTkButton(master=self.add_delete_frame,image=self.addImg, text="",command=self.add_track)
        #self.addButton.grid(row=0, column=0, columnspan=1, pady=20, padx=20, sticky="nwse")

        # create delete track image
        #deleteImg = ImageTk.PhotoImage(Image.open("img/delete.png"))

        # create delete track button
        #self.deleteButton = customtkinter.CTkButton(master=self.add_delete_frame, image=deleteImg, text="", bg_color="#FFF", command=self.delete_track)
        #self.deleteButton.grid(row=0, column=1, columnspan=1, pady=20, padx=20, sticky="nwse")

        # create button to open saved files        
        self.openSavedButton = customtkinter.CTkButton(master=self.saved_frame, text="Select saved score", command=self.openSavedImgEvent)
        self.openSavedButton.grid(row=0, column=0, columnspan=1, pady=20, padx=20, sticky="nwse")

        # create label to show saved score
        self.savedImgLabel = customtkinter.CTkLabel(master=self.saved_frame, text="")
        self.savedImgLabel.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.savedImgLabel.grid(row=1, column=0, columnspan=3, sticky="nwse")

        # app default settings
        self.optionmenu_1.set("Dark")

    
    def on_closing(self, event=0):
        self.destroy()

    def button_event(self):
        print("button pressed")   

    def delete_track(self):
        deletedTrack = self.tracks.pop()
        deletedTrack.hide_track()

        # if there are no tracks left we remove the canvas
        if len(self.tracks) == 0:
            self.tracks_canvas.grid_forget()
        
    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def add_track(self):
        # if there are no tracks, we need to grid the tracks canvas
        if len(self.tracks) == 0:
            self.tracks_canvas.grid(row=0,column=0,sticky='nwse')
            self.tracks_canvas.rowconfigure(0, weight=1)
            self.tracks_canvas.columnconfigure(0, weight=1)

        # create a weighted frame for the new track
        track_frame = customtkinter.CTkFrame(master=self.tracks_subframe)
        track_frame.rowconfigure((0,1,2), weight=1)
        track_frame.columnconfigure((0,2,3), weight=1)
        track_frame.columnconfigure(1, weight=5)


        # create a track
        trk = track.Track(track_frame, self.idTrack)
        self.idTrack += 1
        trk.show_track(len(self.tracks)+1)
        self.tracks.append(trk)

        # update the tracks canvas scrollbar region
        self.bbox = self.tracks_canvas.bbox("all") 
        self.tracks_canvas.configure(scrollregion=self.bbox)

    def savedBtnEvent(self):
        #self.add_delete_frame.grid_forget()
        self.tracks_frame.grid_forget()

        self.add_track_button.grid_forget()
        self.delete_track_button.grid_forget()

        self.saved_button.grid(row=3, column=0, pady=10, padx=20)


        self.saved_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='nwse')
        self.saved_frame.rowconfigure(0, weight=4)
        self.saved_frame.columnconfigure(0, weight=4)  

    def playBtnEvent(self):
        self.saved_frame.grid_forget()
        
        # self.add_delete_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='nwse')
        # self.add_delete_frame.rowconfigure(0, weight=1)
        # self.add_delete_frame.columnconfigure((0,1), weight=1)  
        
        self.add_track_button.grid(row=3, column=0, pady=10, padx=20)
        self.delete_track_button.grid(row=4, column=0, pady=10, padx=20)
        self.saved_button.grid(row=5, column=0, pady=10, padx=20)

        self.tracks_frame.grid(row=1, column=0, columnspan=3, sticky='nwse')
        self.tracks_frame.rowconfigure(0, weight=1)
        self.tracks_frame.columnconfigure(0, weight=1)

    def openSavedImgEvent(self):
        filename = filedialog.askopenfilename(initialdir=os.path.join(FILE_PATH, "files"),title='Select a score')

        image = Image.open(filename).resize((self.saved_frame.winfo_width()-10, 200), Image.ANTIALIAS)
        self.savedImg = ImageTk.PhotoImage(image)
        self.savedImgLabel.configure(image=self.savedImg)

    
if __name__ == "__main__":
    app = App()
    app.mainloop()