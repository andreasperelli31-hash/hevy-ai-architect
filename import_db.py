import requests
import pandas as pd
import json

# URL del database Open Source
DB_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"

def download_and_convert():
    print("⏳ Scaricamento del database esercizi da GitHub...")
    
    try:
        response = requests.get(DB_URL)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Scaricati {len(data)} esercizi grezzi.")
        print("🧹 Inizio pulizia dati...")
        
        clean_exercises = []
        
        for item in data:
            # 1. Gestione sicura dei MUSCOLI (se manca, mettiamo 'Full Body')
            muscles = item.get("primaryMuscles")
            primary_muscle = muscles[0].title() if muscles and len(muscles) > 0 else "Full Body"

            # 2. Gestione sicura dell'ATTREZZATURA (se è None, diventa 'Body Only')
            equip_raw = item.get("equipment")
            if equip_raw is None:
                equip_raw = "body_only"
            equipment = equip_raw.replace("_", " ").title()

            # 3. Gestione sicura del TIPO (se è None, diventa 'Compound')
            mech_raw = item.get("mechanic")
            if mech_raw is None:
                mech_raw = "compound"
            mech_type = mech_raw.title()

            # Costruzione riga
            exercise = {
                "id": item.get("id", "N/A"),
                "name": item.get("name", "Unknown").title(),
                "muscle_group": primary_muscle,
                "equipment": equipment,
                "type": mech_type
            }
            
            # Pulizia finale nomi attrezzi
            if exercise["equipment"] == "Body Only":
                exercise["equipment"] = "Bodyweight"
            
            clean_exercises.append(exercise)
            
        # Creazione DataFrame
        df = pd.DataFrame(clean_exercises)
        
        # Salvataggio CSV
        output_file = "exercises_db.csv"
        df.to_csv(output_file, index=False)
        
        print(f"\n🎉 SUCCESSO! Database creato: {output_file}")
        print(f"📊 Totale esercizi pronti: {len(df)}")
        print("➡️  Ora puoi lanciare: streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Errore critico: {e}")

if __name__ == "__main__":
    download_and_convert()