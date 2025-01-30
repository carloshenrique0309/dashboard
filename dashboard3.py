import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely import wkt
from streamlit_folium import folium_static
import sys
import random

# Função para gerar uma cor aleatória
def generate_random_color():
    return f'#{random.randint(0, 0xFFFFFF):06x}'

try:
    def load_data(file):
        try:
            df = pd.read_csv(file)
            df["geometry"] = df["geometry"].apply(lambda x: wkt.loads(x) if pd.notnull(x) else None)  # Converte WKT para geometria
            df = df.dropna(subset=["geometry"])  # Remove linhas com geometria nula
            return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo {file.name}: {e}")
            return None

    # Título do Dashboard
    st.title("Dashboard Interativo com Mapa")

    # Upload de arquivos CSV
    uploaded_files = st.file_uploader("Carregar arquivos CSV", type=["csv"], accept_multiple_files=True)

    gdfs = {}
    if uploaded_files:
        for file in uploaded_files:
            name = file.name.split(".")[0]
            gdf = load_data(file)
            if gdf is not None and not gdf.empty:
                gdfs[name] = gdf

        if gdfs:
            # Criar um mapa base
            m = folium.Map(location=[-15, -55], zoom_start=4)

            # Seletor para camadas
            selected_layers = st.sidebar.multiselect("Escolha as camadas para visualizar", list(gdfs.keys()))

            # Adicionar camadas selecionadas
            for i, layer in enumerate(selected_layers):
                if not gdfs[layer].empty:
                    geojson_data = gdfs[layer].to_json()
                    folium.GeoJson(
                        geojson_data,
                        name=layer,
                        tooltip=folium.GeoJsonTooltip(fields=[col for col in gdfs[layer].columns if col != "geometry"]),
                        style_function=lambda x: {
                            'fillColor': generate_random_color(),
                            'color': 'black',
                            'weight': 1,
                            'fillOpacity': 0.5
                        }
                    ).add_to(m)

            folium.LayerControl().add_to(m)

            # Exibir mapa
            folium_static(m)
        else:
            st.warning("Nenhum dado válido foi carregado. Verifique os arquivos CSV.")

        # Exibição das bases carregadas (fora do mapa, em área separada)
        st.sidebar.subheader("Bases Carregadas")
        for name in gdfs.keys():
            st.sidebar.write(name)

except ModuleNotFoundError as e:
    sys.stderr.write(f"Módulo não encontrado: {e}. Certifique-se de instalar as dependências corretamente.\n")
    # Em vez de sys.exit(1), lança a exceção para permitir que o IPython a trate
    raise e
