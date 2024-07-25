from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Remplacez par une clé secrète réelle

# Connexion à la base de données

maBase = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bouchamaaya2004.",
    database="gestionmaterielinformatique"
)
meConnect = maBase.cursor()

@app.route('/')
def index():
    try:
        meConnect.execute("SELECT Materiel.type, Materiel.emplacement, Materiel.numero_serie, Materiel.modele, Etablissement.ID_Gresa, Materiel.materiel_id, Etablissement.date_distribution, Etablissement.nobre_materiel FROM Materiel JOIN Etablissement ON Materiel.materiel_id = Etablissement.materiel_id")
        data = meConnect.fetchall()
        return render_template('index.html', data=data)
    except mysql.connector.Error as err:
        flash(f"Erreur lors de la récupération des données : {err}", "error")
        return render_template('index.html', data=None)  # Gérer le cas où il y a une erreur

@app.route('/add', methods=['POST'])
def ajouter():
    type_materiel = request.form['type_materiel']
    numero_serie = request.form['numero_serie']
    emplacement = request.form['emplacement']
    modele = request.form['modele']
    id_gresa = request.form['id_gresa']
    date_str = request.form['date_distribution']
    nobre_materiel = request.form['nobre_materiel']

    try:
        sql_materiel = "INSERT INTO Materiel (type, numero_serie, emplacement, modele) VALUES (%s, %s, %s, %s)"
        val_materiel = (type_materiel, numero_serie, emplacement, modele)
        meConnect.execute(sql_materiel, val_materiel)
        materiel_id = meConnect.lastrowid

        date_distribution = datetime.strptime(date_str, "%d/%m/%Y").date()
        sql_etablissement = "INSERT INTO Etablissement (ID_Gresa, materiel_id, date_distribution, nobre_materiel) VALUES (%s, %s, %s, %s)"
        val_etablissement = (id_gresa, materiel_id, date_distribution, nobre_materiel)
        meConnect.execute(sql_etablissement, val_etablissement)
        
        maBase.commit()
        flash("Matériel et établissement ajoutés avec succès", "success")
    except ValueError:
        flash("Format de date invalide. Utilisez jj/mm/aaaa", "error")
    except mysql.connector.Error as err:
        flash(f"Erreur lors de l'ajout : {err}", "error")

    return redirect(url_for('index'))



@app.route('/modifier/<int:materiel_id>', methods=['GET', 'POST'])
def modifier(materiel_id):
    if request.method == 'POST':
        # Récupération des données du formulaire
        type_materiel = request.form['type_materiel']
        numero_serie = request.form['numero_serie']
        emplacement = request.form['emplacement']
        modele = request.form['modele']
        id_gresa = request.form['id_gresa']
        date_str = request.form['date_distribution']
        nobre_materiel = request.form['nobre_materiel']

        try:
            # Convertir la chaîne de date en objet datetime.date
            date_distribution = datetime.strptime(date_str, "%d/%m/%Y").date()

            # Mettre à jour la table Materiel
            sql_materiel = """
                UPDATE Materiel
                SET type=%s, numero_serie=%s, emplacement=%s, modele=%s
                WHERE materiel_id=%s
            """
            val_materiel = (type_materiel, numero_serie, emplacement, modele, materiel_id)
            meConnect.execute(sql_materiel, val_materiel)

            # Mettre à jour la table Etablissement
            sql_etablissement = """
                UPDATE Etablissement
                SET ID_Gresa=%s, date_distribution=%s, nobre_materiel=%s
                WHERE materiel_id=%s
            """
            val_etablissement = (id_gresa, date_distribution, nobre_materiel, materiel_id)
            meConnect.execute(sql_etablissement, val_etablissement)

            maBase.commit()
            flash('Enregistrement modifié avec succès', 'success')
            return redirect(url_for('index'))

        except ValueError:
            flash('Format de date invalide. Utilisez jj/mm/aaaa', 'error')
        except mysql.connector.Error as err:
            flash(f'Erreur lors de la modification : {err}', 'error')
        
        maBase.rollback()

    # Récupérer les informations actuelles pour le formulaire
    meConnect.execute("SELECT * FROM Materiel WHERE materiel_id=%s", (materiel_id,))
    materiel = meConnect.fetchone()

    meConnect.execute("SELECT * FROM Etablissement WHERE materiel_id=%s", (materiel_id,))
    etablissement = meConnect.fetchone()

    if materiel and etablissement:
        return render_template('modifier.html', materiel=materiel, etablissement=etablissement)
    else:
        flash('Aucun matériel trouvé avec cet ID', 'warning')
        return redirect(url_for('index'))



@app.route('/supprimer/<int:materiel_id>', methods=['POST'])
def supprimer(materiel_id):
    try:
        sql_etablissement = "DELETE FROM Etablissement WHERE materiel_id=%s"
        val_etablissement = (materiel_id,)
        meConnect.execute(sql_etablissement, val_etablissement)
        
        sql_materiel = "DELETE FROM Materiel WHERE materiel_id=%s"
        val_materiel = (materiel_id,)
        meConnect.execute(sql_materiel, val_materiel)
        
        maBase.commit()
        flash("Enregistrement supprimé avec succès", "success")
    except mysql.connector.Error as err:
        flash(f"Erreur lors de la suppression : {err}", "error")
    
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def rechercher():
    numero_serie = request.form['numero_serie']

    try:
        sql = "SELECT Materiel.emplacement, Etablissement.ID_Gresa FROM Materiel JOIN Etablissement ON Materiel.materiel_id = Etablissement.materiel_id WHERE Materiel.numero_serie = %s"
        val = (numero_serie,)
        meConnect.execute(sql, val)
        result = meConnect.fetchone()
        
        if result:
            emplacement, id_gresa = result
            flash(f"Emplacement: {emplacement}, ID Gresa: {id_gresa}", "success")
        else:
            flash("Aucun matériel trouvé avec ce numéro de série", "warning")
    except mysql.connector.Error as err:
        flash(f"Erreur lors de la recherche : {err}", "error")

    return redirect(url_for('index'))



@app.route('/imprimer/<int:materiel_id>', methods=['GET'])
def imprimer(materiel_id):
    try:
        sql = "SELECT Materiel.type, Materiel.numero_serie, Materiel.modele,  Materiel.emplacement, Etablissement.ID_Gresa, Etablissement.date_distribution, Etablissement.nobre_materiel FROM Materiel JOIN Etablissement ON Materiel.materiel_id = Etablissement.materiel_id WHERE Materiel.materiel_id = %s"
        
        val = (materiel_id,)
        meConnect.execute(sql, val)
        materiel = meConnect.fetchone()
        
        # Debug: Affichez les résultats de la requête
        print(materiel)
        
        if materiel:
            now = datetime.now()
            return render_template('impression.html', materiel=materiel, now=now)
        else:
            flash("Aucun matériel trouvé avec cet ID", "warning")
    except mysql.connector.Error as err:
        flash(f"Erreur lors de l'impression : {err}", "error")

    return redirect(url_for('index'))



