"""Ce script contient les fonctions nécessaires à l'execution d'un RPSBlast d'un protéome ainsi que les fonctions permettant d'afficher un DotPlot basé sur deux fichiers RPSBlast"""

from DotPlot_Fonctions import *
import matplotlib.lines as mlines
import numpy as np
import os
import time




def rpsblast(assembly, proteome_file):
    """Effectue un rpsblast+
    input1 : assembly (str) : code assembly d'une espèce
    input2 : proteome_file (str, file_name) : nom du fichier du protéome de                  l'espèce
    output : output_file (str, file name) : fichier de sortie du rpsblast+"""

    output_file = f"rpsblast_QUERY-{assembly}_DB-Cdd_NCBI.out"

    debut = time.time()
    print("RPSblast en train d'être effectué ...")
    os.system(f"rpsblast+ -db /usr/share/cdd/Cdd_NCBI -query Proteomes/{proteome_file} -out CDsearchs/{output_file} -outfmt 7") #base CDD pour avoir les domaines conservées et ainsi les fonctions 
    print("Fini !")
    fin = time.time()

    with open("ExecutionTimeRpsblast.txt", "a") as f:
        f.write(str(fin-debut)) #enregistrement du temps
        f.write("\n")

    return output_file


def read_cdd(file, seuil):
    """
    Lecture d'un fichier fasta et retourne un dictionnaire avec en clefs les noms des séquences et en valeurs les cdds
    input : file (str) : nom du fichier fasta
    output : cdd_esp (dic of str) : en clef les noms des séquences, en valeur les cdds associés
    """

    cdd_esp = {}

    with open(file, "r") as f:
        lines = f.readlines() 
        for line in lines:
            if line[0] != '#':
                gene = line.split("\t")[0] #le nome du gène se trouve à la 1e colonne
                cdd = line.split("\t")[1] #le code CDD se situe à la 2e colonne
                if float(line.split("\t")[10]) < seuil: #evalue = 11e colonne
                    if gene in cdd_esp: #on ajoute le cdd aux valeurs du gène
                        cdd_esp[gene].append(cdd)
                    else:
                        cdd_esp[gene] = [cdd]
    return cdd_esp


def Similarite(cdd_esp1, cdd_esp2, gene1, gene2):
    """
    Calcule la similarité fonctionnelle entre deux gènes en se basant s'ils ont des cdd en commun
    input1 : cdd_esp1 (dic of str) : en clef les noms des séquences, en valeur les cdds associés
    input2 : cdd_esp2 (dic of str) : en clef les noms des séquences, en valeur les cdds associés
    input3 : gene1 (str) : nom du premier gène
    input4 : gene2 (str) : nom du deuxième gène
    output : sim (float) : similarité fonctionnelle entre les deux gènes
    """
    sim = 0

    cdds1 = cdd_esp1[gene1]
    cdds2 = cdd_esp2[gene2]
    cdds_unique = np.unique(cdds1 + cdds2) #liste de l'ensemble des cdds uniques des deux gènes

    for cdd in cdds_unique:
        if (cdd in cdds1) and (cdd in cdds2): #si le cdd est commun 
            sim += 1

    return sim / len(cdds_unique)


def make_DotPlot_SimFonc(proteome1, proteome2, cdd_esp1_file, cdd_esp2_file, seuil):
    """Retourne un DotPlot basé sur deux RPSblast+"""

    proteome_seq1, _ = read_fasta(proteome1)
    proteome_seq2, _ = read_fasta(proteome2)

    N = len(proteome_seq1)
    M = len(proteome_seq2)

    cdd_esp1 = read_cdd(cdd_esp1_file, seuil)
    cdd_esp2 = read_cdd(cdd_esp2_file, seuil)

    DotPlot_Mat = np.zeros((N, M))
    
    for i in range(N):
        for j in range(M):
            gene1 = proteome_seq1[i]
            gene2 = proteome_seq2[j]
            if gene1 in cdd_esp1 and gene2 in cdd_esp2: #pas tous les gènes ont une annotation fonctionnelle
                sim = Similarite(cdd_esp1, cdd_esp2, proteome_seq1[i], proteome_seq2[j])
                if sim > 0.80:
                    DotPlot_Mat[i,j] = 2 
                elif sim > 0.50:
                    DotPlot_Mat[i,j] = 3
                elif sim > 0:
                    DotPlot_Mat[i,j] = 4

    return DotPlot_Mat


def DessinerDotPlot_SimFonc(DotPlot_Mat, espece1, espece2):
    """Dessine un DotPlot (figure) entre deux espèces"""

    x2, y2 = np.where(DotPlot_Mat == 2)
    x3, y3 = np.where(DotPlot_Mat == 3)
    x4, y4 = np.where(DotPlot_Mat == 4)

    fig = plt.Figure(figsize=(6, 6), dpi=100)
    fig.set_facecolor('#191830')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#193429')
    ax.scatter(x2, y2, s=0.7, color='#ff0000')
    ax.scatter(x3, y3, s=0.7, color='#00ff00')
    ax.scatter(x4, y4, s=0.7, color='#0087ff')

    ax.set_title(f"DotPlot par RPSBlast", color='#b7d9ec', fontdict={'fontsize': 14, 'fontweight': 'bold'})
    ax.set_ylabel(espece1, color="#b7d9ec", fontdict={'fontsize': 14})
    ax.set_xlabel(espece2, color="#b7d9ec", fontdict={'fontsize': 14})
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

    #légende personnalisée
    leg1 = mlines.Line2D([], [], color='k', marker='None', markersize=10, linestyle='None', label='Similarité fonctionnelle :')
    leg2 = mlines.Line2D([], [], color='#ff0000', marker='o', markersize=10, linestyle='None', label='>80%')
    leg3 = mlines.Line2D([], [], color='#00ff00', marker='o', markersize=10, linestyle='None', label='>50%')
    leg4 = mlines.Line2D([], [], color='#0087ff', marker='o', markersize=10, linestyle='None', label='<50%')
    ax.legend(handles=[leg1, leg2, leg3, leg4], loc='upper center', bbox_to_anchor=(0.5, 0.055), fancybox=True, ncol=4, prop={'size': 8}, framealpha=0.1)
    #bbox_to_anchor = position / ncol = nb de colonne / framealpha = transparence

    fig.savefig("LastDotPlot_img.png")

    return fig