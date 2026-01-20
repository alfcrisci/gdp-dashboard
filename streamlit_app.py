# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configurazione pagina
st.set_page_config(
    page_title="Dashboard Vendite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titolo
st.title("📈 Dashboard Analitica Vendite")
st.markdown("---")

# Caricamento dati
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv')
        df['date'] = pd.to_datetime(df['date'])
        df['margin'] = (df['profit'] / df['sales'] * 100).round(2)
        return df
    except FileNotFoundError:
        # Se il file non esiste, crea dati di esempio
        st.warning("File data.csv non trovato. Genero dati di esempio...")
        return create_sample_data()

def create_sample_data():
    date_range = pd.date_range('2024-01-01', '2024-01-31')
    categories = ['Elettronica', 'Abbigliamento', 'Casa']
    products = {
        'Elettronica': ['Smartphone', 'Tablet', 'Laptop', 'TV', 'Smartwatch'],
        'Abbigliamento': ['Giacca', 'Pantaloni', 'Scarpe', 'Maglietta'],
        'Casa': ['Forno', 'Frigorifero', 'Lavatrice', 'Microonde']
    }
    regions = ['Nord', 'Centro', 'Sud']
    
    data = []
    for date in date_range:
        for category in categories:
            for product in products[category]:
                sales = np.random.randint(1000, 20000)
                profit = sales * np.random.uniform(0.25, 0.35)
                customers = int(sales / np.random.randint(40, 60))
                region = np.random.choice(regions)
                
                data.append({
                    'date': date,
                    'category': category,
                    'product': product,
                    'sales': sales,
                    'profit': profit,
                    'customers': customers,
                    'region': region
                })
    
    df = pd.DataFrame(data)
    df['margin'] = (df['profit'] / df['sales'] * 100).round(2)
    return df

# Carica dati
df = load_data()

# Sidebar - Filtri
st.sidebar.header("🔍 Filtri")

# Selettore data
min_date = df['date'].min()
max_date = df['date'].max()
date_range = st.sidebar.date_input(
    "Intervallo Date",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filtro categoria
categories = df['category'].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Categoria",
    options=categories,
    default=categories
)

# Filtro regione
regions = df['region'].unique().tolist()
selected_regions = st.sidebar.multiselect(
    "Regione",
    options=regions,
    default=regions
)

# Applica filtri
if len(date_range) == 2:
    mask = (
        (df['date'] >= pd.to_datetime(date_range[0])) &
        (df['date'] <= pd.to_datetime(date_range[1])) &
        (df['category'].isin(selected_categories)) &
        (df['region'].isin(selected_regions))
    )
    filtered_df = df[mask].copy()
else:
    filtered_df = df.copy()

# KPI Cards
st.subheader("📊 Indicatori Chiave (KPI)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_df['sales'].sum()
    delta_sales = ((filtered_df['sales'].sum() / df['sales'].sum()) - 1) * 100
    st.metric(
        label="Vendite Totali",
        value=f"€ {total_sales:,.0f}",
        delta=f"{delta_sales:+.1f}%"
    )

with col2:
    total_profit = filtered_df['profit'].sum()
    st.metric(
        label="Profitto Totale",
        value=f"€ {total_profit:,.0f}",
        delta=f"{(total_profit/total_sales*100):.1f}% margine"
    )

with col3:
    avg_customers = filtered_df['customers'].mean()
    st.metric(
        label="Clienti Medi Giornalieri",
        value=f"{avg_customers:.0f}",
        delta="per giorno"
    )

with col4:
    unique_products = filtered_df['product'].nunique()
    st.metric(
        label="Prodotti Venduti",
        value=unique_products,
        delta=f"{len(filtered_df)} transazioni"
    )

st.markdown("---")

# Grafici
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("💰 Andamento Vendite Giornaliero")
    
    # Dati aggregati per giorno
    daily_sales = filtered_df.groupby('date').agg({
        'sales': 'sum',
        'profit': 'sum',
        'customers': 'sum'
    }).reset_index()
    
    # Grafico lineare con Plotly
    fig = px.line(
        daily_sales,
        x='date',
        y='sales',
        title='Vendite per Data',
        labels={'sales': 'Vendite (€)', 'date': 'Data'},
        markers=True
    )
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🏷️ Vendite per Categoria")
    
    category_sales = filtered_df.groupby('category')['sales'].sum().reset_index()
    
    fig_pie = px.pie(
        category_sales,
        values='sales',
        names='category',
        hole=0.4,
        title='Distribuzione per Categoria'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Seconda riga di grafici
st.subheader("📈 Analisi Dettagliata")

tab1, tab2, tab3 = st.tabs(["Per Regione", "Top Prodotti", "Margini"])

with tab1:
    region_sales = filtered_df.groupby('region').agg({
        'sales': 'sum',
        'profit': 'sum',
        'customers': 'sum'
    }).reset_index()
    
    fig_bar = px.bar(
        region_sales,
        x='region',
        y='sales',
        color='region',
        title='Vendite per Regione',
        labels={'sales': 'Vendite (€)', 'region': 'Regione'},
        text='sales'
    )
    fig_bar.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    top_products = filtered_df.groupby('product').agg({
        'sales': 'sum',
        'profit': 'sum'
    }).nlargest(10, 'sales').reset_index()
    
    fig_bar_h = px.bar(
        top_products,
        y='product',
        x='sales',
        orientation='h',
        title='Top 10 Prodotti per Vendite',
        labels={'sales': 'Vendite (€)', 'product': 'Prodotto'},
        color='sales',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_bar_h, use_container_width=True)

with tab3:
    product_margin = filtered_df.groupby('product').agg({
        'sales': 'sum',
        'margin': 'mean'
    }).reset_index()
    
    fig_scatter = px.scatter(
        product_margin,
        x='sales',
        y='margin',
        size='sales',
        color='margin',
        hover_name='product',
        title='Margine vs Vendite per Prodotto',
        labels={'sales': 'Vendite (€)', 'margin': 'Margine %'},
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# Tabella dati
st.subheader("📋 Dati Dettagliati")

# Opzioni di visualizzazione
view_option = st.radio(
    "Visualizzazione dati:",
    ["Sintesi", "Dettaglio Completo"],
    horizontal=True
)

if view_option == "Sintesi":
    summary_df = filtered_df.groupby(['date', 'category', 'region']).agg({
        'sales': 'sum',
        'profit': 'sum',
        'customers': 'sum',
        'margin': 'mean'
    }).reset_index()
    st.dataframe(
        summary_df.sort_values('date', ascending=False),
        use_container_width=True
    )
else:
    st.dataframe(
        filtered_df.sort_values('date', ascending=False),
        use_container_width=True
    )

# Download dati
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Esporta Dati")

if st.sidebar.button("Scarica CSV Filtrato"):
    csv = filtered_df.to_csv(index=False)
    st.sidebar.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"dashboard_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Informazioni dashboard
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Informazioni Dashboard:**
    - Dati aggiornati al: {}
    - Totale record: {}
    - Periodo analizzato: {} - {}
    """.format(
        max_date.strftime('%d/%m/%Y'),
        len(filtered_df),
        filtered_df['date'].min().strftime('%d/%m'),
        filtered_df['date'].max().strftime('%d/%m')
    )
)

# Footer
st.markdown("---")
st.caption("Dashboard creata con Streamlit • Ultimo aggiornamento: " + datetime.now().strftime("%d/%m/%Y %H:%M"))
