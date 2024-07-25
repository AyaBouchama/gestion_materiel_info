import sys
import os


# Assurez-vous que le chemin est correctement spécifié
sys.path.insert(0, r"C:\Users\Bouchama\Documents\newinfo\Flask_App")

from app import app as application

if __name__ == "__main__":
    application.run()
