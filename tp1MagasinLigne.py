from flask import Flask, render_template, request, redirect, session

from bd import ouvrir_connexion

app = Flask(__name__)
app.secret_key = "JeSuisUneCleSecreteChutFautPasLeDire"

def estConnecter():
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()
        if ("utilisateur" not in session):
            return False
        id = session["utilisateur"]
        curseur.execute("SELECT * FROM utilisateur WHERE id = %s", (id,))
        unUtilisateur = curseur.fetchone()
        if (unUtilisateur == None):
            return False
        if (unUtilisateur[3] == 1 or unUtilisateur[3] == 0):
            return True
    finally:
        connexion.close()

def estAdmin():
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()
        id = session["utilisateur"]
        curseur.execute("SELECT * FROM utilisateur WHERE id = %s", (id,))
        unUtilisateur = curseur.fetchone()
        if (unUtilisateur[3] == 0):
            return False
        if (unUtilisateur[3] == 1):
            return True
    finally:
        connexion.close()

@app.route("/")
def index():
    if (estConnecter() == True):
        if (estAdmin() == True):
            return redirect("/admin_menu")
        if (estAdmin() == False):
            return redirect("/list_magasin")
    if (estConnecter() == False):
        return redirect("/authentifier_utilisateurs")

@app.route("/authentifier_utilisateurs")
def AfficherAuthentifierUilisateurs():
    return render_template("authentificationUtilisateur.html")

@app.route("/authentifier_utilisateurs", methods=["POST"])
def authentifier_utilisateurs():
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()

        nom = request.form["nom"]
        mdp = request.form["mdp"]
        admin = request.form["admin"]

        curseur.execute("SELECT * FROM utilisateur WHERE nom=%s AND mdp=%s AND administrateur=%s;", (nom, mdp, admin))
        unUtilisateur = curseur.fetchone()

        if (unUtilisateur == None):
            return redirect("/authentifier_utilisateurs")
        else:
            id = unUtilisateur[0]
            session["utilisateur"] = id
            if (unUtilisateur[3] == 1):
                return redirect("/admin_menu")
            else:
                return redirect("/list_magasin")
    finally:
        connexion.close()

@app.route("/authentifier_utilisateurs/deconnexion")
def deconnexion():
    session.pop('utilisateur', None)
    return redirect("/authentifier_utilisateurs")

@app.route("/lister_utilisateurs")
def lister_utilisateurs():
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()

        if (estConnecter() == True):
            if (estAdmin() == True):
                # connecter en admin
                curseur.execute("SELECT * FROM utilisateur")
                lstUtilisateurs = curseur.fetchall()
                return render_template("listUtilisateurs.html", lstUtilisateurs = lstUtilisateurs)
            else:
                return render_template("page403.html"), 403
        else:
            return render_template("page403.html"), 403
    finally:
        connexion.close()

@app.route("/creer_utilisateur")
def AfficherPage():
    if (estConnecter() == True):
        if (estAdmin() == True):
            # connecter en admin
            return render_template("creerUtilisateur.html")
        else:
            return render_template("page403.html"), 403
    else:
        return render_template("page403.html"), 403

@app.route("/creer_utilisateur", methods=["POST"])
def creer_utilisateur():
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()

        if (estConnecter() == True):
            if (estAdmin() == True):
                # connecter en admin
                nom = request.form["nom"]
                mdp = request.form["mdp"]
                admin = request.form["admin"]

                if (nom != "" and nom != " " and nom != None and mdp != "" and mdp != " " and mdp != None):
                    curseur.execute("SELECT * FROM utilisateur WHERE nom=%s", (nom,))
                    lstUtilisateur = curseur.fetchall()
                    if (len(lstUtilisateur) == 0):
                        curseur.execute("INSERT INTO utilisateur(nom, mdp, administrateur) VALUES (%s,%s,%s)", (nom, mdp, admin))
                        connexion.commit()
                        return redirect("/lister_utilisateurs")
            else:
                return render_template("page403.html"), 403
        else:
            return render_template("page403.html"), 403
    finally:
        connexion.close()

@app.route("/effacerUtilisateur/<int:id>")
def effacer(id):
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()
        if (estConnecter() == True):
            if (estAdmin() == True):
                # connecter en admin
                curseur.execute("DELETE FROM utilisateur WHERE utilisateur.id = %s", (id,))
                connexion.commit()
                return redirect("/lister_utilisateurs")
            else:
                return render_template("page403.html"), 403
        else:
            return render_template("page403.html"), 403
    finally:
        connexion.close()

@app.route("/admin_menu")
def utilisateur():
    if (estConnecter() == True):
        if (estAdmin() == True):
            # connecter en admin
            return render_template("adminMenu.html")
        else:
            return render_template("page403.html"), 403
    else:
        return render_template("page403.html"), 403

@app.route("/list_magasin")
def list_magasin():
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()

        if (estConnecter() == True):
            curseur.execute("SELECT magasinid, nom FROM magasin")
            lstMagasin = curseur.fetchall()
            return render_template("listMagasin.html", lstMagasin = lstMagasin)
        else:
            return render_template("page403.html"), 403
    finally:
        connexion.close()

@app.route("/creerProduit")
def afficherCreerProduit():
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()
        if (estConnecter() == True):
            curseur.execute("SELECT * FROM magasin")
            lstMagasin = curseur.fetchall()
            curseur.execute("SELECT * FROM typealiment")
            lstCategories = curseur.fetchall()
            return render_template("creerProduit.html", lstMagasin = lstMagasin, lstCategories = lstCategories)
        else:
            return render_template("page403.html"), 403
    finally:
        connexion.close()

@app.route("/creerProduit", methods=["POST"])
def creerProduit():
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()
        if (estConnecter() == True):
            description = str(request.form["description"])
            nom = str(request.form["nom"])
            prix = float(request.form["prix"])
            coutant = float(request.form["coutant"])
            leFormat = str(request.form["format"])
            stock = int(request.form["stock"])
            taxPro = int(request.form["taxPro"])
            taxFed = int(request.form["taxFed"])
            categorie = int(request.form["categorie"])
            active = int(request.form["active"])
            if (not request.form["magasin"]):
                idMagasin = None
            else:
                idMagasin = int(request.form["magasin"])

            curseur.execute("INSERT INTO produit(nom, description, stock, coutant, active, format, prix, typeID, idMagasin, taxableFederal, taxableProvincial) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (nom, description, stock, coutant, active, leFormat, prix, categorie, idMagasin, taxFed, taxPro))
            connexion.commit()

            return redirect("/creerProduit")
        else:
            return render_template("page403.html"), 403
    finally:
        connexion.close()

@app.route("/produitsMagasin/<int:id>")
def produitsMagasin(id):
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()
        if (estConnecter() == True):
            curseur.execute("SELECT * FROM produit where idMagasin = %s OR idMagasin IS NULL", (id,))
            lstProduit = curseur.fetchall()
            return render_template("produitsMagasin.html", lstProduit = lstProduit, id=id)
        else:
            return render_template("page403.html"), 403
    finally:
        connexion.close()

@app.route("/produitsMagasin/tous")
def tousLesProduitsMagasin():
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()
        if (estConnecter() == True):
            curseur.execute("SELECT * FROM produit where idMagasin IS NULL")
            lstProduit = curseur.fetchall()
            return render_template("produitsMagasin.html", lstProduit = lstProduit, id = 2147483647)
        else:
            return render_template("page403.html"), 403
    finally:
        connexion.close()

@app.route("/effacerProduit/<int:idMagasin>/<int:idProduit>")
def effacerProduit(idMagasin, idProduit):
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()
        if (estConnecter() == True):
            curseur.execute("DELETE FROM produit where produitId=%s", (idProduit,))
            connexion.commit()

            if (idMagasin == 2147483647):
                url = "/produitsMagasin/tous"
            else:
                url = "/produitsMagasin/" + str(idMagasin)

            return redirect(url)
        else:
            return render_template("page403.html"), 403
    finally:
        connexion.close()

@app.route("/modifierProduit/<int:idMagasin>/<int:idProduit>")
def AfficherProduit(idMagasin, idProduit):
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()
        if (estConnecter() == True):

            curseur.execute("SELECT * FROM produit where produitId=%s", (idProduit,))
            lstProduit = curseur.fetchone()

            curseur.execute("SELECT * FROM magasin")
            lstMagasin = curseur.fetchall()

            curseur.execute("SELECT * FROM typealiment")
            lstCategories = curseur.fetchall()

            return render_template("modifierProduits.html", idMagasin = idMagasin, idProduit = idProduit, lstProduit = lstProduit, lstMagasin = lstMagasin, lstCategories = lstCategories)
        else:
            return render_template("page403.html"), 403
    finally:
        connexion.close()

@app.route("/modifierProduit/<int:idMagasin>/<int:idProduit>", methods=["POST"])
def modifierProduit(idMagasin, idProduit):
    try:
        connexion = ouvrir_connexion()
        curseur = connexion.cursor()
        if (estConnecter() == True):
            description = str(request.form["description"])
            nom = str(request.form["nom"])
            prix = float(request.form["prix"])
            coutant = float(request.form["coutant"])
            leFormat = str(request.form["format"])
            stock = int(request.form["stock"])
            taxPro = int(request.form["taxPro"])
            taxFed = int(request.form["taxFed"])
            categorie = int(request.form["categorie"])
            active = int(request.form["active"])
            if (not request.form["magasin"]):
                idMagasin = None
            else:
                idMagasin = int(request.form["magasin"])

            curseur.execute("UPDATE `produit` SET `nom`=%s,`description`=%s,`stock`=%s,`coutant`=%s,`active`=%s,`format`=%s,`prix`=%s,`typeID`=%s,`idMagasin`=%s,`taxableFederal`=%s,`taxableProvincial`=%s WHERE produitId=%s;", (str(nom), str(description), int(stock), int(coutant), int(active), str(leFormat), int(prix), str(categorie), idMagasin, int(taxFed), int(taxPro), int(idProduit)))
            connexion.commit()

            if (idMagasin == 2147483647 or idMagasin is None or idMagasin == "None"):
                url = "/produitsMagasin/tous"
            else:
                url = "/produitsMagasin/" + str(idMagasin)

            return redirect(url)
        else:
            return render_template("page403.html"), 403
    finally:
        connexion.close()


@app.errorhandler(404)
def page404(error):
  return render_template("page404.html"), 404

@app.errorhandler(500)
def page500(error):
  return render_template("page500.html"), 500

@app.errorhandler(403)
def page403(error):
  return render_template("page403.html"), 403

if __name__ == "__main__":
    app.run()