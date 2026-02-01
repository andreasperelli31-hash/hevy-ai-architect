# 🏋️‍♂️ Hevy AI Architect

Generatore intelligente di schede di allenamento personalizzate basato su AI.

## Funzionalità

- 🎯 **Obiettivi multipli**: Ipertrofia, Dimagrimento, Forza, Postura, Resistenza
- 📊 **Personalizzazione completa**: Età, sesso, livello, attrezzatura disponibile
- 🧠 **AI avanzata**: Utilizza Google Gemini per generare schede scientificamente valide
- 📄 **Export PDF**: Scarica la tua scheda in formato PDF
- 💾 **Preferenze salvate**: Ricorda le tue impostazioni tra le sessioni

## Demo Online

🌐 **[Prova l'app online](https://hevy-ai-architect.streamlit.app)**

## Installazione Locale

```bash
# Clona il repository
git clone https://github.com/TUOUSERNAME/hevy-ai-architect.git
cd hevy-ai-architect

# Installa le dipendenze
pip install -r requirements.txt

# Imposta la tua API key
export GEMINI_API_KEY="la-tua-api-key"

# Avvia l'app
streamlit run app.py
```

## Configurazione API Key

1. Vai su [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Crea una nuova API key
3. Imposta la variabile d'ambiente `GEMINI_API_KEY`

## Deploy su Streamlit Cloud

1. Fai fork di questo repository
2. Vai su [share.streamlit.io](https://share.streamlit.io)
3. Collega il tuo repository GitHub
4. Nelle impostazioni dell'app, aggiungi il secret:
   ```
   GEMINI_API_KEY = "la-tua-api-key"
   ```

## Tecnologie

- **Frontend**: Streamlit
- **AI**: Google Gemini API
- **PDF**: FPDF
- **Data**: Pandas

## Licenza

MIT License - Usa liberamente per scopi personali e commerciali.
