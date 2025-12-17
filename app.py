# =======================================================
# APP.PY - APPLICATION FLASK BAEL
# =======================================================

from flask import Flask, render_template, request, redirect, url_for
import sys
import os

# Ajouter le dossier calculs au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'calculs'))

# Importer la classe CalculBAEL
from calculs.calculs_bael import CalculBAEL

app = Flask(__name__)

# ==================================
# FONCTIONS DE VÉRIFICATION CORRIGÉES
# ==================================

def verifier_valeurs_positives(data):
    """Vérifie que toutes les valeurs sont positives"""
    erreurs = []
    
    if float(data["b"]) <= 0:
        erreurs.append("❌ La largeur b doit être positive.")
    
    if float(data["fc28"]) <= 0:
        erreurs.append("❌ fc28 doit être positive.")
    
    if float(data["Mu"]) <= 0:
        erreurs.append("❌ Mu doit être positive.")
    
    if float(data["Ms"]) <= 0:
        erreurs.append("❌ Ms doit être positive.")
    
    if float(data["h"]) <= 0:
        erreurs.append("❌ La hauteur h doit être positive.")
    
    if float(data["d"]) <= 0:
        erreurs.append("❌ La hauteur utile d doit être positive.")
    
    if float(data["dp"]) <= 0:
        erreurs.append("❌ L'enrobage d' doit être positif.")
    
    return erreurs

def verifier_geometrie_apres_conversion(donnees_norm):
    """Vérifie les relations géométriques APRÈS conversion en mètres"""
    erreurs = []
    
    # Vérifier h > d (en mètres)
    if donnees_norm['h_m'] <= donnees_norm['d_m']:
        erreurs.append("❌ La hauteur totale h doit être supérieure à la hauteur utile d.")
    
    # Vérifier h > d' (en mètres)
    if donnees_norm['h_m'] <= donnees_norm['dp_m']:
        erreurs.append("❌ La hauteur h doit être supérieure à d'.")
    
    # Vérifier d > d' (EN MÈTRES - CORRECTION IMPORTANTE)
    if donnees_norm['d_m'] <= donnees_norm['dp_m']:
        # Convertir en cm pour le message d'erreur
        d_cm = donnees_norm['d_m'] * 100
        dp_cm = donnees_norm['dp_m'] * 100
        erreurs.append(f"❌ La hauteur utile d ({d_cm:.1f} cm) doit être supérieure à d' ({dp_cm:.1f} cm).")
    
    # Vérifier Mu > Ms
    if donnees_norm['Mu_MNm'] <= donnees_norm['Ms_MNm']:
        erreurs.append("❌ Mu doit être strictement supérieur à Ms (ELU > ELS).")
    
    return erreurs

# ==================================
# ROUTES DU SITE
# ==================================

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        section = request.form["section"]
        if section == "te":
            return redirect(url_for("maintenance"))
        return redirect(url_for("donnees"))
    return render_template("home.html")

@app.route("/maintenance")
def maintenance():
    return render_template("maintenance.html")

@app.route("/donnees", methods=["GET", "POST"])
def donnees():
    if request.method == "POST":
        try:
            # 1. RÉCUPÉRATION DES DONNÉES
            data = {
                "Mu": request.form["Mu"],
                "Mu_unite": request.form["Mu_unite"],
                "Ms": request.form["Ms"],
                "Ms_unite": request.form["Ms_unite"],
                "b": request.form["b"],
                "b_unite": request.form["b_unite"],
                "h": request.form["h"],
                "h_unite": request.form["h_unite"],
                "d": request.form["d"],
                "d_unite": request.form["d_unite"],
                "dp": request.form["dp"],
                "dp_unite": request.form["dp_unite"],
                "fc28": request.form["fc28"],
                "acier": request.form["acier"],
                "fissuration": request.form["fissuration"],
                "acier_ha": request.form["acier_ha"]  # NOUVEAU: HA ou RL
            }
            
        except Exception as e:
            return render_template("donnees.html", 
                                 erreurs=["❌ ERREUR: Tous les champs doivent être remplis correctement."])
        
        # 2. VÉRIFICATION VALEURS POSITIVES
        erreurs_positives = verifier_valeurs_positives(data)
        if erreurs_positives:
            return render_template("donnees.html", 
                                 erreurs=erreurs_positives, 
                                 anciennes_valeurs=request.form)
        
        try:
            # 3. NORMALISATION DES UNITÉS
            donnees_norm = CalculBAEL.normaliser_donnees(data)
            
            # 4. VÉRIFICATION GÉOMÉTRIE (APRÈS CONVERSION)
            erreurs_geometrie = verifier_geometrie_apres_conversion(donnees_norm)
            if erreurs_geometrie:
                return render_template("donnees.html", 
                                     erreurs=erreurs_geometrie, 
                                     anciennes_valeurs=request.form)
            
            # 5. CALCUL ELU
            resultats_elu = CalculBAEL.calcul_elu(
                Mu_MNm=donnees_norm['Mu_MNm'],
                b_m=donnees_norm['b_m'],
                d_m=donnees_norm['d_m'],
                dp_m=donnees_norm['dp_m'],
                fc28_MPa=donnees_norm['fc28_MPa'],
                acier_type=donnees_norm['acier_type']
            )
            
            # 6. VÉRIFICATION ELS
            resultats_els = CalculBAEL.verification_els(
                Ms_MNm=donnees_norm['Ms_MNm'],
                b_m=donnees_norm['b_m'],
                d_m=donnees_norm['d_m'],
                dp_m=donnees_norm['dp_m'],
                fc28_MPa=donnees_norm['fc28_MPa'],
                acier_type=donnees_norm['acier_type'],
                fissuration=donnees_norm['fissuration'],
                acier_ha=donnees_norm['acier_ha'],
                Ast_m2=resultats_elu['Ast_m2'],
                Asc_m2=resultats_elu['Asc_m2']
            )
            
            # 7. PRÉPARATION POUR AFFICHAGE
            donnees_affichage = {
                'Mu': data['Mu'],
                'Mu_unite': data['Mu_unite'],
                'Ms': data['Ms'],
                'Ms_unite': data['Ms_unite'],
                'b': data['b'],
                'b_unite': data['b_unite'],
                'h': data['h'],
                'h_unite': data['h_unite'],
                'd': data['d'],
                'd_unite': data['d_unite'],
                'dp': data['dp'],
                'dp_unite': data['dp_unite'],
                'fc28': data['fc28'],
                'acier': data['acier'],
                'fissuration': data['fissuration'],
                'acier_ha': data['acier_ha']
            }
            
            # 8. AFFICHAGE DES RÉSULTATS
            return render_template("resultats.html",
                                 donnees=donnees_affichage,
                                 elu=resultats_elu,
                                 els=resultats_els)
            
        except ValueError as e:
            return render_template("donnees.html", 
                                 erreurs=[f"❌ ERREUR de calcul: {str(e)}"],
                                 anciennes_valeurs=request.form)
        except Exception as e:
            return render_template("donnees.html", 
                                 erreurs=[f"❌ ERREUR technique: {str(e)}"],
                                 anciennes_valeurs=request.form)
    
    # GET request
    return render_template("donnees.html")

# ==================================
# LANCEMENT APPLICATION
# ==================================
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)