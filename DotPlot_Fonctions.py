"""Ce script contient les fonctions de bases permettant de faire un DotPlot à partir de deux fichiers de protéomes associés à deux espèces (BlastP)"""

from ConnectionToDataBase import *
import matplotlib.pyplot as plt
import numpy as np
import time
import os



#######################################################################################
# Fonctions pour un DotPlot avec BlastP                                               #
#######################################################################################

def read_fasta(file):
    """
    Lecture d'un fichier fasta et stockage des noms des séquences et des séquences dans deux listes
    input : file (str) : nom du fichier fasta
    output1 : names (list of strings) : liste des noms des séquences
    output2 : sequences (list of strings) : liste des séquences
    """

    names = []
    sequences = []

    with open(file, "r") as f:
        lines = f.readlines() #toutes les lignes du fichier
        for line in lines:
            if line[0] == ">": #si on a un chevron au début de la ligne, lors c'est le titre d'une séquence
                names.append(line[1:].split()[0]) #on ajoute seulement le nom de la séquence
            else : #on a une séquence
                if len(names) == len(sequences): #on a autant de séquence que de noms => la ligne 'line' fait partie de la dernière séquence
                    sequences[-1].append(line)
                else : #on a une différence, donc on ajoute une séquence
                    sequences.append([line])
    return names, sequences


def blastp(proteome1, proteome2, output_file):
    """
    Execution d'un blastp entre 2 protéomes
    input1 : protéome 1 (file name, str) : nom du fichier fasta ayant toutes les séquences protéiques de l'espèce 1
    input2 : protéome 2 (file name, str) : nom du fichier fasta ayant toutes les séquences protéiques de l'espèce 2
    input3 : output_file (file name, str) : nom du fichier de sortie où les résultats du blast sont enregistrés
    """

    debut = time.time()
    print("Blastp en train d'être effectué ...")
    cmd = f"blastp -query {proteome1} -subject {proteome2} -out {output_file} -outfmt '6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore'"
    os.system(cmd) #valeur de e-value seuil par défaut : 10
    print("Fini !")
    fin = time.time()

    with open('ExecutionTimeBlastp.txt', "a") as f: #on enregistre le temps du blast pour en faire une moyenne de temps d'attente 
            f.write(str(fin-debut))
            f.write("\n")

    return 



def paires_homologues(BLASTP_file, seuil):
    """
    input1 : BLASTP_file (file name, str) : nom du fichier de sortie du blastp
    input2 : seuil (float) : score e-value maximale toléré
    output : coord (list of tuples) : liste de toutes les séquences protéiques dont les gènes sont considérés comme homologues
    """

    seq_homologues = []

    with open(BLASTP_file, "r") as f:
        for line in f.readlines():
            evalue = float(line.split('\t')[10])
            if evalue < seuil:
                seq1 = line.split('\t')[0] #query
                seq2 = line.split('\t')[1] #subject
                seq_homologues.append((seq1, seq2))

    return seq_homologues


def coord_homologues(seq_homologues, proteome_seq1, proteome_seq2):
    """
    input1 : seq_homologues (list of tuples) : noms des protéines dont les gènes sont considérés comme homologues
    input2 : proteome_seq1 (list of strings) : liste des noms des protéines du génome 1
    input3 : proteome_seq2 (list of strings) : liste des noms des protéines du génome 2
    output : coord (list of tuples) : coordonnées où la paire de gène sont considérés comme homologues
    """

    coord = []

    for (prot1, prot2) in seq_homologues:
        i = proteome_seq1.index(prot1) 
        j = proteome_seq2.index(prot2)
        coord.append((i,j))

    return coord


def make_DotPlot(espece1, espece2, proteome1, proteome2, seuil):
    """Renvoie la matrice DotPlot, où les coordonnées des gènes homologues sont marquées par un 1
    input1 : espece1 (str) : nom de l'espèce 1
    input2 : espece2 (str) : nom de l'espèce 2
    input3 : proteome1 (file name, str) : nom du fichier fasta ayant toutes les séquences protéiques de l'espèce 1
    input4 : proteome2 (file name, str) : nom du fichier fasta ayant toutes les séquences protéiques de l'espèce 2
    input5 : seuil (float) : score e-value maximale toléré
    output : DotPlot (array) : matrice de 0 et de 1"""

    blast_already_exists = TestIfBlastExists(espece1, espece2)

    if blast_already_exists == 0: #s'il faut faire un blastp
        assembly1 = getAssembly(espece1)
        assembly2 = getAssembly(espece2)
        output_file = "BLASTs/blastp_QUERY-" + assembly1 + "_SUBJECT-" + assembly2 + ".out"
        blastp(proteome1, proteome2, output_file)
        MajBaseBlast(espece1, espece2, output_file) #mise à jour de la base de données
    else: #sinon, le nom du fichier blast se trouve dans la sortie de la fonction TestIfBlastExists
        output_file = blast_already_exists

    paires_hom = paires_homologues(output_file, seuil)

    #on considère que les protéines dans les fichiers protéomes sont dans le même ordre que leur gène sur les chromosomes. 
    proteome_seq1, _ = read_fasta(proteome1)
    proteome_seq2, _ = read_fasta(proteome2)
    coord_hom = coord_homologues(paires_hom, proteome_seq1, proteome_seq2)

    N = len(proteome_seq1) #longueurs des génomes
    M = len(proteome_seq2)

    #création de la matrice DotPlot
    DotPlot = np.zeros((N, M))
    for (i,j) in coord_hom:
        DotPlot[i,j] = 1

    return DotPlot


def DessinerDotPlot(DotPlot_Mat, espece1, espece2):
    """Dessine un DotPlot (figure) entre deux espèces"""

    x, y = np.where(DotPlot_Mat == 1)
    fig = plt.Figure(figsize=(6, 6), dpi=100)
    fig.set_facecolor('#191830')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#193429')
    ax.scatter(x, y, s=0.7, color='#C7A318')
    ax.set_title(f"DotPlot par BlastP", color='#b7d9ec', fontdict={'fontsize': 14, 'fontweight': 'bold'})
    ax.set_xlabel(espece1, color="#b7d9ec", fontdict={'fontsize': 14})
    ax.set_ylabel(espece2, color="#b7d9ec", fontdict={'fontsize': 14})
    abscisses = [g for g in range(np.size(DotPlot_Mat, 0)) if g % 1000 == 0]
    abscisses.append(np.size(DotPlot_Mat, 0))
    ax.set_xticks(abscisses)
    ax.set_xticklabels(abscisses)
    ordonnees = [g for g in range(np.size(DotPlot_Mat, 1)) if g % 1000 == 0]
    ordonnees.append(np.size(DotPlot_Mat, 1))
    ax.set_yticks(ordonnees)
    ax.set_yticklabels(ordonnees)
    ax.tick_params(axis='x', colors="#ffffff")
    ax.tick_params(axis='y', colors="#ffffff")
    fig.savefig("LastDotPlot_img.png")
    return fig



#######################################################################################
# Fonctions annexes                                                                   #
#######################################################################################


def FiltreMat(DotPlot):
    """Filtre le dotplot, enlevant le bruit permettant de mieux voir les diagonales"""
    MatFiltered = np.zeros((np.shape(DotPlot)))
    l = 3 #longueur de la fenêtre de filtrage
    for i in range(np.shape(DotPlot)[0] - l):
        for j in range(np.shape(DotPlot)[1] - l):
            subMat = DotPlot[i:i+l, j:j+l]
            if subMat[0,0] != 0 and subMat[1,1] != 0 and subMat[2,2] != 0: 
                MatFiltered[i,j] = DotPlot[i,j]
                MatFiltered[i+1,j+1] = DotPlot[i+1,j+1]
                MatFiltered[i+2,j+2] = DotPlot[i+2,j+2]
            if subMat[0,2] == 1 and subMat[1,1] == 1 and subMat[2,0] == 1:
                MatFiltered[i+2,j] = DotPlot[i+2,j]
                MatFiltered[i+1,j+1] = DotPlot[i+1,j+1]
                MatFiltered[i,j+2] = DotPlot[i,j+2]
    return MatFiltered


def VoirMax(Mat, i, j, r):
    """Retourne le maximum de la matrice aux alentours des coordonnées (i,j) à un 'rayon' r
    input1 : Mat (array) : Matrice alternative encodant les diagonales du DotPlot
    input2 : i (int) : position i du DotPlot
    input3 : j (int) : position j du DotPlot
    input4 : r (int) : 'rayon' où l'on relèvera le maximum
    output (int) : maximum dans la sous-matrice"""
    N, M = Mat.shape
    x_min, x_max = max(0, i-r), min(N, i+r+1)
    y_min, y_max = max(0, j-r), min(M, j+r+1)
    
    sub_mat = Mat[x_min:x_max, y_min:y_max]
    
    if np.all(sub_mat == 0): #si tout est égal à 0
        return 0
    
    return np.max(sub_mat[sub_mat != 0])


def PlusLongueDiag(Mat, r):
    """Retourne la longueur de la plus longue diagonale
    intput1 : Mat (array) : DotPlot
    intput2 : r (int) : 'rayon' où l'on relèvera le maximum de la matrice encodant les diagonales"""
    N, M = Mat.shape
    alt = np.zeros((N, M))

    for i in range(N-1, -1, -1):
        for j in range(M-1, -1, -1):
            if Mat[i,j] != 0:
                if i == 0 or i == N-1 or j == 0 or j == M-1:
                    alt[i,j] = 1
                else:
                    alt[i,j] = VoirMax(alt, i, j, r) + 1
                    
    return np.max(alt)





