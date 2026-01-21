import streamlit as st
import pandas as pd
import plotly.express as px

def afficher_carte_frequentation(engine, type_carte="Points"):
    """Génère la carte interactive selon le mode choisi : Points ou Chaleur"""
    st.subheader(f"📍 Carte de fréquentation ({type_carte})")
    
    try:
        # Requête SQL pour obtenir les volumes par commune géolocalisée
        query = """
            SELECT c.nom_c, c.lat, c.lon, COUNT(e.num) as nb_entretiens
            FROM public.entretien e
            JOIN public.commune c ON e.commune = c.nom_c
            WHERE c.lat IS NOT NULL
            GROUP BY c.nom_c, c.lat, c.lon
        """
        df_map = pd.read_sql(query, engine)
        
        if df_map.empty:
            st.info("Aucune donnée géographique disponible. Assurez-vous d'avoir lancé le script d'enrichissement.")
            return

        if type_carte == "Points":
            # Représentation avec des bulles (taille proportionnelle au nombre d'entretiens)
            fig = px.scatter_mapbox(
                df_map, 
                lat="lat", lon="lon", 
                size="nb_entretiens",
                color="nb_entretiens",
                hover_name="nom_c",
                color_continuous_scale=px.colors.sequential.YlOrRd,
                size_max=30, 
                zoom=9,
                mapbox_style="carto-positron"
            )
        else:
            # Carte de chaleur (Heatmap) : densité de fréquentation
            fig = px.density_mapbox(
                df_map, 
                lat="lat", lon="lon", 
                z="nb_entretiens", 
                radius=25,
                hover_name="nom_c",
                zoom=9,
                mapbox_style="carto-positron",
                color_continuous_scale=px.colors.sequential.YlOrRd
            )
        
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, width='stretch')

    except Exception as e:
        st.error(f"Erreur lors de la génération de la carte : {e}")