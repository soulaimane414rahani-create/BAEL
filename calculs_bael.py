# =======================================================
# CALCULS BAEL DÉTAILLÉS - RAHANI Soulaimane
# =======================================================

import math

class CalculBAEL:
    """
    Classe principale pour tous les calculs BAEL
    """
    
    # ============================================
    # 1. CONVERSION DES UNITÉS
    # ============================================
    
    @staticmethod
    def convertir_moment(valeur, unite):
        """Convertit le moment en MN.m"""
        if unite == "MN.m":
            return float(valeur)
        elif unite == "kN.m":
            return float(valeur) / 1000.0
        else:
            raise ValueError(f"Unité non reconnue: {unite}")
    
    @staticmethod
    def convertir_longueur(valeur, unite):
        """Convertit la longueur en mètres"""
        if unite == "m":
            return float(valeur)
        elif unite == "cm":
            return float(valeur) / 100.0
        elif unite == "mm":
            return float(valeur) / 1000.0
        else:
            raise ValueError(f"Unité non reconnue: {unite}")
    
    @staticmethod
    def normaliser_donnees(donnees_brutes):
        """Normalise TOUTES les données en unités BAEL"""
        norm = {}
        
        # Conversion des moments
        norm['Mu_MNm'] = CalculBAEL.convertir_moment(donnees_brutes['Mu'], donnees_brutes['Mu_unite'])
        norm['Ms_MNm'] = CalculBAEL.convertir_moment(donnees_brutes['Ms'], donnees_brutes['Ms_unite'])
        
        # Conversion des longueurs
        norm['b_m'] = CalculBAEL.convertir_longueur(donnees_brutes['b'], donnees_brutes['b_unite'])
        norm['h_m'] = CalculBAEL.convertir_longueur(donnees_brutes['h'], donnees_brutes['h_unite'])
        norm['d_m'] = CalculBAEL.convertir_longueur(donnees_brutes['d'], donnees_brutes['d_unite'])
        norm['dp_m'] = CalculBAEL.convertir_longueur(donnees_brutes['dp'], donnees_brutes['dp_unite'])
        
        # Matériaux
        norm['fc28_MPa'] = float(donnees_brutes['fc28'])
        norm['acier_type'] = int(donnees_brutes['acier'])
        norm['fissuration'] = donnees_brutes['fissuration']
        norm['acier_ha'] = donnees_brutes['acier_ha']  # 'HA' ou 'RL'
        
        return norm
    
    # ============================================
    # 2. CALCUL ELU
    # ============================================
    
    @staticmethod
    def calcul_elu(Mu_MNm, b_m, d_m, dp_m, fc28_MPa, acier_type):
        """
        Calcul ELU selon organigramme BAEL
        
        Retourne:
        - Pour armatures simples: α, z, Ast
        - Pour armatures doubles: MR, Mr, zR, εsc (‰), Ast, Asc
        """
        # 1. Paramètres acier
        if acier_type == 400:
            muR = 0.391
            alphaR = 0.669
            eps_els_pour_mille = 1.74  # en ‰
            fe_MPa = 400
        elif acier_type == 500:
            muR = 0.371
            alphaR = 0.617
            eps_els_pour_mille = 2.17  # en ‰
            fe_MPa = 500
        
        # 2. Contraintes de calcul
        sigma_bc_MPa = (0.85 * fc28_MPa) / 1.5
        sigma_st_MPa = fe_MPa / 1.15
        
        # 3. Moment réduit μ
        mu = Mu_MNm / (b_m * d_m * d_m * sigma_bc_MPa)
        
        # 4. Détermination pivot
        mu_AB = 0.186
        if mu < mu_AB:
            pivot = "A"
        else:
            pivot = "B"
        
        # 5. PIVOT A
        if pivot == "A":
            # Vérification μ < μ₁ (simplifié)
            mu_1 = 0.185 if acier_type == 400 else 0.180
            if mu < mu_1:
                raise ValueError("Section sous-dimensionnée. Augmentez b ou d.")
            
            # Armatures simples pivot A
            alpha = 1.25 * (1 - math.sqrt(1 - 2 * mu))
            z_m = d_m * (1 - 0.4 * alpha)
            Ast_m2 = Mu_MNm / (z_m * sigma_st_MPa)
            
            return {
                'type': 'simples',
                'pivot': 'A',
                'mu': round(mu, 4),
                'alpha': round(alpha, 4),
                'z_m': z_m,
                'z_cm': round(z_m * 100, 2),
                'Ast_m2': Ast_m2,
                'Ast_cm2': round(Ast_m2 * 10000, 2),
                'Asc_m2': 0.0,
                'Asc_cm2': 0.0,
                'sigma_bc_MPa': round(sigma_bc_MPa, 2),
                'sigma_st_MPa': round(sigma_st_MPa, 2),
                'display_order': [
                    {'label': 'Moment réduit μ', 'value': round(mu, 4), 'unit': ''},
                    {'label': 'Pivot', 'value': 'A', 'unit': ''},
                    {'label': 'α', 'value': round(alpha, 4), 'unit': ''},
                    {'label': 'z', 'value': round(z_m * 100, 2), 'unit': 'cm'},
                    {'label': 'A<sub>st</sub>', 'value': round(Ast_m2 * 10000, 2), 'unit': 'cm²'}
                ]
            }
        
        # 6. PIVOT B
        else:
            if mu <= muR:
                # Armatures simples pivot B
                alpha = 1.25 * (1 - math.sqrt(1 - 2 * mu))
                z_m = d_m * (1 - 0.4 * alpha)
                Ast_m2 = Mu_MNm / (z_m * sigma_st_MPa)
                
                return {
                    'type': 'simples',
                    'pivot': 'B',
                    'mu': round(mu, 4),
                    'alpha': round(alpha, 4),
                    'z_m': z_m,
                    'z_cm': round(z_m * 100, 2),
                    'Ast_m2': Ast_m2,
                    'Ast_cm2': round(Ast_m2 * 10000, 2),
                    'Asc_m2': 0.0,
                    'Asc_cm2': 0.0,
                    'sigma_bc_MPa': round(sigma_bc_MPa, 2),
                    'sigma_st_MPa': round(sigma_st_MPa, 2),
                    'display_order': [
                        {'label': 'Moment réduit μ', 'value': round(mu, 4), 'unit': ''},
                        {'label': 'Pivot', 'value': 'B', 'unit': ''},
                        {'label': 'α', 'value': round(alpha, 4), 'unit': ''},
                        {'label': 'z', 'value': round(z_m * 100, 2), 'unit': 'cm'},
                        {'label': 'A<sub>st</sub>', 'value': round(Ast_m2 * 10000, 2), 'unit': 'cm²'}
                    ]
                }
            
            else:
                # ARMATURES DOUBLES
                # Fixer μ = μR, α = αR
                alpha = alphaR
                z_R = d_m * (1 - 0.4 * alphaR)
                
                # Moment résistant MR
                MR_MNm = muR * b_m * d_m * d_m * sigma_bc_MPa
                
                # Moment résiduel Mr
                Mr_MNm = Mu_MNm - MR_MNm
                
                # Calcul εsc en ‰ (CORRECTION IMPORTANTE)
                # Formula: εsc = ((d - d')/d) × (εels + 3.5‰) - εels
                eps_sc_pour_mille = ((d_m - dp_m) / d_m) * (eps_els_pour_mille + 3.5) - eps_els_pour_mille
                
                # Calcul σsc
                if eps_sc_pour_mille < eps_els_pour_mille:
                    # Convertir en décimal pour calcul
                    eps_sc_decimal = eps_sc_pour_mille / 1000.0
                    E_MPa = 200000
                    sigma_sc_MPa = E_MPa * eps_sc_decimal
                else:
                    sigma_sc_MPa = fe_MPa / 1.15
                
                # Calcul Asc
                Asc_m2 = Mr_MNm / ((d_m - dp_m) * sigma_sc_MPa)
                
                # Calcul Ast
                Ast_MR = MR_MNm / (z_R * sigma_st_MPa)
                Ast_Mr = Mr_MNm / ((d_m - dp_m) * sigma_st_MPa)
                Ast_m2 = Ast_MR + Ast_Mr
                
                return {
                    'type': 'doubles',
                    'pivot': 'B',
                    'mu': round(mu, 4),
                    'alpha': round(alpha, 4),
                    'z_m': z_R,
                    'z_cm': round(z_R * 100, 2),
                    'Ast_m2': Ast_m2,
                    'Ast_cm2': round(Ast_m2 * 10000, 2),
                    'Asc_m2': Asc_m2,
                    'Asc_cm2': round(Asc_m2 * 10000, 2),
                    'MR_MNm': round(MR_MNm, 6),
                    'Mr_MNm': round(Mr_MNm, 6),
                    'eps_sc_pour_mille': round(eps_sc_pour_mille, 2),
                    'sigma_sc_MPa': round(sigma_sc_MPa, 2),
                    'sigma_bc_MPa': round(sigma_bc_MPa, 2),
                    'sigma_st_MPa': round(sigma_st_MPa, 2),
                    'display_order': [
                        {'label': 'Moment réduit μ', 'value': round(mu, 4), 'unit': ''},
                        {'label': 'Pivot', 'value': 'B', 'unit': ''},
                        {'label': 'M<sub>R</sub>', 'value': round(MR_MNm, 6), 'unit': 'MN.m'},
                        {'label': 'M<sub>r</sub>', 'value': round(Mr_MNm, 6), 'unit': 'MN.m'},
                        {'label': 'z<sub>R</sub>', 'value': round(z_R * 100, 2), 'unit': 'cm'},
                        {'label': 'ε<sub>sc</sub>', 'value': round(eps_sc_pour_mille, 2), 'unit': '‰'},
                        {'label': 'A<sub>st</sub>', 'value': round(Ast_m2 * 10000, 2), 'unit': 'cm²'},
                        {'label': 'A<sub>sc</sub>', 'value': round(Asc_m2 * 10000, 2), 'unit': 'cm²'}
                    ]
                }
    
    # ============================================
    # 3. VÉRIFICATION ELS
    # ============================================
    
    @staticmethod
    def calcul_contraintes_admissibles(fc28_MPa, acier_type, fissuration, acier_ha):
        """
        Calcul des contraintes admissibles
        
        acier_ha: 'HA' (η=1.6) ou 'RL' (η=1.0)
        """
        # Contrainte béton admissible
        sigma_b_adm_MPa = 0.6 * fc28_MPa
        
        # Calcul ft28
        ft28_MPa = 0.6 + 0.06 * fc28_MPa
        
        # Coefficient η
        eta = 1.6 if acier_ha == "HA" else 1.0
        
        # Limite d'élasticité de l'acier
        fe_MPa = 400 if acier_type == 400 else 500
        
        # Contrainte acier admissible selon fissuration
        if fissuration == "FPP":
            sigma_s_adm_MPa = fe_MPa 
        
        elif fissuration == "FP":
            limite1 = (2/3) * fe_MPa
            limite2 = 110 * math.sqrt(eta * ft28_MPa)
            sigma_s_adm_MPa = min(limite1, limite2)
        
        elif fissuration == "FTP":
            limite1 = 0.5 * fe_MPa
            limite2 = 90 * math.sqrt(eta * ft28_MPa)
            sigma_s_adm_MPa = min(limite1, limite2)
        
        return sigma_b_adm_MPa, sigma_s_adm_MPa
    
    @staticmethod
    def verification_els(Ms_MNm, b_m, d_m, dp_m, fc28_MPa, acier_type, fissuration, acier_ha, Ast_m2, Asc_m2):
        """
        Vérification ELS selon organigramme
        
        Affiche: Y1, Igg', K, σb, σs, et comparaison avec admissibles
        """
        # 1. Contraintes admissibles
        sigma_b_adm_MPa, sigma_s_adm_MPa = CalculBAEL.calcul_contraintes_admissibles(
            fc28_MPa, acier_type, fissuration, acier_ha
        )
        
        # 2. Calcul axe neutre Y1
        # Équation: bY1² + 30(Ast + Asc)Y1 - 30(Asc×d' + Ast×d) = 0
        A = b_m
        B = 30 * (Ast_m2 + Asc_m2)
        C = -30 * (Asc_m2 * dp_m + Ast_m2 * d_m)
        
        delta = B**2 - 4 * A * C
        
        if delta < 0:
            raise ValueError("Pas de solution réelle pour l'axe neutre")
        
        Y1_m = (-B + math.sqrt(delta)) / (2 * A)
        
        # 3. Calcul inertie Igg'
        I_m4 = (b_m * Y1_m**3) / 3
        I_m4 += 15 * Asc_m2 * (dp_m - Y1_m)**2
        I_m4 += 15 * Ast_m2 * (d_m - Y1_m)**2
        
        # 4. Calcul pente K
        K_MN_m3 = Ms_MNm / I_m4
        
        # 5. Calcul contraintes
        sigma_b_MPa = K_MN_m3 * Y1_m
        sigma_s_MPa = 15 * K_MN_m3 * (d_m - Y1_m)
        
        # 6. Vérification
        verif_beton = sigma_b_MPa <= sigma_b_adm_MPa
        verif_acier = sigma_s_MPa <= sigma_s_adm_MPa
        
        # 7. Détermination du cas
        if verif_beton and verif_acier:
            cas = 1
            message = "Cas 1: ELU déterminant"
        elif verif_beton and not verif_acier:
            cas = 2
            message = "Cas 2: ELS Armatures simples"
        elif not verif_beton and not verif_acier:
            cas = 3
            message = "Cas 3: ELS Armatures doubles"
        else:
            cas = 4
            message = "Cas 4: ELS Armatures doubles"
        
        return {
            'Y1_m': Y1_m,
            'Y1_cm': round(Y1_m * 100, 2),
            'I_m4': I_m4,
            'I_cm4': round(I_m4 * 100000000, 0),
            'K_MN_m3': round(K_MN_m3, 4),
            'sigma_b_MPa': round(sigma_b_MPa, 2),
            'sigma_s_MPa': round(sigma_s_MPa, 2),
            'sigma_b_adm_MPa': round(sigma_b_adm_MPa, 2),
            'sigma_s_adm_MPa': round(sigma_s_adm_MPa, 2),
            'cas': cas,
            'message_cas': message,
            'verif_beton': 'OK' if verif_beton else 'NON',
            'verif_acier': 'OK' if verif_acier else 'NON',
            'display_order': [
                {'label': 'Axe neutre Y<sub>1</sub>', 'value': round(Y1_m * 100, 2), 'unit': 'cm'},
                {'label': 'Inertie I<sub>gg\'</sub>', 'value': round(I_m4 * 100000000, 0), 'unit': 'cm⁴'},
                {'label': 'Pente K', 'value': round(K_MN_m3, 4), 'unit': 'MN/m³'},
                {'label': 'σ<sub>b</sub>', 'value': round(sigma_b_MPa, 2), 'unit': 'MPa'},
                {'label': 'σ<sub>s</sub>', 'value': round(sigma_s_MPa, 2), 'unit': 'MPa'},
                {'label': 'σ<sub>b</sub> admissible', 'value': round(sigma_b_adm_MPa, 2), 'unit': 'MPa'},
                {'label': 'σ<sub>s</sub> admissible', 'value': round(sigma_s_adm_MPa, 2), 'unit': 'MPa'},
                {'label': 'Vérification béton', 'value': 'OK' if verif_beton else 'NON', 'unit': ''},
                {'label': 'Vérification acier', 'value': 'OK' if verif_acier else 'NON', 'unit': ''}
            ]
        }
