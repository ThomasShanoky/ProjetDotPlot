import psycopg2 as pg
import os



host = None
dbname = 'UneBaseThomas' #psql UneBaseThomas
user = None
password = None



#######################################################################################
# Création et remplissage des tables Procaryotes et Blast                             #
#######################################################################################


connecteur = pg.connect(host=host, dbname=dbname, user=user, password=password)
cur = connecteur.cursor()
with open("Database_Creation.sql", "r") as sql: #création des tables si elles n'existent pas
    script = sql.read()
cur.execute(script)
connecteur.commit()

cur.execute("SELECT COUNT(*) FROM procaryotes;") #compter le nombre d'espèces dans la base
row = cur.fetchall()[0][0]

if row == 0: #si la table est vide (ie si elle vient juste d'être créée), on la remplie avec les espèces jouets
    with open("Database_Remplissage.sql", "r") as sql:
        script = sql.read()
    cur.execute(script)
    connecteur.commit()

connecteur.close()



#######################################################################################
# Obtenir les informations depuis les tables                                          #
#######################################################################################


def getAssembly(espece_name):
    """Récupère le code assembly d'une espèce
    input : espece_name (str) : nom de l'espèce
    output : assembly (str) : code assembly de l'espèce"""
    connecteur = pg.connect(host=host, dbname=dbname, user=user, password=password)
    cur = connecteur.cursor()
    cur.execute(f"SELECT assembly FROM procaryotes WHERE espece = '{espece_name}';") 
    assembly = cur.fetchall()[0][0]
    connecteur.close()

    return assembly


def getEspeces():
    """Récupère toutes les espèces possibles dans la base de données
    output : Especes (list of str) : liste des espèces"""
    connecteur = pg.connect(host=host, dbname=dbname, user=user, password=password) #connexion à la base de données 
    cur = connecteur.cursor() #création d'un curseur
    cur.execute("SELECT espece FROM procaryotes;") #avoir toutes les espèces dans la base
    res = cur.fetchall() #on récupère l'execution du curseur
    connecteur.close()

    Especes = []
    for i in range(len(res)):
        Especes.append(res[i][0]) #la sortie est un tuple contenant l'espèce
    return Especes


def getProteome(espece_name):
    """Récupère le nom du fichier proteome.faa de l'espèce
    input : espece_name (str) : nom de l'espèce
    output : proteome_file (str) : nom du fichier proteome"""
    connecteur = pg.connect(host=host, dbname=dbname, user=user, password=password) 
    cur = connecteur.cursor()
    cur.execute(f"SELECT proteome FROM procaryotes WHERE espece = '{espece_name}';") 
    proteome_file = "Proteomes/" + cur.fetchall()[0][0] #on récupère le nom du fichier proteome dans un tuple dans une liste
    connecteur.close()

    return proteome_file


def getCDsearch(espece_name):
    """Récupère le nom du fichier de CDsearch de l'espèce
    input : espece_name (str) : nom de l'espèce
    output : cdsearch_file (str) : nom du fichier CDsearch"""
    connecteur = pg.connect(host=host, dbname=dbname, user=user, password=password) 
    cur = connecteur.cursor()
    cur.execute(f"SELECT cdsearch FROM procaryotes WHERE espece = '{espece_name}';") 
    cdsearch_file = "CDsearchs/" + cur.fetchall()[0][0] #on récupère le nom du fichier rpsblast+ dans un tuple dans une liste
    connecteur.close()

    return cdsearch_file



#######################################################################################
# Mises à jour des tables                                                             #
#######################################################################################


def DownloadProteome(ftp):
    """Télécharge un proteome depuis un lien FTP
    input : ftp (str) : lien FTP du proteome
    output : proteome_file (str) : nom du fichier proteome téléchargé"""

    download_path = "https" + ftp[3:] #on remplace le 'ftp' par 'https
    proteome_file = download_path.split("/")[9] + "_translated_cds.faa.gz" 
    download_path = download_path + "/" + proteome_file

    os.system(f"wget {download_path}") #téléchargement
    os.system(f"gunzip {proteome_file}") #extraction

    proteome_file = proteome_file[:-3] #on enlève le '.gz'

    os.system(f"mv {proteome_file} Proteomes/") #changer le répertoire 

    return proteome_file


def MajBaseProcaryotes(espece_name, assembly, ftp_link, proteome_file, cdsearch):
    """Met à jour la table Procaryotes
    input1 : espece_name (str) : nom de l'espèce
    input2 : assembly (str) : code assembly de l'espèce
    input3 : ftp_link (str) : lien FTP de l'espèce
    input4 : proteome_file (str) : nom du fichier proteome téléchargé"""
    connecteur = pg.connect(host=host, dbname=dbname, user=user, password=password) 
    cur = connecteur.cursor()
    cur.execute(f"INSERT INTO procaryotes (espece, assembly, ftplink, proteome, cdsearch) VALUES ('{espece_name}', '{assembly}', '{ftp_link}', '{proteome_file}', '{cdsearch}');") 
    connecteur.commit() #appliquer les modifications dans la base de données
    connecteur.close()
    return 


def TestIfBlastExists(espece_name1, espece_name2):
    """Teste si un blast a déjà été effectué entre deux espèces
    input1 : espece_name1 (str) : nom de la première espèce
    input2 : espece_name2 (str) : nom de la deuxième espèce
    output : 0 si le blast n'existe pas, le nom du fichier blast sinon"""
    connecteur = pg.connect(host=host, dbname=dbname, user=user, password=password) 
    cur = connecteur.cursor()
    cur.execute(f"SELECT blastfile FROM blast WHERE espece1 = '{espece_name1}' AND espece2 = '{espece_name2}';") 
    res = cur.fetchall()
    connecteur.close()

    if res == []:
        return 0
    else:
        return res[0][0]


def MajBaseBlast(espece_name1, espece_name2, blast_file):
    """Met à jour la table Blast
    input1 : espece_name1 (str) : nom de la première espèce
    input2 : espece_name2 (str) : nom de la deuxième espèce
    input3 : blast_file (str) : nom du fichier blast"""
    connecteur = pg.connect(host=host, dbname=dbname, user=user, password=password) 
    cur = connecteur.cursor()
    cur.execute(f"INSERT INTO blast (espece1, espece2, blastfile) VALUES ('{espece_name1}', '{espece_name2}', '{blast_file}');") 
    connecteur.commit() 
    connecteur.close()
    return





## Modifier le fichier prokaryotes_complete-genomes.csv afin qu'il ne contienne que des liens ftp contenants des liens "translated_cds"

# import requests


# file = "prokaryotes_complete-genomes.csv"
# new_file = "prokaryotes_complete-genomes_downloadable.csv"

# c = 0
# t = 0

# with open(file, "r") as f:
#     with open(new_file, "w") as f_new:
#         for i, line in enumerate(f.readlines()):

#             print(f"Vérification du {i}e lien")

#             if i == 0:
#                 f_new.write(line)
#                 continue

#             ftp_link = line.split(",")[14]

#             download_path = "https" + ftp_link[4:][:-1] #on remplace le 'ftp' par 'https + on enlève '\n'

#             proteome_file = download_path.split("/")[9] + "_translated_cds.faa.gz" 
#             download_path = download_path + "/" + proteome_file

#             rep = requests.head(download_path)
#             if rep.status_code == 200:
#                 f_new.write(line)
#                 t += 1
#                 print(f"Lien valide, total des téléchargements possible : {t}")
#             print("Vérification effectuée")

# print(c)
# print(t)