Téléchargement des packages :
Pour télécharger les packages, faire :

pip install -r application/requirements.txt

ou faire :

pip install -r application/requirements.txt --user

Lancement du serveur et mise en place de la base de donnée:
Ouvrir l'application pgadmin

Démarrer le serveur

Lancer une nouvelle connection avec :

Remplir le fichier avec ces informations :

 Nom: Choisir un nom  pour la connection 
 Hôte: localhost 
 Port: 5437
 Nom utilisateur: pgis 
 Mot de passe: pgis
Création de la base de donnée en faisant un clique droit sur base de données, puis cliquer sur Ajouter une base de données.

!!! Choisir le nom MD pour la base de données !!! (Pour correspondre avec le paramétrage de l'application python et permet donc un GET et un POST des données)

Faire un clique droit sur la base de données précédement crée puis amller sur restaurer et parcourir le dossier de l'application pour se trouver dans "H:\SAE_finale\Analyse-et-conception-d-un-outil-d-cisionnel-\base_de_donnee" et prendre le fichier "MaisonDuDroit_bd_avec_donnees_final.backup"
Insertion des données dans la table entretien, demande à l'aide de la commande :
& "D:\tools\pgsql-12.5-win64\bin\psql.exe" -U pgis -d MD -p 5437 -f data.sql

Insertion des données dans la table solution avec le code :
SET client_encoding = 'WIN1252';

INSERT INTO public.solution (num, pos, nature) VALUES (413, 3, '2a'), (435, 3, '7c'), (446, 3, '9b'), (463, 3, '1j'), (483, 3, '9a'), (510, 3, '8c'), (523, 3, '4c'), (548, 3, '7b'), (549, 3, '9b'), (550, 3, '9b'), (553, 3, '1d'), (594, 3, '9b'), (683, 3, '1c'), (730, 3, '1d'), (739, 3, '7b'), (744, 3, '1c'), (750, 3, '1g'), (752, 3, '9b'), (754, 3, '9b');

Changement de la taille de la variable origine de la table entretien :
ALTER TABLE public.entretien ALTER COLUMN origine TYPE character varying(50);

Lancement des test unitaires, web
Pour lancer l 'application:

streamlit run app.py

ou

python -m streamlit run app.py

Pour lancer les test web :

python test_web/Selenium_test_web.py

Pour lancer les tests unitaires :

pytest tests_unitaires/ --cov=application

ou

python -m pytest tests_unitaires/ --cov=application

Changement de la base de donnée:

TRUNCATE TABLE public.demande, public.solution, public.entretien RESTART IDENTITY CASCADE;

Mise en place de la base de donnée sur supabase :

1.Sécurité RLS et activation des Policies :

-- 1. Activation du RLS pour les tables de données ALTER TABLE public.entretien ENABLE ROW LEVEL SECURITY; ALTER TABLE public.demande ENABLE ROW LEVEL SECURITY; ALTER TABLE public.solution ENABLE ROW LEVEL SECURITY;

-- 2. Création des politiques d'accès (Lecture et Écriture pour l'API) -- Note : 'anon' est le rôle utilisé par défaut par votre clé publique Supabase.

-- Pour la table entretien CREATE POLICY "Autoriser lecture pour l'API" ON public.entretien FOR SELECT TO anon USING (true); CREATE POLICY "Autoriser insertion pour l'API" ON public.entretien FOR INSERT TO anon WITH CHECK (true);

-- Pour la table demande CREATE POLICY "Autoriser lecture pour l'API" ON public.demande FOR SELECT TO anon USING (true); CREATE POLICY "Autoriser insertion pour l'API" ON public.demande FOR INSERT TO anon WITH CHECK (true);

-- Pour la table solution CREATE POLICY "Autoriser lecture pour l'API" ON public.solution FOR SELECT TO anon USING (true); CREATE POLICY "Autoriser insertion pour l'API" ON public.solution FOR INSERT TO anon WITH CHECK (true);

-- 3. Rendre les tables de métadonnées lisibles ALTER TABLE public.modalite ENABLE ROW LEVEL SECURITY; CREATE POLICY "Lecture publique" ON public.modalite FOR SELECT TO anon USING (true);

-- 1. Synchroniser le compteur des entretiens (numéro 783 actuellement le plus haut) SELECT setval('public.entretien_num_seq', (SELECT MAX(num) FROM public.entretien));

-- 2. Synchroniser le compteur des agglomérations SELECT setval('public.agglo_code_a_seq', (SELECT MAX(code_a) FROM public.agglo));

-- 3. Synchroniser le compteur des communes SELECT setval('public.commune_code_c_seq', (SELECT MAX(code_c) FROM public.commune));

-- 4. Synchroniser le compteur des quartiers SELECT setval('public.quartier_code_q_seq', (SELECT MAX(code_q) FROM public.quartier));

-- 5. Synchroniser le compteur des rubriques SELECT setval('public.rubrique_pos_seq', (SELECT MAX(pos) FROM public.rubrique));

-- Ajout des colonnes de géolocalisation à la table COMMUNE ALTER TABLE public.commune ADD COLUMN IF NOT EXISTS lat FLOAT, ADD COLUMN IF NOT EXISTS lon FLOAT;

-- Vérification : la table COMMUNE contient les noms issus de vos données historiques SELECT nom_c, lat, lon FROM public.commune LIMIT 5;

SI les colonnes lat et lon de la base de données Supabase sont vides, faire :

python enrichir_coords.py