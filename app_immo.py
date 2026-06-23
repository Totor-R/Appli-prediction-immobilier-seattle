import sys
import random
import joblib
import sqlite3
from datetime import datetime
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFormLayout, 
                             QLineEdit, QPushButton, QLabel, QScrollArea, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt

class ImmoPredictor(QWidget):
    def __init__(self):
        super().__init__()
        
        self.features = [
            'bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'floors', 
            'waterfront', 'view', 'condition', 'sqft_above', 'sqft_basement', 
            'yr_built', 'yr_renovated'
        ]

        self.traductions = {
            'bedrooms': 'Nombre de chambres',
            'bathrooms': 'Nombre de salles de bain',
            'sqft_living': 'Surface habitable (sqft)',
            'sqft_lot': 'Surface du terrain (sqft)',
            'floors': 'Nombre d\'étages',
            'waterfront': 'Vue sur l\'eau (0=Non, 1=Oui)',
            'view': 'Note de la vue (0 à 4)',
            'condition': 'État général (1 à 5)',
            'sqft_above': 'Surface au-dessus du sol (sqft)',
            'sqft_basement': 'Surface du sous-sol (sqft)',
            'yr_built': 'Année de construction',
            'yr_renovated': 'Année de rénovation (0 si jamais)'
        }

        self.initUI()
        self.init_database()
        self.charger_historique_visuel()
        
        try:
            self.model = joblib.load("modele_immo.joblib")
        except Exception as e:
            print(f"Erreur lors du chargement du modèle : {e}")
            sys.exit()

    def init_database(self):
        conn = sqlite3.connect("immo_history.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historique_estimations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_simulation TEXT,
                bedrooms REAL,
                bathrooms REAL,
                sqft_living REAL,
                sqft_lot REAL,
                floors REAL,
                waterfront REAL,
                view REAL,
                condition REAL,
                sqft_above REAL,
                sqft_basement REAL,
                yr_built REAL,
                yr_renovated REAL,
                prix_predit REAL
            )
        """)
        conn.commit()
        conn.close()

    def initUI(self):
        self.setWindowTitle("IA Estimator - Immobilier Seattle")
        self.setGeometry(100, 100, 500, 750)

        main_layout = QVBoxLayout()
        
        self.label_titre = QLabel("🏠 Estimation de Prix par l'IA")
        self.label_titre.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.label_titre)

        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.form_layout = QFormLayout()
        self.inputs = {}

        for f in self.features:
            le = QLineEdit()
            le.setText("0") 
            nom_francais = self.traductions[f]
            self.form_layout.addRow(QLabel(nom_francais + " :"), le)
            self.inputs[f] = le

        scroll_widget.setLayout(self.form_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        self.btn_random = QPushButton("🎲 GÉNÉRER AU HASARD")
        self.btn_random.clicked.connect(self.generer_hasard)
        main_layout.addWidget(self.btn_random)

        self.btn_predict = QPushButton("🚀 OBTENIR L'ESTIMATION")
        self.btn_predict.clicked.connect(self.lancer_prediction)
        main_layout.addWidget(self.btn_predict)

        self.resultat = QLineEdit()
        self.resultat.setReadOnly(True)
        self.resultat.setPlaceholderText("Le prix apparaîtra ici...")
        self.resultat.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.resultat)

        main_layout.addWidget(QLabel("📋 Dernières estimations enregistrées (SQL) :"))
        self.table_historique = QTableWidget()
        self.table_historique.setColumnCount(4)
        self.table_historique.setHorizontalHeaderLabels(["Date", "Chambres", "Surface", "Prix Prédit"])
        self.table_historique.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.table_historique)

        self.setLayout(main_layout)

    def charger_historique_visuel(self):
        try:
            conn = sqlite3.connect("immo_history.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date_simulation, bedrooms, sqft_living, prix_predit 
                FROM historique_estimations 
                ORDER BY id DESC LIMIT 5
            """)
            lignes = cursor.fetchall()
            conn.close()

            self.table_historique.setRowCount(len(lignes))
            for i, ligne in enumerate(lignes):
                date_short = ligne[0][5:16] if ligne[0] else ""
                self.table_historique.setItem(i, 0, QTableWidgetItem(date_short))
                self.table_historique.setItem(i, 1, QTableWidgetItem(str(int(ligne[1]))))
                self.table_historique.setItem(i, 2, QTableWidgetItem(f"{int(ligne[2])} sqft"))
                self.table_historique.setItem(i, 3, QTableWidgetItem(f"{ligne[3]:,.0f} $"))
        except Exception as e:
            print(f"Erreur chargement tableau : {e}")

    def generer_hasard(self):
        chambres = random.randint(1, 5)
        surface_habitable = chambres * random.randint(500, 750)
        
        if chambres == 1:
            salles_de_bain = 1
        else:
            salles_de_bain = random.randint(chambres - 1, chambres)

        # CORRECTION : On sécurise le calcul du sous-sol pour éviter les bornes inversées
        a_un_sous_sol = random.choice([False, False, True])
        max_sous_sol = int(surface_habitable * 0.4)
        
        if a_un_sous_sol and max_sous_sol > 300:
            sous_sol = random.randint(300, max_sous_sol)
            au_dessus_du_sol = surface_habitable - sous_sol
        else:
            sous_sol = 0
            au_dessus_du_sol = surface_habitable

        terrain = surface_habitable * random.randint(2, 6)
        etages = 1 if surface_habitable < 1500 else random.randint(1, 2)
        vue_eau = random.choice([0, 0, 0, 0, 0, 1]) 
        note_vue = random.randint(1, 4) if vue_eau == 1 else 0
        etat = random.randint(3, 5) 
        annee_construction = random.randint(1930, 2026)
        annee_renovation = random.choice([0, 0, random.randint(2000, 2026)])

        valeurs_hasard = {
            'bedrooms': str(chambres),
            'bathrooms': str(salles_de_bain),
            'sqft_living': str(surface_habitable),
            'sqft_lot': str(terrain),
            'floors': str(etages),
            'waterfront': str(vue_eau),
            'view': str(note_vue),
            'condition': str(etat),
            'sqft_above': str(au_dessus_du_sol),
            'sqft_basement': str(sous_sol),
            'yr_built': str(annee_construction),
            'yr_renovated': str(annee_renovation)
        }

        for f in self.features:
            self.inputs[f].setText(valeurs_hasard[f])

        self.resultat.setText("")
        self.resultat.setPlaceholderText("Nouvelles valeurs cohérentes ! Cliquez sur estimer 🚀")

    def lancer_prediction(self):
        try:
            valeurs = []
            for f in self.features:
                val = float(self.inputs[f].text())
                valeurs.append(val)

            if valeurs[2] == 0:
                self.resultat.setText("0.00 $")
                return

            maison_df = pd.DataFrame([valeurs], columns=self.features)
            prix_estime = self.model.predict(maison_df)[0]
            self.resultat.setText(f"{prix_estime:,.2f} $")

            try:
                conn = sqlite3.connect("immo_history.db")
                cursor = conn.cursor()
                date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                donnees_a_inserer = [date_actuelle] + valeurs + [float(prix_estime)]
                
                cursor.execute("""
                    INSERT INTO historique_estimations (
                        date_simulation, bedrooms, bathrooms, sqft_living, sqft_lot, 
                        floors, waterfront, view, condition, sqft_above, 
                        sqft_basement, yr_built, yr_renovated, prix_predit
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, donnees_a_inserer)
                
                conn.commit()
                conn.close()
                self.charger_historique_visuel()
                
            except Exception as e:
                print(f"Erreur lors de l'écriture SQL : {e}")

        except ValueError:
            self.resultat.setText("⚠️ Erreur : Entrez des nombres !")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImmoPredictor()
    window.show()
    sys.exit(app.exec_())
