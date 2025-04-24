import pandas as pd
df = pd.read_csv("data.csv")
df = df.drop_duplicates()
df = df.dropna(subset=['modele'])
df = df.dropna(subset=['annee'])
df['annee'] = df['annee'].astype(int)
df['places'] = df['places'].replace('N/D', 'N/O')
df['portes'] = df['portes'].replace('N/D', 'N/O')
df['marque'] = df['marque'].str.capitalize()
df['marque'] = df['marque'].replace('Mercedes', 'Mercedes-Benz')
df['marque'] = df['marque'].replace('Mercedes-amg', 'Mercedes-AMG')
df['marque'] = df['marque'].replace('Alfa-romeo', 'Alfa Romeo')
df['marque'] = df['marque'].replace('Rolls-royce', 'Rolls-Royce')
df['marque'] = df['marque'].replace('Bmw', 'BMW')
df['marque'] = df['marque'].replace('Gmc', 'GMC')
df['marque'] = df['marque'].replace('Mini', 'MINI')
df['carrosserie'] = df['carrosserie'].replace('Berline', 'Sedan')
df['carrosserie'] = df['carrosserie'].replace('Utilitaire Sportif', 'SUV')
df['carrosserie'] = df['carrosserie'].replace('Coupé', 'Coupe')
df['carrosserie'] = df['carrosserie'].replace('À hayon', 'Hatchback')
df['carrosserie'] = df['carrosserie'].replace('Décapotable', 'Convertible')
df['carrosserie'] = df['carrosserie'].replace('Familiale', 'Wagon')
df['carrosserie'] = df['carrosserie'].replace('Camionnette', 'Pickup')
df['carrosserie'] = df['carrosserie'].replace('Mini-fourgonnette', 'Minivan')
df['carrosserie'] = df['carrosserie'].replace('Fourgonnette', 'Minivan')
df['carrosserie'] = df['carrosserie'].replace('Coupé Sport', 'Coupe')
df['carrosserie'] = df['carrosserie'].replace('Roadster', 'Coupe')
df['carrosserie'] = df['carrosserie'].replace('Coupé/Roadster', 'Coupe')
df['carrosserie'] = df['carrosserie'].replace('Intermédiaire', 'Sedan')
df['carrosserie'] = df['carrosserie'].replace('Pleine grandeur', 'Sedan')
df['carrosserie'] = df['carrosserie'].replace('Sous-compacte', 'Hatchback')
df['carrosserie'] = df['carrosserie'].replace('Sport', 'Coupe')
df['carrosserie'] = df['carrosserie'].replace('N/O', 'Other')
df['modele'] = df['modele'].str.upper()
def simplifier_transmission(val):
    if pd.isna(val):
        return val
    val_lower = val.lower()
    if "n/o" in val_lower or "other" in val_lower:
        return "N/O"
    elif "automatique" in val_lower:
        return "Automatique"
    else:
        return "Manuelle"
df["transmission"] = df["transmission"].astype(str).apply(simplifier_transmission)
df.to_csv("data_auto123_normalized.csv", index=False)