# =======================================================
# app.py - APPLICATION BAEL PROFESSIONNELLE
# =======================================================
import streamlit as st
import sys
import os
import math


# Import du module de calcul - version simplifiée
try:
    from calculs_bael import CalculBAEL
    CALCULS_DISPONIBLES = True
except ImportError:
    CALCULS_DISPONIBLES = False
    st.error("⚠️ Erreur : module de calcul BAEL introuvable")


# =======================================================
# FOOTER
# =======================================================
def afficher_footer():
    st.markdown(
        """
        <div style="text-align: center; color: #718096; font-size: 0.9rem;
                    padding: 2rem 0; border-top: 1px solid #e2e8f0; margin-top: 3rem;">
            🏗️ RAHANI Soulaimane - Futur ingénieur d'État Bâtiment et Travaux Publics © 2025
        </div>
        """,
        unsafe_allow_html=True,
    )


# =======================================================
# CONFIG
# =======================================================
st.set_page_config(
    page_title="Calcul BAEL - RAHANI Soulaimane © 2025",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# CSS
st.markdown(
    """
<style>
.main-title {
    text-align: center;
    color: #1a365d;
    font-size: 2.8rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    font-family: 'Segoe UI', sans-serif;
}
.page-subtitle {
    text-align: center;
    color: #4a5568;
    font-size: 1.2rem;
    margin-bottom: 2rem;
}
.section-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 2.5rem;
    margin: 1.5rem 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
}
.section-card:hover {
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    transform: translateY(-2px);
}
.results-metric {
    background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
    border-radius: 10px;
    padding: 1.5rem;
    border-left: 4px solid #3182ce;
    margin: 1rem 0;
}
.status-ok { color: #38a169; font-weight: 600; }
.status-ko { color: #e53e3e; font-weight: 600; }

.stExpander > div > label > div {
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    color: #1a365d !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# =======================================================
# SESSION
# =======================================================
if "page" not in st.session_state:
    st.session_state.page = "accueil"

if "donnees_saisie" not in st.session_state:
    st.session_state.donnees_saisie = {}

if "resultats_elu" not in st.session_state:
    st.session_state.resultats_elu = None

if "resultats_els" not in st.session_state:
    st.session_state.resultats_els = None


# =======================================================
# FONCTIONS UTILES
# =======================================================
def verifier_valeurs_positives(data):
    erreurs = []
    if float(data.get("b", 0)) <= 0:
        erreurs.append("❌ Largeur b doit être positive")
    if float(data.get("fc28", 0)) <= 0:
        erreurs.append("❌ fc28 doit être positive")
    if float(data.get("Mu", 0)) <= 0:
        erreurs.append("❌ Mu doit être positive")
    if float(data.get("Ms", 0)) <= 0:
        erreurs.append("❌ Ms doit être positive")
    if float(data.get("h", 0)) <= 0:
        erreurs.append("❌ Hauteur h doit être positive")
    if float(data.get("d", 0)) <= 0:
        erreurs.append("❌ Hauteur utile d doit être positive")
    if float(data.get("dp", 0)) <= 0:
        erreurs.append("❌ Enrobage d' doit être positif")
    return erreurs


def valider_dimensions(h, h_unite, d, d_unite, dp, dp_unite, b, b_unite):
    b_m = b / 100 if b_unite == "cm" else b
    h_m = h / 100 if h_unite == "cm" else h
    d_m = d / 100 if d_unite == "cm" else d
    dp_m = dp / 100 if dp_unite == "cm" else dp

    if d_m >= h_m:
        st.error(f"❌ ERREUR : d ({d_m:.2f} m) ≥ h ({h_m:.2f} m) – corriger h et d.")
        return False, None, None, None, None

    if dp_m >= d_m:
        st.error(f"❌ ERREUR : d' ({dp_m:.2f} m) ≥ d ({d_m:.2f} m) – corriger d et d'.")
        return False, None, None, None, None

    if dp_m >= h_m:
        st.error(f"❌ ERREUR : d' ({dp_m:.2f} m) ≥ h ({h_m:.2f} m) – corriger d' et h.")
        return False, None, None, None, None

    return True, h_m, d_m, dp_m, b_m


# =======================================================
# PAGE ACCUEIL
# =======================================================
def page_accueil():
    st.markdown(
        '<h1 class="main-title">Dimensionnement des poutres en BA</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='page-subtitle'>🏗️ Application de calcul BAEL 91</p>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align: center; margin-bottom: 2rem; font-size: 4rem;">📐</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h3 style="text-align: center; color: #1a365d; margin-bottom: 1.5rem;">Section rectangulaire</h3>',
            unsafe_allow_html=True,
        )
        if st.button("🚀 Démarrer le calcul", type="primary", use_container_width=True):
            st.session_state.page = "saisie_rectangulaire"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align: center; margin-bottom: 2rem; font-size: 4rem;">T</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h3 style="text-align: center; color: #1a365d; margin-bottom: 1.5rem;">Section en T</h3>',
            unsafe_allow_html=True,
        )
        st.info("🧱 Module en développement (section en T)")
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("À propos de l'application"):
        st.markdown(
            """
- Dimensionnement des poutres en BA selon la norme de BAEL 91 
- La version prochaine appartient Dimensionnement du poutre section en Té 
  InchaALLAH
"""
        )

    afficher_footer()


# =======================================================
# PAGE SAISIE
# =======================================================
def page_saisie_rectangulaire():
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.markdown(
            '<h2 class="main-title">Saisie des données</h2>', unsafe_allow_html=True
        )
        st.markdown(
            "<p class='page-subtitle'>Section rectangulaire – BAEL 91</p>",
            unsafe_allow_html=True,
        )
    with col_back:
        if st.button("⬅️ Accueil"):
            st.session_state.page = "accueil"
            st.rerun()

    if not CALCULS_DISPONIBLES:
        st.error("❌ Module de calcul BAEL non disponible")
        afficher_footer()
        return

    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    # valeurs par défaut
    b_default, h_default, d_default, dp_default = 0.25, 0.50, 0.45, 0.04
    Mu_default, Ms_default, fc28_default = 0.320, 0.177, 25.0

    calculer = False
    retour = False

    with st.form("form_saisie", clear_on_submit=False):
        st.markdown("### 📐 Géométrie de la section")
        col1, col2 = st.columns([4, 1])
        with col1:
            b = st.number_input(
                "Largeur b",
                min_value=0.01,
                value=b_default,
                format="%.3f",
                key="b_input",
            )
        with col2:
            b_unite = st.selectbox(" ", ["m", "cm"], index=0, key="b_unit")

        col1, col2 = st.columns([4, 1])
        with col1:
            h = st.number_input(
                "Hauteur totale h",
                min_value=0.01,
                value=h_default,
                format="%.3f",
                key="h_input",
            )
        with col2:
            h_unite = st.selectbox(" ", ["m", "cm"], index=0, key="h_unit")

        col1, col2 = st.columns([4, 1])
        with col1:
            d = st.number_input(
                "Hauteur utile d",
                min_value=0.01,
                value=d_default,
                format="%.3f",
                key="d_input",
            )
        with col2:
            d_unite = st.selectbox(" ", ["m", "cm"], index=0, key="d_unit")

        col1, col2 = st.columns([4, 1])
        with col1:
            dp = st.number_input(
                "Enrobage d'",
                min_value=0.01,
                value=dp_default,
                format="%.3f",
                key="dp_input",
            )
        with col2:
            dp_unite = st.selectbox(" ", ["m", "cm"], index=0, key="dp_unit")

        st.markdown("---")

        st.markdown("### 🧮 Sollicitations")
        # CHOIX MN.m (défaut) ou kN.m
        col1, col2 = st.columns([4, 1])
        with col1:
            Mu = st.number_input(
                "Moment ultime Mu (ELU)",
                min_value=0.001,
                value=Mu_default,
                format="%.3f",
                key="Mu_input",
            )
        with col2:
            Mu_unite = st.selectbox(" ", ["MN.m", "kN.m"], index=0, key="Mu_unit")  # MN.m par défaut

        col1, col2 = st.columns([4, 1])
        with col1:
            Ms = st.number_input(
                "Moment de service Ms (ELS)",
                min_value=0.001,
                value=Ms_default,
                format="%.3f",
                key="Ms_input",
            )
        with col2:
            Ms_unite = st.selectbox(" ", ["MN.m", "kN.m"], index=0, key="Ms_unit")  # MN.m par défaut

        st.markdown("---")

        st.markdown("### 🧱 Matériaux")
        col1, col2 = st.columns([4, 1])
        with col1:
            fc28 = st.number_input(
                "Résistance béton fc28",
                min_value=1.0,
                value=fc28_default,
                format="%.0f",
                key="fc28_input",
            )
        with col2:
            st.markdown("MPa")

        acier = st.selectbox(
            "Nuance d'acier", ["FeE 400", "FeE 500"], index=1, key="acier"
        )
        fissuration = st.selectbox(
            "Classe de fissuration", ["FPP", "FP", "FTP"], index=1, key="fissuration"
        )
        acier_ha = st.radio("Nature de l'acier", ["HA", "RL"], index=0, key="acier_ha")

        st.markdown("---")

        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            retour = st.form_submit_button("⬅️ Retour", use_container_width=True)
        with col_btn2:
            calculer = st.form_submit_button(
                "🏗️ Calculer BAEL", type="primary", use_container_width=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

    if calculer:
        valide, h_m, d_m, dp_m, b_m = valider_dimensions(
            h, h_unite, d, d_unite, dp, dp_unite, b, b_unite
        )

        if not valide:
            afficher_footer()
            return

        # Conversion kN.m -> MN.m si nécessaire
        Mu_MNm = Mu / 1000 if Mu_unite == "kN.m" else Mu
        Ms_MNm = Ms / 1000 if Ms_unite == "kN.m" else Ms

        data = {
            "Mu": Mu_MNm,
            "Mu_unite": "MN.m",
            "Ms": Ms_MNm,
            "Ms_unite": "MN.m",
            "b": round(b_m, 3),
            "b_unite": "m",
            "h": round(h_m, 3),
            "h_unite": "m",
            "d": round(d_m, 3),
            "d_unite": "m",
            "dp": round(dp_m, 3),
            "dp_unite": "m",
            "fc28": float(fc28),
            "acier": 500 if "500" in acier else 400,
            "fissuration": fissuration,
            "acier_ha": acier_ha,
        }

        erreurs = verifier_valeurs_positives(data)
        if erreurs:
            for err in erreurs:
                st.error(err)
        else:
            try:
                donnees_norm = CalculBAEL.normaliser_donnees(data)
                resultats_elu = CalculBAEL.calcul_elu(
                    Mu_MNm=donnees_norm["Mu_MNm"],
                    b_m=donnees_norm["b_m"],
                    d_m=donnees_norm["d_m"],
                    dp_m=donnees_norm["dp_m"],
                    fc28_MPa=donnees_norm["fc28_MPa"],
                    acier_type=donnees_norm["acier_type"],
                )
                resultats_els = CalculBAEL.verification_els(
                    Ms_MNm=donnees_norm["Ms_MNm"],
                    b_m=donnees_norm["b_m"],
                    d_m=donnees_norm["d_m"],
                    dp_m=donnees_norm["dp_m"],
                    fc28_MPa=donnees_norm["fc28_MPa"],
                    acier_type=donnees_norm["acier_type"],
                    fissuration=donnees_norm["fissuration"],
                    acier_ha=donnees_norm["acier_ha"],
                    Ast_m2=resultats_elu["Ast_m2"],
                    Asc_m2=resultats_elu.get("Asc_m2", 0.0),
                )

                st.session_state.donnees_saisie = data
                st.session_state.donnees_norm = donnees_norm
                st.session_state.resultats_elu = resultats_elu
                st.session_state.resultats_els = resultats_els
                st.session_state.page = "resultats"
                st.rerun()
            except Exception:
                # Message exact demandé
                st.error(
                    "❌ Erreur de calcul : Section sous-dimensionnée. "
                    "Il faut redimensionner la section (augmenter b ou d)."
                )

    if retour:
        st.session_state.page = "accueil"
        st.rerun()

    afficher_footer()


# =======================================================
# PAGE RÉSULTATS (identique - sans majoration)
# =======================================================
def page_resultats():
    if not st.session_state.resultats_elu:
        st.warning("❌ Aucun résultat disponible")
        if st.button("🔄 Nouveau calcul"):
            st.session_state.page = "saisie_rectangulaire"
            st.rerun()
        afficher_footer()
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.markdown(
            '<h2 class="main-title">Résultats BAEL</h2>', unsafe_allow_html=True
        )
        st.markdown(
            "<p class='page-subtitle'>Section rectangulaire – ELU & ELS</p>",
            unsafe_allow_html=True,
        )
    with col_back:
        if st.button("⬅️ Accueil"):
            st.session_state.page = "accueil"
            st.rerun()

    elu = st.session_state.resultats_elu
    els = st.session_state.resultats_els
    data = st.session_state.donnees_saisie

    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown('<hr style="margin: 2rem 0;">', unsafe_allow_html=True)

    # Données de saisie
    with st.expander("📋 Données de saisie", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("h", f"{data['h']*100:.1f} cm")
            st.metric("d", f"{data['d']*100:.1f} cm")
        with col2:
            st.metric("d'", f"{data['dp']*100:.1f} cm")
            st.metric("b", f"{data['b']*100:.1f} cm")
        with col3:
            st.metric("Mu", f"{data['Mu']:.3f} MN.m")
            st.metric("Ms", f"{data['Ms']:.3f} MN.m")
            st.metric("fc28", f"{data['fc28']:.0f} MPa")

    # === ELU ===
    with st.expander("🔥 ELU – État limite ultime", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="results-metric">', unsafe_allow_html=True)
            st.markdown(
                '<h4 style="margin: 0 0 0.5rem 0; color: #1a365d;">µ réduit</h4>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<h2 style="margin: 0; font-size: 2rem;">{elu.get("mu", 0):.3f}</h2>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="results-metric">', unsafe_allow_html=True)
            st.markdown(
                '<h4 style="margin: 0 0 0.5rem 0; color: #1a365d;">Pivot</h4>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<h2 style="margin: 0; font-size: 2rem;">{elu.get("pivot", "-")}</h2>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            Asc_cm2 = round(elu.get("Asc_cm2", 0.0), 2)
            type_armature = "Armatures doubles 🔩" if Asc_cm2 > 0 else "Armatures simples 🔩"
            st.markdown(
                '<div class="results-metric">'
                '<h4 style="margin: 0 0 0.5rem 0; color: #1a365d;">Type d\'armature</h4>'
                f'<h2 style="margin: 0; font-size: 1.5rem;">{type_armature}</h2>'
                "</div>",
                unsafe_allow_html=True,
            )

        st.markdown('<hr style="margin: 1.5rem 0;">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Aₛₜ :** {elu.get('Ast_cm2', 0.0):.2f} cm²")
            if Asc_cm2 > 0:
                st.markdown(f"**Aₛ꜀ :** {Asc_cm2:.2f} cm²")
        with col2:
            st.markdown(f"**α :** {elu.get('alpha', 0.0):.3f}")
            st.markdown(f"**z :** {elu.get('z_cm', 0.0):.2f} cm")
            eps_sc = elu.get("eps_sc_pour_mille", 0.0)
            st.markdown(f"**ε<sub>sc</sub> :** {eps_sc:.3f} ‰", unsafe_allow_html=True)

        if elu.get("type") == "doubles":
            st.markdown("---")
            st.markdown(
                f"**M<sub>R</sub> :** {elu.get('MR_MNm', 0.0):.3f} MN.m",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"**M<sub>r</sub> :** {elu.get('Mr_MNm', 0.0):.3f} MN.m",
                unsafe_allow_html=True,
            )

    # === ELS ===
    with st.expander("✅ ELS – Vérification en service", expanded=True):
        st.markdown("**📐 Calculs ELS selon BAEL :**")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🧭 Axe neutre Y₁ :** {els.get('Y1_cm', 0.0):.2f} cm")
            st.markdown(
                f"**📏 Inertie I₉₉' :** {els.get('I_cm4', 0.0):.2f} cm⁴"
            )
            Ms_MNm = data["Ms"]
            I_m4 = els.get("I_m4", 0.0)
            k_val = Ms_MNm / I_m4 if I_m4 > 0 else 0.0
            st.markdown(f"**📈 Pente k = Ms/I₉₉' :** {k_val:.4f} MN/m³")

        with col2:
            st.markdown(f"**🧱 σb calculée :** {els.get('sigma_b_MPa', 0.0):.2f} MPa")
            st.markdown(
                f"**🧱 σb admissible :** {els.get('sigma_b_adm_MPa', 0.0):.2f} MPa"
            )
            st.markdown(f"**🔩 σs calculée :** {els.get('sigma_s_MPa', 0.0):.2f} MPa")
            st.markdown(
                f"**🔩 σs admissible :** {els.get('sigma_s_adm_MPa', 0.0):.2f} MPa"
            )

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            beton_ok = els.get("verif_beton", "NON") == "OK"
            acier_ok = els.get("verif_acier", "NON") == "OK"
            st.markdown("### 🧮 Vérifications")
            st.markdown(
                f"**🧱 σb ≤ σb,adm :** {'✅ OUI' if beton_ok else '❌ NON'}"
            )
            st.markdown(
                f"**🔩 σs ≤ σs,adm :** {'✅ OUI' if acier_ok else '❌ NON'}"
            )

        with col2:
            cas_num = els.get("cas", 1)
            if cas_num == 1:
                titre = "🏗️ Cas 1 ELU"
            elif cas_num == 2:
                titre = "🏗️ Cas 2 ELS armatures simples"
            else:
                titre = "🏗️ Cas 3 ELS armatures doubles"

            st.markdown(
                f"""
                <div style="background:#fff3cd; border:3px solid #ffc107; border-radius:12px;
                            padding:1.8rem; text-align:center; font-weight:800;
                            font-size:1.2rem; color:#22543d;">
                    {titre}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Nouveau calcul", use_container_width=True):
            for key in ["resultats_elu", "resultats_els", "donnees_saisie", "donnees_norm"]:
                st.session_state[key] = {} if key == "donnees_saisie" else None
            st.session_state.page = "saisie_rectangulaire"
            st.rerun()
    with col2:
        if st.button("📝 Modifier la saisie", use_container_width=True):
            st.session_state.page = "saisie_rectangulaire"
            st.rerun()
    with col3:
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state.page = "accueil"
            st.rerun()

    afficher_footer()


# =======================================================
# MAIN
# =======================================================
def main():
    st.sidebar.markdown("# 🧭 Navigation")
    if st.sidebar.button("🏠 Accueil"):
        st.session_state.page = "accueil"
        st.rerun()
    if st.sidebar.button("🧮 Saisie"):
        st.session_state.page = "saisie_rectangulaire"
        st.rerun()
    if st.sidebar.button("📊 Résultats") and st.session_state.resultats_elu:
        st.session_state.page = "resultats"
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("**RAHANI Soulaimane**")
    st.sidebar.markdown("**Futur Ingénieur d'État BTP**")
    st.sidebar.markdown("**© 2025**")

    if st.session_state.page == "accueil":
        page_accueil()
    elif st.session_state.page == "saisie_rectangulaire":
        page_saisie_rectangulaire()
    elif st.session_state.page == "resultats":
        page_resultats()


if __name__ == "__main__":
    main()
