-- Remplissage des tables Procaryotes et Blast lors de la premiere connexion à la base de donnees

INSERT INTO Procaryotes(espece, assembly, ftplink, proteome, cdsearch) VALUES
('Escherichia coli str. K-12 substr. MG1655', 'GCA_000005845.2',
'ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/005/845/GCA_000005845.2_ASM584v2',
'GCA_002843685.1_ASM284368v1_translated_cds.faa', 'rpsblast_QUERY-GCA_002843685.1_DB-Cdd_NCBI.out'),
('Escherichia coli IAI1', 'GCA_000026265.1', 'ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/026/265/GCA_000026265.1_ASM2626v1',
'GCA_000026265.1_ASM2626v1_translated_cds.faa', 'rpsblast_QUERY-GCA_000026265.1_DB-Cdd_NCBI.out'),
('Ramlibacter tataouinensis', 'GCA_001580455.1', 'ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/001/580/455/GCA_001580455.1_ASM158045v1',
'GCA_001580455.1_ASM158045v1_translated_cds.faa', 'rpsblast_QUERY-GCA_001580455.1_DB-Cdd_NCBI.out'),
('Ramlibacter tataouinensis TTB310', 'GCA_000215705.1', 'ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/215/705/GCA_000215705.1_ASM21570v1',
'GCA_000215705.1_ASM21570v1_translated_cds.faa', 'rpsblast_QUERY-GCA_000215705.1_DB-Cdd_NCBI.out'),
('Magnetococcus marinus MC-1', 'GCA_000014865.1', 'ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/014/865/GCA_000014865.1_ASM1486v1', 
'GCA_000014865.1_ASM1486v1_translated_cds.faa', 'rpsblast_QUERY-GCA_000014865.1_DB-Cdd_NCBI.out'),
('Magnetospirillum magneticum AMB-1', 'GCA_000009985.1', 'ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/009/985/GCA_000009985.1_ASM998v1',
'GCA_000009985.1_ASM998v1_translated_cds.faa', 'rpsblast_QUERY-GCA_000009985.1_DB-Cdd_NCBI.out')
