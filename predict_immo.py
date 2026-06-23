import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv("data.csv")
df = df.dropna()

# On vire les lignes aberrantes où le prix vaut 0 $
df = df[df['price'] > 0]

features = [
    'bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'floors', 
    'waterfront', 'view', 'condition', 'sqft_above', 'sqft_basement', 
    'yr_built', 'yr_renovated'
]
X = df[features]
y = df['price']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modele = RandomForestRegressor(n_estimators=100, random_state=42)
modele.fit(X_train, y_train)

# On calcule le nouveau score d'examen
score = modele.score(X_test, y_test)
print(f"Précision du modèle (R²) : {score:.2f}")

joblib.dump(modele, "modele_immo.joblib", compress=3)
print("Cerveau de l'IA sauvegardé avec succès !")

maison_mystere = pd.DataFrame([[3, 2, 1500, 5000, 1, 0, 0, 3, 1500, 0, 1980, 0]], columns=features)
prediction = modele.predict(maison_mystere)
print(f"🏠 Pour cette maison, l'IA estime son prix à : {prediction[0]:,.2f} $")
