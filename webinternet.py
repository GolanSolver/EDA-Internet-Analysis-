import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import json
import matplotlib.ticker as mtick

# Cargar datos
@st.cache_data
def load_data():
    file_path = 'Final.csv'
    df = pd.read_csv(file_path, usecols=lambda column: column not in ['Unnamed: 0'])
    return df

# Cargar datos geoespaciales
@st.cache_data
def load_geospatial_data():
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    with open('cables_dates.json', 'r') as json_file:
        data = json.load(json_file)
    cables_dates = data['cables_dates']
    cables = gpd.read_file('cables.geojson')
    return world, cables, cables_dates

df = load_data()
world, cables, cables_dates = load_geospatial_data()

# Listas de regiones y países
non_countries = [
    "East Asia and Pacific", "Europe and Central Asia", "Latin America and Caribbean",
    "North America", "Sub-Saharan Africa", "Middle East and North Africa", "South Asia", "World"
]
paises_europa = [ "Albania", "Latvia", "Andorra", "Liechtenstein", "Armenia", "Lithuania", "Austria", 
                  "Luxembourg", "Azerbaijan", "Malta", "Belarus", "Moldova", "Faeroe Islands", "Belgium", 
                  "Monaco", "Bosnia and Herzegovina", "Montenegro", "Bulgaria", "Netherlands", "Croatia", 
                  "Norway", "Cyprus", "Poland", "Czechia", "Portugal", "Denmark", "Romania", "Estonia", 
                  "Russia", "Finland", "San Marino", "North Macedonia", "Serbia", "France", "Slovakia", 
                  "Gibraltar", "Georgia", "Slovenia", "Germany", "Spain", "Greece", "Sweden", "Hungary", 
                  "Iceland", "Switzerland", "Ireland", "Turkey", "Italy", "Ukraine", "Kosovo", "United Kingdom"]
paises_africa = [ "Algeria", "Egypt", "Ethiopia", "Guinea", "Papua New Guinea", "Guinea-Bissau", "Liberia", 
                  "Morocco", "Senegal", "Togo", "Tunisia", "Zambia", "Angola", "Benin", "Botswana", "Burkina Faso", 
                  "Burundi", "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros", "Cote d'Ivoire", 
                  "Democratic Republic of Congo", "Djibouti", "Equatorial Guinea", "Eritrea", "Eswatini", "Gabon", 
                  "Gambia", "Ghana", "Kenya", "Lesotho", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania", 
                  "Mauritius", "Mozambique", "Namibia", "Niger", "Nigeria", "Congo", "Rwanda", "Sao Tome and Principe", 
                  "Seychelles", "Sierra Leone", "South Africa", "South Sudan", "Sudan", "Tanzania", "Uganda", "Zimbabwe", 
                  "Somalia"]
paises_america = [ "Antigua and Barbuda", "Argentina", "Bahamas", "Barbados", "Belize", "Turks and Caicos Islands", 
                   "Bolivia", "Brazil", "Canada", "Chile", "Colombia", "Cayman Islands", "Greenland", "Curacao", 
                   "Costa Rica", "Cuba", "Dominica", "Dominican Republic", "Ecuador", "British Virgin Islands", 
                   "Sint Maarten (Dutch part)", "El Salvador", "Grenada", "Guatemala", "Guyana", "Haiti", "American Samoa", 
                   "United States Virgin Islands", "Honduras", "Jamaica", "Mexico", "Nicaragua", "Panama", "Aruba", 
                   "Bermuda", "French Polynesia", "Paraguay", "Peru", "Saint Kitts and Nevis", "Saint Lucia", 
                   "Saint Vincent and the Grenadines", "Suriname", "Trinidad and Tobago", "United States", "Uruguay", 
                   "Venezuela", "Guam", "Puerto Rico"]
paises_asia = [ "Afghanistan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Macao", "Cambodia", "China", "India", 
                "Indonesia", "Iran", "Hong Kong", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan", "Timor", "Kuwait", 
                "Kyrgyzstan", "Laos", "Lebanon", "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal", "North Korea", 
                "Oman", "Pakistan", "Palestine", "Philippines", "Qatar", "Saudi Arabia", "Singapore", "South Korea", 
                "Sri Lanka", "Syria", "Taiwan", "Tajikistan", "Thailand", "Timor-Leste", "Turkmenistan", 
                "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen"]
paises_oceania = [ "Australia", "Fiji", "Kiribati", "Marshall Islands", "Micronesia", "Nauru", "New Zealand", 
                   "Palau", "Samoa", "Solomon Islands", "Northern Mariana Islands", "Tonga", "Tuvalu", "Vanuatu", 
                   "Micronesia (country)", "New Caledonia"]

continent_dict = {}
for country in paises_europa:
    continent_dict[country] = 'Europe'
for country in paises_africa:
    continent_dict[country] = 'Africa'
for country in paises_america:
    continent_dict[country] = 'America'
for country in paises_asia:
    continent_dict[country] = 'Asia'
for country in paises_oceania:
    continent_dict[country] = 'Oceania'

df['Continent'] = df['Entity'].map(continent_dict)

# Navegación de páginas
page = st.sidebar.selectbox("Selecciona una página", ["Visualización de Datos", "Visualización de Datos en Mapas", "Tablas de Datos"])

if page == "Visualización de Datos":
    st.title('Visualización de datos')
    
    # Widgets de selección
    chart_type = st.selectbox('Selecciona el tipo de gráfica', ['Barras', 'Líneas', 'Histograma', 'Dispersión', 'Caja y bigotes'])
    year_placeholder = st.empty()
    if chart_type != 'Líneas':
        year = year_placeholder.slider('Selecciona el año', min_value=int(df['Year'].min()), max_value=int(df['Year'].max()), value=int(df['Year'].max()))
    else:
        year = None

    # Widget para seleccionar la variable en gráficos de barras
    if chart_type == 'Barras':
        variable = st.selectbox('Selecciona la variable', ['No. of Internet Users', 'Internet Users(%)', 'Cellular Subscription', 'Broadband Subscription'], index=0)
    else:
        variable = None
    
    # Función para generar gráficas
    def generate_chart(chart_type, year, variable=None):
        if chart_type == 'Barras':
            data_year = df[(df['Year'] == year) & (~df['Entity'].isin(non_countries))]
            top_10 = data_year.sort_values(variable, ascending=False).head(10)
            colors = sns.color_palette('hsv', n_colors=len(top_10))
            
            fig, ax = plt.subplots(figsize=(10, 6))
            if variable == 'No. of Internet Users':
                y_values = top_10[variable].astype(float) / 1000000
                barplot = sns.barplot(x='Code', y=y_values, data=top_10, palette=colors, ax=ax)
                fmt = '{x:.0f}M'
                tick = mtick.StrMethodFormatter(fmt)
                barplot.yaxis.set_major_formatter(tick)
                ylabel = 'Number of Internet Users (millions)'
            else:
                y_values = top_10[variable]
                barplot = sns.barplot(x='Code', y=y_values, data=top_10, palette=colors, ax=ax)
                ax.yaxis.set_major_formatter(mtick.PercentFormatter())
                ylabel = variable

            plt.title(f'{variable} by Country in {year} (Top 10)')
            plt.ylabel(ylabel)
            st.pyplot(fig)
            st.write(f'Gráfica de barras del {variable} en el año {year} para los 10 países principales.')
            
        elif chart_type == 'Líneas':
            entities = st.multiselect('Selecciona las entidades', df['Entity'].unique(), default=non_countries)
            df_countries = df[df['Entity'].isin(entities)]
            df_pivot = df_countries.pivot(index='Year', columns='Entity', values='Internet Users(%)')

            plt.figure(figsize=(14, 7))
            for country in df_pivot.columns:
                plt.plot(df_pivot.index, df_pivot[country], marker='', linewidth=2, label=country)

            plt.title('Share of the Population Using the Internet Over Time')
            plt.xlabel('Year')
            plt.ylabel('Internet Users (%)')
            plt.legend(loc='upper left', ncol=2, fontsize='small')
            plt.grid(True)
            st.pyplot(plt)
            st.write('Gráfica de líneas que muestra el porcentaje de la población que usa Internet a lo largo del tiempo.')

        elif chart_type == 'Histograma':
            hist_type = st.selectbox('Selecciona el tipo de histograma', ['Individual', 'Múltiple'])
            continent_options = {
                'Europa': paises_europa,
                'África': paises_africa,
                'América': paises_america,
                'Asia': paises_asia,
                'Oceanía': paises_oceania
            }

            if hist_type == 'Individual':
                selected_continent = st.selectbox('Selecciona el continente', list(continent_options.keys()))
                selected_countries = continent_options[selected_continent]
                df_continent_year = df[(df['Year'] == year) & (df['Entity'].isin(selected_countries))]

                plt.figure(figsize=(10, 6))
                plt.hist(df_continent_year['Internet Users(%)'], bins=20, color='blue', edgecolor='black')
                plt.title(f'Distribución de Usuarios de Internet (%) en {selected_continent} para {year}')
                plt.xlabel('Porcentaje de Usuarios de Internet (%)')
                plt.ylabel('Cantidad de Países')
                st.pyplot(plt)
                st.write(f'Histograma del porcentaje de usuarios de Internet en {selected_continent} para el año {year}.')

            elif hist_type == 'Múltiple':
                selected_continents = st.multiselect('Selecciona los continentes', list(continent_options.keys()), default=['Europa', 'África'])
                if len(selected_continents) < 2:
                    st.warning('Por favor, selecciona al menos dos continentes.')
                else:
                    plt.figure(figsize=(12, 8))
                    for continent in selected_continents:
                        selected_countries = continent_options[continent]
                        df_continent_year = df[(df['Year'] == year) & (df['Entity'].isin(selected_countries))]
                        plt.hist(df_continent_year['Internet Users(%)'], bins=20, alpha=0.5, edgecolor='black', label=continent)

                    plt.title(f'Distribución de Usuarios de Internet (%) en {", ".join(selected_continents)} para {year}')
                    plt.xlabel('Porcentaje de Usuarios de Internet (%)')
                    plt.ylabel('Cantidad de Países')
                    plt.legend()
                    st.pyplot(plt)
                    st.write(f'Histograma comparativo del porcentaje de usuarios de Internet en los continentes {", ".join(selected_continents)} para el año {year}.')

        elif chart_type == 'Dispersión':
            df_year = df[df["Year"] == year]
            show_regression = st.checkbox('Mostrar regresión', value=False)
            
            plt.figure(figsize=(10, 6))
            if show_regression:
                sns.regplot(x='Cellular Subscription', y='Broadband Subscription', data=df_year[df_year["Cellular Subscription"] < 250], scatter_kws={'alpha':0.5}, line_kws={"color":"red"}, order=1)
            else:
                plt.scatter(df_year['Cellular Subscription'], df_year['Broadband Subscription'], alpha=0.5)
            
            plt.xlabel('Cellular Subscription')
            plt.ylabel('Broadband Subscription')
            plt.title(f'Scatter Plot of Cellular Subscription vs. Broadband Subscription ({year})')
            st.pyplot(plt)
            st.write(f'Diagrama de dispersión de las suscripciones celulares frente a las suscripciones de banda ancha en el año {year}.')
            
        elif chart_type == 'Caja y bigotes':
            df_continents_year = df[df['Continent'].notna() & (df['Year'] == year)]
            
            metric = st.selectbox('Selecciona la métrica', ['Cellular Subscription', 'Broadband Subscription', 'Internet Users(%)', 'No. of Internet Users'])

            plt.figure(figsize=(12, 8))
            sns.boxplot(x='Continent', y=metric, data=df_continents_year)
            plt.xticks(rotation=45)
            plt.title(f'Distribution of {metric} by Continent in {year}')
            if metric == 'No. of Internet Users':
                plt.ylabel(f'{metric} (millions)')
            else:
                plt.ylabel(f'{metric} (%)')
            plt.xlabel('Continent')
            st.pyplot(plt)
            st.write(f'Gráfico de caja y bigotes de la distribución de {metric} por continente en el año {year}.')

    # Generar gráfica basada en selección
    generate_chart(chart_type, year, variable)

elif page == "Visualización de Datos en Mapas":
    st.title('Visualización de datos en Mapas')

    # Preparación de datos
    df = df[df['Year'] >= 1989]
    df = df[~df['Entity'].isin(non_countries)]
    
    name_mapping = {
        "Cote d'Ivoire": "Côte d'Ivoire", "Central African Republic": "Central African Rep.",
        "South Sudan": "S. Sudan", "Democratic Republic of Congo": "Dem. Rep. Congo",
        "United States": "United States of America", "Sub-Saharan Africa": "W. Sahara",
        "Dominican Republic": "Dominican Rep.", "Argentina": "Falkland Is.", "Antarctica": "Fr. S. Antarctic Lands",
        "Timor": "Timor-Leste", "Equatorial Guinea": "Eq. Guinea", "Eswatini": "eSwatini",
        "Solomon Islands": "Solomon Is.", "China": "Taiwan", "Cyprus": "N. Cyprus", "Somalia": "Somaliland",
        "Bosnia and Herzegovina": "Bosnia and Herz."
    }
    
    additional_rows = []
    
    for original, mapped in name_mapping.items():
        matching_rows = df[df['Entity'] == original].copy()
        matching_rows['Entity'] = mapped
        additional_rows.append(matching_rows)
    
    df_extended = pd.concat([df] + additional_rows, ignore_index=True)
    
    world_with_dates = world.merge(df_extended, how="left", left_on="name", right_on="Entity")

    # Slider para seleccionar el año
    year = st.slider('Selecciona el año', min_value=int(df['Year'].min()), max_value=int(df['Year'].max()), value=int(df['Year'].max()))

    # Selección del tipo de mapa
    map_option = st.selectbox('Selecciona el tipo de mapa', [
        "Number of Internet Users in Million", 
        "Internet Users (%)",
        "Cellular Subscription",
        "Broadband Subscription",
        "Gradient Map of Cellular Subscription vs Broadband Subscription"
    ])

    # Toggle para mostrar por continente o por país
    show_by_continent = st.checkbox('Mostrar por continentes', value=False)

    # Opción para mostrar cables submarinos
    show_cables = st.checkbox('Mostrar cables submarinos hasta el año seleccionado', value=False)

    # Filtrar datos para el año seleccionado y excluir entradas que no son países
    data_year = world_with_dates[(world_with_dates['Year'] == year) & (~world_with_dates['Entity'].isin(non_countries))]

    # Disolver datos por continente si se selecciona la opción
    if show_by_continent:
        data_year = data_year.dissolve(by='continent', aggfunc={
            'Cellular Subscription': 'mean',
            'Internet Users(%)': 'mean',
            'No. of Internet Users': 'mean',
            'Broadband Subscription': 'mean'
        }).reset_index()

    # Mapa basado en la opción seleccionada
    if map_option == "Number of Internet Users in Million":
        column = 'No. of Internet Users'
        title = f'Number of Internet Users in Millions by {"Continent" if show_by_continent else "Country"} in {year}'
        if not show_by_continent:
            data_year[column] = data_year[column] / 1000000  # Convertir a millones
        description = f'Mapa del número de usuarios de Internet en millones en el año {year}'
    elif map_option == "Internet Users (%)":
        column = 'Internet Users(%)'
        title = f'Internet Users (%) by {"Continent" if show_by_continent else "Country"} in {year}'
        description = f'Mapa del porcentaje de usuarios de Internet en el año {year}'
    elif map_option == "Cellular Subscription":
        column = 'Cellular Subscription'
        title = f'Cellular Subscription by {"Continent" if show_by_continent else "Country"} in {year}'
        description = f'Mapa de suscripciones celulares en el año {year}'
    elif map_option == "Broadband Subscription":
        column = 'Broadband Subscription'
        title = f'Broadband Subscription by {"Continent" if show_by_continent else "Country"} in {year}'
        description = f'Mapa de suscripciones de banda ancha en el año {year}'
    elif map_option == "Gradient Map of Cellular Subscription vs Broadband Subscription":
        data_year['Cellular Subscription (normalized)'] = (data_year['Cellular Subscription'] - data_year['Cellular Subscription'].min()) / (data_year['Cellular Subscription'].max() - data_year['Cellular Subscription'].min())
        data_year['Broadband Subscription (normalized)'] = (data_year['Broadband Subscription'] - data_year['Broadband Subscription'].min()) / (data_year['Broadband Subscription'].max() - data_year['Broadband Subscription'].min())
        data_year['Gradient'] = data_year['Cellular Subscription (normalized)'] - data_year['Broadband Subscription (normalized)']
        column = 'Gradient'
        title = f'Gradient Map of Cellular Subscription vs Broadband Subscription by {"Continent" if show_by_continent else "Country"} in {year}'
        description = f'Mapa de gradiente de suscripciones celulares frente a suscripciones de banda ancha en el año {year}'
    
    if show_by_continent:
        description += " por continente"
    else:
        description += " por país"

    if show_cables:
        description += " con cables submarinos"

    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    data_year.boundary.plot(ax=ax, linewidth=1, edgecolor='k')
    data_year.plot(column=column, ax=ax, legend=True,
                   legend_kwds={'label': column, 'orientation': "horizontal"},
                   missing_kwds={'color': 'lightgrey', 'edgecolor': 'red', 'hatch': '//'},
                   cmap='OrRd' if map_option != "Gradient Map of Cellular Subscription vs Broadband Subscription" else 'coolwarm')
    plt.title(title)
    
    if show_cables:
        # Convertir la lista de tuplas en un df
        cables_dates_df = pd.DataFrame(cables_dates, columns=['slug', 'slugDate'])

        # Concatenamos ambos df
        cables_with_dates = pd.merge(cables, cables_dates_df, on='slug', how='left')

        # Filtramos los cables hasta el año seleccionado
        cables_up_to_year = cables_with_dates[cables_with_dates['slugDate'] <= year]

        cables_up_to_year.plot(ax=ax, linewidth=2, cmap='Paired', alpha=0.8, legend=True, label='Submarine Cables')

    st.pyplot(fig)
    st.write(description)

elif page == "Tablas de Datos":
    st.title('Tablas de Datos')

    # Widget para seleccionar el archivo
    data_option = st.selectbox('Selecciona el archivo de datos', ['Evolución de Internet', 'Cables Submarinos'])

    # Mostrar tabla basada en selección
    if data_option == 'Evolución de Internet':
        st.write(df)
        st.write("Datos sobre la Evolución del consumo de Internet")
    elif data_option == 'Cables Submarinos':
        cables_dates_df = pd.DataFrame(cables_dates, columns=['Cable', 'Incorporation Date'])
        st.write(cables_dates_df)
        st.write("Datos sobre los cables submarinos y su Incorparación")