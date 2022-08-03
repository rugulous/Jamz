from PIL import Image
from datetime import datetime
import json
import os
import shutil
import subprocess
import math
import tkinter as tk
import tkinter.messagebox
import sqlite3

################################################################################
################################################################################
########################## EXPORT SCORE UTILS ##################################
################################################################################
################################################################################

MUSESCORE_PATH = "C:\\Program Files\\MuseScore 3.5 Beta\\bin\\Musescore3.exe"

def exportScores(scores,path = None):
    if path == None:
        path = os.path.dirname(os.path.realpath(__file__)) + "\\test\\"
        print(path)

    json = exportJSON(scores, path)
    runMSExport(json)
    

def exportJSON(scores, path):
    score_data = []
    for score in scores:
        dir_name = os.path.splitext(score)[0].lower().replace(" ","-")
        if(os.path.isdir(path + dir_name)):
            shutil.rmtree(path + dir_name)

        os.mkdir(path + dir_name)
        data = {
            "in":path + score,
            "plugin":"jamz.qml",
            "out":path + dir_name + "\\" + dir_name + ".png"
        }

        score_data.append(data)

    json_name = path + "jamz-export-" + datetime.today().strftime('%Y-%m-%d-%H-%M-%S') + ".json"
    print("Creating JSON file at", json_name)
    with open(json_name,"w") as file:
        json.dump(score_data, file)
        
    return json_name


def runMSExport(json_name, removeJSON = True):
    print("Running MuseScore export with JSON file...")
    subprocess.run([MUSESCORE_PATH, "--job",json_name])
    print("Export finished!")

    if(removeJSON):
        print("Removing json file...")
        os.remove(json_name)
        print()

def prepareImages(scores, path):
    print("Preparing images for PowerPoint...")
    for score in scores:
        directory = path + os.path.splitext(score)[0].lower().replace(" ","-")
        print("Checking exports in " + directory)
        files = os.listdir(directory)
        for file in files:
            filename = directory + "\\" + file
        
            print("Opening", filename, "for editing...")
            src = Image.open(filename)
            width, height = src.size
            height = height - 250
        
            crop = src.crop((0,0,width, height))
            alpha = crop.convert('RGBA').split()[-1]

            img = Image.new("RGBA", src.size, (255,255,255,255))
            img.paste(crop, mask=alpha)
            img.show()

            pixels = img.load()
        

            first_black = -1
            last_black = -1
            for y in range(height):
                for x in range(math.floor(width * 0.25), math.floor(width * 0.6)):
                    cpixel = pixels[x, y]
                    if cpixel == (0,0,0,255):
                        if first_black == -1:
                            first_black = y

                        last_black = y
                        break

            print("Black pixels found between", first_black, "and", last_black, "(image size:", width,",",height,")")
            if(first_black == -1):
                print("No notes found!!")
            else:
                print("Cropping image to", min(last_black +first_black,height),"px tall")
                box = (0,0,width, min(last_black +first_black,height))
                new_image = img.crop(box)
                new_image.show()

        print()

################################################################################
################################################################################
############################## MAIN STUFF ######################################
################################################################################
################################################################################

def loadSongs():
    con = sqlite3.connect('jamz.db')
    c = con.cursor()
    c.execute('SELECT ID, Title FROM Song')
    rows = c.fetchall()
    con.close()
    return rows

def loadArtists():
    con = sqlite3.connect('jamz.db')
    c = con.cursor()
    c.execute("SELECT ID, Name FROM Artist")
    rows = c.fetchall()
    con.close()
    return rows

def loadGenres():
    con = sqlite3.connect('jamz.db')
    c = con.cursor()
    c.execute("SELECT ID, Name FROM Genre")
    rows = c.fetchall()
    con.close()
    return rows

class MainMenu:

    add_song = None
    
    def __init__(self, master):
        self.master = master
        
        #bind controls
        self.frmSongs = tk.LabelFrame(master=self.master,width=250,height=500,padx=10,text="Songs")
        self.lbSongs = tk.Listbox(master=self.frmSongs)
        self.lbSongs.pack()
        self.frmSongs.pack(side=tk.LEFT)

        self.frmSongBtn = tk.Frame(master = self.master, width=250,height=500,padx=10)
        self.btnAddSong = tk.Button(master=self.frmSongBtn,text="Add...",command=self.btnAddSong_click)
        self.btnAddSong.pack()
        self.frmSongBtn.pack(side=tk.LEFT)

        #populate listbox
        self.songs = loadSongs()
        if len(self.songs) == 0:
            self.lbSongs.insert(tk.END, "<no available songs>")
        else:
            for song in self.songs:
                self.lbSongs.insert(tk.END,song[1])

    def btnAddSong_click(self):
        tl = tk.Toplevel()
        tl.title("Add Song")
        self.add_song = AddSong(tl)

class AddSong:
    valid_config = {'foreground':'#080','highlightcolor':'#080','highlightbackground':'#080'}
    invalid_config = {'foreground':'#F00','highlightcolor':'#F00','highlightbackground':'#F00'}
    no_artist = "<no available artists>"
    no_genre = "<no available genres>"
    
    def __init__(self, master):
        self.master = master

        #load data
        artists = loadArtists()
        if not artists:
            artists = [(-1,self.no_artist)]

        self.artists = artists
        disp_artists = []
        for artist in artists:
            disp_artists.append(artist[1])

        genres = loadGenres()
        if not genres:
            genres = [(-1, self.no_genre)]

        self.genres = genres
        disp_genres = []
        for genre in genres:
            disp_genres.append(genre[1])
            
        
        #bind controls
        self.frmTitle = tk.LabelFrame(master=self.master,width=250,text="Song Title")
        self.txtTitle = tk.Entry(master=self.frmTitle)
        self.txtTitle.pack(fill=tk.BOTH, expand=1)
        self.frmTitle.pack(fill=tk.BOTH, expand=1,padx=20,pady=5)

        self.frmArtist = tk.LabelFrame(master=self.master,text="Artist")
        self.varArtist = tk.StringVar(self.master)
        self.varArtist.set(disp_artists[0])      
        self.ddlArtist = tk.OptionMenu(self.frmArtist,self.varArtist, *disp_artists)
        self.ddlArtist.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
        self.btnAddArtist = tk.Button(master=self.frmArtist,text="Add...")
        self.btnAddArtist.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
        self.frmArtist.pack(fill=tk.BOTH, expand=1,padx=20,pady=5)

        self.frmGenre = tk.LabelFrame(master=self.master,width=250,height=500,text="Genre")
        self.varGenre = tk.StringVar(self.master)
        self.varGenre.set(disp_genres[0])      
        self.ddlGenre = tk.OptionMenu(self.frmGenre,self.varGenre, *disp_genres)
        self.ddlGenre.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
        self.btnAddGenre = tk.Button(master=self.frmGenre,text="Add...")
        self.btnAddGenre.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
        self.frmGenre.pack(fill=tk.BOTH, expand=1,padx=20,pady=5)

        self.frmDuration = tk.LabelFrame(master=self.master,width=250,height=500,text="Duration")
        self.txtMins = tk.Entry(master=self.frmDuration)
        self.txtMins.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
        self.lblMins = tk.Label(master=self.frmDuration,text="Minutes")
        self.lblMins.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
        self.txtSecs = tk.Entry(master=self.frmDuration)
        self.txtSecs.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
        self.lblSecs = tk.Label(master=self.frmDuration,text="Seconds")
        self.lblSecs.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
        self.frmDuration.pack(fill=tk.BOTH, expand=1,padx=20,pady=5)

        self.frmYT = tk.LabelFrame(master=self.master,width=250,height=500,text="YouTube Link")
        self.txtYTLink = tk.Entry(master=self.frmYT)
        self.txtYTLink.pack(fill=tk.BOTH, expand=1)
        self.frmYT.pack(fill=tk.BOTH, expand=1,padx=20,pady=5)

        self.btnSave = tk.Button(master=self.master, text="Save", padx=10, command=self.btnSave_click)
        self.btnSave.pack(pady=5)

    def btnSave_click(self):
        isValid = True
        
        title = self.txtTitle.get()
        if title.strip() == "":
            self.frmTitle.configure(self.invalid_config)
            self.txtTitle.configure(self.invalid_config)
            isValid = False
        else:
            self.frmTitle.configure(self.valid_config)
            self.txtTitle.configure(self.valid_config)

        artist = self.varArtist.get()
        if artist == self.no_artist:
            self.frmArtist.configure(self.invalid_config)
            self.ddlArtist.configure(self.invalid_config)
            isValid = False
        else:
            self.frmArtist.configure(self.valid_config)
            self.ddlArtist.configure(self.valid_config)

        genre = self.varGenre.get()
        if genre == self.no_genre:
            self.frmGenre.configure(self.invalid_config)
            self.ddlGenre.configure(self.invalid_config)
            isValid = False
        else:
            self.frmGenre.configure(self.valid_config)
            self.ddlGenre.configure(self.valid_config)

        mins = self.txtMins.get()
        mins = mins.strip()
        minsValid = True
        
        if mins == "":
            isValid = False
            minsValid = False
        else:
            try:
                mins = int(mins)
            except Exception:
                isValid = False
                minsValid = False

        if minsValid:
            self.txtMins.configure(self.valid_config)
            self.lblMins.configure(self.valid_config)
        else:
            self.txtMins.configure(self.invalid_config)
            self.lblMins.configure(self.invalid_config)

        seconds = self.txtSecs.get()
        seconds = seconds.strip()
        secsValid = True
        
        if seconds == "":
            isValid = False
            secsValid = False
        else:
            try:
                seconds = int(seconds)
            except Exception:
                isValid = False
                secsValid = False

        if secsValid:
            self.txtSecs.configure(self.valid_config)
            self.lblSecs.configure(self.valid_config)
        else:
            self.txtSecs.configure(self.invalid_config)
            self.lblSecs.configure(self.invalid_config)

        if secsValid and minsValid:
            self.frmDuration.configure(self.valid_config)
        else:
            self.frmDuration.configure(self.invalid_config)

        link = self.txtYTLink.get()
        if link.strip() == "":
            isValid = False
            self.txtYTLink.configure(self.invalid_config)
            self.frmYT.configure(self.invalid_config)
        else:
            self.txtYTLink.configure(self.valid_config)
            self.frmYT.configure(self.valid_config)

        if isValid:
            tkinter.messagebox.showinfo("Saved","Song Saved!")
        else:
            tkinter.messagebox.showerror("Error","Please correct the fields in red")
    
if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0,0)
    root.title("JAMZ")
    entry_point = MainMenu(root)
    root.mainloop()
