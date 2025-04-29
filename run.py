from app import app
import os
from dotenv import load_dotenv

# Charge les variables d'environnement depuis .env
load_dotenv()  

if __name__ == "__main__":
    # Configuration avec valeurs par défaut ou depuis .env
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1").lower() in ("1", "true", "yes")
    
    app.run(host=host, port=port, debug=debug)