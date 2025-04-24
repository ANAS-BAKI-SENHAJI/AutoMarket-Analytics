import pandas as pd
df = pd.read_csv("airflow/data/data_autohebdo.csv")
df = df.dropna(subset=['kilometrage'])
df['carrosserie'] = df['carrosserie'].replace('SUV, Crossover', 'SUV')
df['carrosserie'] = df['carrosserie'].replace('Minivan, Van', 'Minivan')
df['carrosserie'] = df['carrosserie'].replace('Pickup Truck', 'Pickup')
df['carrosserie'] = df['carrosserie'].replace('Coupe (2 door)', 'Coupe')
df['modele'] = df['modele'].str.upper()
def simplifier_transmission(val):
    if pd.isna(val):
        return val
    val_lower = val.lower()
    if "n/o" in val_lower or "other" in val_lower:
        return "N/O"
    elif "automatic" in val_lower:
        return "Automatique"
    elif "semi-Aatomatic" in val_lower:
        return "Automatique"
    elif "manual" in val_lower:
        return "Manuelle"
    else:
        return "N/O"
df["transmission"] = df["transmission"].astype(str).apply(simplifier_transmission)
df['kilometrage'] = df['kilometrage'].apply(lambda x: int(x) if pd.notna(x) else x)
df['prix'] = df['prix'].apply(lambda x: int(x) if pd.notna(x) else x)
df['date_rafraichi'] = pd.to_datetime(df['date_rafraichi'], format="%Y-%m-%d", errors='coerce')
df.to_csv("airflow/data/data_autohebdo_normalized.csv", index=False)

df = pd.read_csv("airflow/data/data_kijiji.csv")
df['carrosserie'] = df['carrosserie'].replace('SUV, Crossover', 'SUV')
df['carrosserie'] = df['carrosserie'].replace('Minivan, Van', 'Minivan')
df['carrosserie'] = df['carrosserie'].replace('Pickup Truck', 'Pickup')
df['carrosserie'] = df['carrosserie'].replace('Coupe (2 door)', 'Coupe')
df['modele'] = df['modele'].str.upper()
df['prix'] = df['prix'].apply(lambda x: int(x) if pd.notna(x) else x)
df = df.dropna(subset=['kilometrage'])
df['kilometrage'] = df['kilometrage'].apply(lambda x: int(x) if pd.notna(x) else x)
def simplifier_transmission(val):
    if pd.isna(val):
        return val
    val_lower = val.lower()
    if "n/o" in val_lower or "other" in val_lower:
        return "N/O"
    elif "automatic" in val_lower:
        return "Automatique"
    elif "semi-Aatomatic" in val_lower:
        return "Automatique"
    elif "manual" in val_lower:
        return "Manuelle"
    else:
        return "N/O"
df["transmission"] = df["transmission"].astype(str).apply(simplifier_transmission)
df.to_csv("airflow/data/data_kijiji_normalized.csv", index=False)