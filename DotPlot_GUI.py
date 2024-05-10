"""Ce script contient un code permettant d'avoir une interface graphique nous proposant d'effectuer un dotplot entre deux espèces choisies"""

from DotPlot_Fonctions import *
from CDsearch_Fonctions import *
from ConnectionToDataBase import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import simpledialog
import os




#######################################################################################
# Interface Graphique : Affichage                                                     #
#######################################################################################

figDefaut = plt.Figure(figsize=(6, 6), dpi=100) #DotPlot vide
figDefaut.set_facecolor('#191830')
ax = figDefaut.add_subplot(111)
ax.set_title("Dot Plot vide", color='#b7d9ec', fontdict={'fontsize': 19, 'fontweight': 'bold'})
ax.set_facecolor('#193429')
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)


class GUI:

    def __init__(self):
        self.window = tk.Tk() #création d'une fenêtre
        self.window.geometry("1100x675")
        self.window.config(bg='#191830')
        self.window.title("Programme DotPlot")


        self.menu = tk.Menu(self.window) #création d'une barre de menu
        self.filemenu = tk.Menu(self.menu, tearoff=0) #création d'un menu déroulant
        self.filemenu.add_command(label="Sauvegarder le dernier DotPlot", command=self.SaveDotPlot) #ajouter une option au menu déroulant
        self.filemenu.add_command(label="Ajouter une espèce", command=self.AjouterEspece)
        self.menu.add_cascade(label="Options", menu=self.filemenu) #ajouter le menu déroulant à la barre de menu
        self.menu.config(bg='#161533', fg='#b7d9ec')
        self.window.config(menu=self.menu) #ajouter la barre de menu à la fenêtre


        self.canvas = FigureCanvasTkAgg(figDefaut, master=self.window) #espace pour le DotPlot
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=0.42, rely=0.05)

        self.label1 = tk.Label(self.window, text="Choisissez une première espèce : ")
        self.label1.config(font=("DejaVu Serif", 13), bg="#191830", fg="#b7d9ec")
        self.label1.place(relx=0.03, rely=0.05)

        self.Especes = getEspeces()

        self.ListeEspece1 = tk.StringVar(self.window)
        self.optionmenu1 = tk.OptionMenu(self.window, self.ListeEspece1, *self.Especes)
        self.optionmenu1.config(width=40)
        self.optionmenu1.place(relx=0.03, rely=0.10)

        self.label2 = tk.Label(self.window, text="Choisissez une deuxième espèce : ")
        self.label2.config(font=("DejaVu Serif", 13), bg="#191830", fg="#b7d9ec")
        self.label2.place(relx=0.03, rely=0.18)

        self.ListeEspece2 = tk.StringVar(self.window)
        self.optionmenu2 = tk.OptionMenu(self.window, self.ListeEspece2, *self.Especes)
        self.optionmenu2.config(width=40)
        self.optionmenu2.place(relx=0.03, rely=0.23)

        self.label3 = tk.Label(self.window, text="Entrez un seuil :")
        self.label3.config(font=("DejaVu Serif", 13), bg="#191830", fg="#b7d9ec")
        self.label3.place(relx=0.03, rely=0.31)
        self.seuil_entry = tk.Entry(self.window, width=8, bg="#dcdcdc", fg="#000000")
        self.seuil_entry.place(relx=0.03, rely=0.36)

        self.ligne = tk.Canvas(self.window, width=410, height=1, bg="#a76726", highlightbackground='#191830')
        self.ligne.place(relx=0.01, rely=0.42)

        self.Filtre = tk.BooleanVar()
        self.checkbutton = tk.Checkbutton(self.window, variable=self.Filtre, bg="#191830")
        self.checkbutton.place(relx=0.03, rely=0.44)
        self.label4 = tk.Label(self.window, text="Filtrer le DotPlot")
        self.label4.config(font=("DejaVu Serif", 13), bg="#191830", fg="#b7d9ec")
        self.label4.place(relx=0.06, rely=0.44)

        self.CDsearch = tk.BooleanVar()
        self.checkbutton = tk.Checkbutton(self.window, variable=self.CDsearch, bg="#191830")
        self.checkbutton.place(relx = 0.03, rely=0.52)
        self.label5 = tk.Label(self.window, text="DotPlot par RPSBlast")
        self.label5.config(font=("DejaVu Serif", 13), bg="#191830", fg="#b7d9ec")
        self.label5.place(relx=0.06, rely=0.52)

        self.buttonBlast = tk.Button(self.window, text="Dessiner le DotPlot", command=self.updateCanva)
        self.buttonBlast.config(width=15,font=("DejaVu Serif", 20, "bold"), highlightbackground="#370028", bg="#191830", fg="#b7d9ec")
        self.buttonBlast.place(relx=0.08, rely=0.60)

        self.attenteMin, self.attenteSec = self.Temps("ExecutionTimeBlastp.txt")
        self.label6 = tk.Label(self.window, text=f"Temps d'attente pour l'execution d'un BlastP la première fois : {self.attenteMin}min{self.attenteSec}s.", font=("DejaVu Serif", 10, "italic"), bg="#191830", fg="#b7d9ec")
        self.label6.place(relx=0.02, rely=0.90)
        self.attenteMin, self.attenteSec = self.Temps("ExecutionTimeRpsblast.txt")
        self.label7 = tk.Label(self.window, text=f"Temps d'attente pour l'execution d'un RPSBlast la première fois : {self.attenteMin}min{self.attenteSec}s", font=("DejaVu Serif", 10, "italic"), bg="#191830", fg="#b7d9ec")
        self.label7.place(relx=0.02, rely=0.95)

        self.label9 = tk.Label(self.window, text="")
        self.label9.config(font=("DejaVu Serif", 13), bg="#191830", fg="#b7d9ec")
        self.label9.place(relx=0.46, rely=0.95)


        self.window.mainloop()


    def Temps(self, fileTime):
        """
        input1 : fileTime (file name, str) : fichier où sont enregistrés les temps d'execution des blasts
        output1 : temps (float) : temps d'execution moyen d'un blast
        """
        
        with open(fileTime, "r") as f:
            lines = f.readlines()
            temps = 0

            for line in lines:
                temps += float(line.split()[0]) #première colonne contenant le temps

            temps = temps/len(lines) #ce temps est en seconde 
        
        minutes, secondes = divmod(temps, 60) #quotient et reste de la division

        return int(minutes), int(secondes)


    def updateCanva(self):

        espece1 = self.ListeEspece1.get() #obtenir l'espèce 1 choisie
        espece2 = self.ListeEspece2.get() #obtenir l'espèce 2 choisie

        if espece1 == espece2:
            raise ValueError("Veuillez choisir deux espèces différentes")

        if espece2 < espece1: #on définit un ordre arbitraire afin de ne pas avoir de problèmes avec les fichiers
            espece1, espece2 = espece2, espece1

        proteome1 = getProteome(espece1) #obtenir le proteome 1 lié
        proteome2 = getProteome(espece2) #obtenir le proteome 2 lié

        seuil = float(self.seuil_entry.get()) #récupérer les entrées de l'utilisateur
        FiltreBool = self.Filtre.get() 
        CDSearchBool = self.CDsearch.get()

        if seuil == "" or seuil < 0:
            raise ValueError("Veuillez spécifier un seuil strictement positif")

        if CDSearchBool:
            Cdd_esp1_file = getCDsearch(espece1)
            Cdd_esp2_file = getCDsearch(espece2)
            DotPlot_Mat = make_DotPlot_SimFonc(proteome1, proteome2, Cdd_esp1_file, Cdd_esp2_file, seuil)
        else:
            DotPlot_Mat = make_DotPlot(espece1, espece2, proteome1, proteome2, seuil)

        if FiltreBool:
            DotPlot_Mat = FiltreMat(DotPlot_Mat)

            if CDSearchBool: #les points dans une diagonale avec un RPSBlast sont plus éparpillés, on doit donc avoir un rayon r plus grand
                longDiag = int(PlusLongueDiag(DotPlot_Mat, 79))
            else:
                longDiag = int(PlusLongueDiag(DotPlot_Mat, 58))
            self.label9.destroy()
            self.label9 = tk.Label(self.window, text=f"Longueur de la plus grande diagonale : {longDiag} paires de gène")
            self.label9.config(font=("DejaVu Serif", 13), bg="#191830", fg="#b7d9ec")
            self.label9.place(relx=0.46, rely=0.95)
        else:
            self.label9.destroy()
            self.label9 = tk.Label(self.window, text="")
            self.label9.config(font=("DejaVu Serif", 13), bg="#191830", fg="#b7d9ec")
            self.label9.place(relx=0.46, rely=0.95)


        if CDSearchBool:
            new_fig = DessinerDotPlot_SimFonc(DotPlot_Mat, espece1, espece2)
        else:
            new_fig = DessinerDotPlot(DotPlot_Mat, espece1, espece2)

        self.canvas.figure = new_fig #".figure" => on remplace la zone de dessin réservée pour une figure
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=0.42, rely=0.05)


    def SaveDotPlot(self):
        name = simpledialog.askstring("Option", prompt="Entrer un nom de fichier :")
        if not(name[-4:] == '.png'):
            name += '.png' #si l'utilisateur n'a pas rajouté l'extension, on le fait 
        os.rename('LastDotPlot_img.png', name)


    def AjouterEspece(self):
        global ListeEspece1, ListeEspece2
        ass = simpledialog.askstring("Option", prompt="Entrer l'assembly de l'espèce :")
        espece_name, ftp = "", ""
        with open("prokaryotes_complete-genomes_downloadable.csv", "r") as f:
            for line in f.readlines():
                if line.split(',')[5].replace('"', '') == ass: #on parcourt le fichier.csv et on récupère l'espèce/lien FTP 
                    espece_name = line.split(',')[0].replace('"', '')
                    ftp = line.split(',')[14].replace('"', '')

        if espece_name == "":
            raise ValueError("Assembly non reconnue")

        proteome_file = DownloadProteome(ftp)
        cdsearch = rpsblast(ass, proteome_file)

        MajBaseProcaryotes(espece_name, ass, ftp, proteome_file, cdsearch)

        self.Especes = getEspeces() #mise à jour de l'interface

        self.ListeEspece1 = tk.StringVar(self.window)
        self.optionmenu1 = tk.OptionMenu(self.window, self.ListeEspece1, *self.Especes)
        self.optionmenu1.config(width=40)
        self.optionmenu1.place(relx=0.03, rely=0.10)

        self.ListeEspece2 = tk.StringVar(self.window)
        self.optionmenu2 = tk.OptionMenu(self.window, self.ListeEspece2, *self.Especes)
        self.optionmenu2.config(width=40)
        self.optionmenu2.place(relx=0.03, rely=0.23)



GUI()