import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Acidentes de Trânsito no Brasil",
    page_icon="🚗",
    layout="wide"
)

# Estilo e Cabeçalho
st.title("🚗 Análise e Monitoramento de Acidentes de Trânsito no Brasil")
st.markdown("""
**Disciplina:** Linguagem de Programação – Análise e Visualização de Dados com Python  
**Professor:** Alexandre Neves Louzada  
**Aluno:** Carlos Gabriel Anselmo Da Silva  
**Tema 5:** Acidentes de Trânsito no Brasil
---
""")

# Carregamento de dados (via SQLite/Pandas)
@st.cache_data
def load_data():
    try:
        engine = create_engine('sqlite:///acidentes_transito.db')
        df = pd.read_sql_table('acidentes', con=engine)
    except:
        url = "https://raw.githubusercontent.com/AlexandreLouzada/Dados-Simulados-G2/main/datasets_g2_30_temas/simulacao_acidentes_transito_brasil.csv"
        df = pd.read_csv(url)
        df['total_vitimas'] = df['feridos'] + df['obitos']
        df['taxa_severidade'] = (df['total_vitimas'] / df['acidentes']).round(4)
    return df

df = load_data()

# Barra Lateral - Filtros Múltiplos
st.sidebar.header("🔍 Filtros de Análise")

anos_disponiveis = sorted(df['ano'].unique().tolist())
anos_selecionados = st.sidebar.multiselect("Selecione o(s) Ano(s):", anos_disponiveis, default=anos_disponiveis)

regioes_disponiveis = sorted(df['regiao'].unique().tolist())
regioes_selecionadas = st.sidebar.multiselect("Selecione a(s) Região(ões):", regioes_disponiveis, default=regioes_disponiveis)

df_filtrado_reg = df[df['regiao'].isin(regioes_selecionadas)]
ufs_disponiveis = sorted(df_filtrado_reg['uf'].unique().tolist())
ufs_selecionadas = st.sidebar.multiselect("Selecione a(s) UF(s):", ufs_disponiveis, default=ufs_disponiveis)

climas_disponiveis = sorted(df['condicao_climatica'].unique().tolist())
climas_selecionados = st.sidebar.multiselect("Condição Climática:", climas_disponiveis, default=climas_disponiveis)

# Aplicar Filtros
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['regiao'].isin(regioes_selecionadas)) &
    (df['uf'].isin(ufs_selecionadas)) &
    (df['condicao_climatica'].isin(climas_selecionados))
]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    # KPIs Dinâmicos
    st.subheader("📊 Indicadores Principais (KPIs)")
    col1, col2, col3, col4 = st.columns(4)
    
    tot_acidentes = int(df_filtrado['acidentes'].sum())
    tot_vitimas = int(df_filtrado['total_vitimas'].sum())
    tot_obitos = int(df_filtrado['obitos'].sum())
    taxa_media = df_filtrado['taxa_severidade'].mean()
    
    col1.metric("Total de Acidentes", f"{tot_acidentes:,}".replace(",", "."))
    col2.metric("Total de Vítimas", f"{tot_vitimas:,}".replace(",", "."))
    col3.metric("Total de Óbitos", f"{tot_obitos:,}".replace(",", "."))
    col4.metric("Taxa Média de Severidade", f"{taxa_media:.2f}")

    st.markdown("---")

    # Abas Organizadoras
    aba1, aba2, aba3 = st.tabs(["📈 Análise Temporal & Geográfica", "🌧️ Clima & Tipos de Acidente", "📋 Tabela de Dados"])

    with aba1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Evolução Temporal de Acidentes e Óbitos")
            df_temp = df_filtrado.groupby('ano')[['acidentes', 'obitos']].sum().reset_index()
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(x=df_temp['ano'], y=df_temp['acidentes'], mode='lines+markers', name='Acidentes', line=dict(color='steelblue')))
            fig_temp.add_trace(go.Scatter(x=df_temp['ano'], y=df_temp['obitos'], mode='lines+markers', name='Óbitos', line=dict(color='crimson')))
            fig_temp.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350)
            st.plotly_chart(fig_temp, use_container_width=True)

        with c2:
            st.markdown("##### Taxa de Severidade por Região")
            df_reg = df_filtrado.groupby('regiao')['taxa_severidade'].mean().reset_index().sort_values(by='taxa_severidade', ascending=False)
            fig_reg = px.bar(df_reg, x='regiao', y='taxa_severidade', color='taxa_severidade', color_continuous_scale='Blues')
            fig_reg.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350)
            st.plotly_chart(fig_reg, use_container_width=True)

    with aba2:
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("##### Severidade por Condição Climática")
            df_cli = df_filtrado.groupby('condicao_climatica')['taxa_severidade'].mean().reset_index().sort_values(by='taxa_severidade', ascending=False)
            fig_cli = px.bar(df_cli, x='condicao_climatica', y='taxa_severidade', color='condicao_climatica', color_discrete_sequence=px.colors.qualitative.Set2)
            fig_cli.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350)
            st.plotly_chart(fig_cli, use_container_width=True)

        with c4:
            st.markdown("##### Total de Vítimas por Tipo de Acidente")
            df_tipo = df_filtrado.groupby('tipo_acidente')['total_vitimas'].sum().reset_index().sort_values(by='total_vitimas', ascending=True)
            fig_tipo = px.bar(df_tipo, y='tipo_acidente', x='total_vitimas', orientation='h', color='total_vitimas', color_continuous_scale='Reds')
            fig_tipo.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350)
            st.plotly_chart(fig_tipo, use_container_width=True)

    with aba3:
        st.markdown("##### Visão Detalhada dos Registros Filtrados")
        st.dataframe(df_filtrado, use_container_width=True)

    st.markdown("---")
    st.markdown("### 💡 Conclusão Executiva")
    st.info("""
    **Direcionamento Estratégico:** A análise interativa permite mapear detalhadamente os pontos críticos da malha viária brasileira. 
    Recomenda-se focar ações educativas e de fiscalização preventiva nas regiões e períodos com condições climáticas adversas e maior proporção de vítimas por ocorrência.
    """)
