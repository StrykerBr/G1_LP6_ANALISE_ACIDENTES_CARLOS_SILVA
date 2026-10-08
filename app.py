import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

st.set_page_config(
    page_title="Análise de Acidentes de Trânsito",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }

    div[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #262730;
    }

    .info-card {
        background-color: #161b22;
        border: 1px solid #262730;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .info-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-top: 16px;
    }

    .info-box {
        background: rgba(255, 255, 255, 0.03);
        padding: 14px;
        border-radius: 8px;
        border-left: 4px solid #4f8bf9;
    }

    .info-box label {
        display: block;
        font-size: 0.75rem;
        color: #a3adc2;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }

    .info-box span {
        font-size: 0.95rem;
        font-weight: 600;
        color: #fafafa;
    }

    .action-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 18px;
        margin-top: 20px;
    }

    .action-card {
        border-radius: 10px;
        padding: 20px;
        border: 1px solid transparent;
    }

    .action-card h3 {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .action-card ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .action-card li {
        font-size: 0.88rem;
        line-height: 1.5;
        margin-bottom: 10px;
        color: #e0e6ed;
    }

    .action-card li strong {
        color: #ffffff;
    }

    .action-blue {
        background-color: rgba(26, 54, 93, 0.4);
        border-color: #2b6cb0;
    }
    .action-blue h3 { color: #63b3ed; }

    .action-yellow {
        background-color: rgba(90, 74, 22, 0.4);
        border-color: #b7791f;
    }
    .action-yellow h3 { color: #f6e05e; }

    .action-green {
        background-color: rgba(20, 71, 48, 0.4);
        border-color: #2f855a;
    }
    .action-green h3 { color: #68d391; }

    @media (max-width: 900px) {
        .info-grid, .action-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    try:
        engine = create_engine('sqlite:///acidentes.db')
        df = pd.read_sql('SELECT * FROM acidentes', engine)
    except Exception:
        df = pd.read_csv('acidentes_brasil.csv')
    
    if 'ano' in df.columns:
        df['ano'] = df['ano'].astype(int)
    return df

df = carregar_dados()

st.sidebar.header("🔍 Filtros de Análise")

anos_disponiveis = sorted(df['ano'].unique().tolist()) if 'ano' in df.columns else []
anos_selecionados = st.sidebar.multiselect("Selecione o(s) Ano(s):", anos_disponiveis, default=anos_disponiveis)

regioes_disponiveis = sorted(df['regiao'].unique().tolist()) if 'regiao' in df.columns else []
regioes_selecionadas = st.sidebar.multiselect("Selecione a(s) Região(ões):", regioes_disponiveis, default=regioes_disponiveis)

ufs_disponiveis = sorted(df[df['regiao'].isin(regioes_selecionadas)]['uf'].unique().tolist()) if 'uf' in df.columns else []
ufs_selecionadas = st.sidebar.multiselect("Selecione a(s) UF(s):", ufs_disponiveis, default=ufs_disponiveis)

clima_disponivel = sorted(df['condicao_metereologica'].unique().tolist()) if 'condicao_metereologica' in df.columns else []
clima_selecionado = st.sidebar.multiselect("Condição Climática:", clima_disponivel, default=clima_disponivel)

df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['regiao'].isin(regioes_selecionadas)) &
    (df['uf'].isin(ufs_selecionadas)) &
    (df['condicao_metereologica'].isin(clima_selecionado))
]

st.title("🚗 Análise e Monitoramento de Acidentes de Trânsito no Brasil")

st.markdown("""
<div class="info-card">
    <div class="info-grid">
        <div class="info-box">
            <label>🎓 Projeto Acadêmico</label>
            <span>Linguagem de Programação — Python</span>
        </div>
        <div class="info-box">
            <label>👨‍🏫 Orientação</label>
            <span>Prof. Alexandre Neves Louzada</span>
        </div>
        <div class="info-box">
            <label>👤 Autoria</label>
            <span>Carlos Gabriel Anselmo Da Silva</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.subheader("📊 Indicadores Principais (KPIs)")

col1, col2, col3, col4 = st.columns(4)
total_acidentes = len(df_filtrado)
total_vitimas = df_filtrado['vitimas'].sum() if 'vitimas' in df_filtrado.columns else 0
total_obitos = df_filtrado['mortos'].sum() if 'mortos' in df_filtrado.columns else 0
media_severidade = df_filtrado['taxa_severidade'].mean() if 'taxa_severidade' in df_filtrado.columns else 0.0

col1.metric("Total de Acidentes", f"{total_acidentes:,}".replace(",", "."))
col2.metric("Total de Vítimas", f"{int(total_vitimas):,}".replace(",", "."))
col3.metric("Total de Óbitos", f"{int(total_obitos):,}".replace(",", "."))
col4.metric("Taxa Média de Severidade", f"{media_severidade:.2f}")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📈 Análise Temporal & Geográfica", "🌧️ Clima & Tipos de Acidente", "📋 Tabela de Dados"])

with tab1:
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Evolução Temporal de Acidentes e Óbitos")
        if 'ano' in df_filtrado.columns and not df_filtrado.empty:
            df_temp = df_filtrado.groupby('ano').agg({'id': 'count', 'mortos': 'sum'}).reset_index()
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(x=df_temp['ano'], y=df_temp['id'], mode='lines+markers', name='Acidentes', line=dict(color='#4f8bf9', width=3)))
            fig_temp.add_trace(go.Scatter(x=df_temp['ano'], y=df_temp['mortos'], mode='lines+markers', name='Óbitos', line=dict(color='#ff4b4b', width=3)))
            fig_temp.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_temp, use_container_width=True)

    with c2:
        st.subheader("Taxa de Severidade por Região")
        if 'regiao' in df_filtrado.columns and 'taxa_severidade' in df_filtrado.columns and not df_filtrado.empty:
            df_reg = df_filtrado.groupby('regiao')['taxa_severidade'].mean().reset_index().sort_values(by='taxa_severidade', ascending=False)
            fig_reg = px.bar(df_reg, x='regiao', y='taxa_severidade', color='taxa_severidade', color_continuous_scale='Blues')
            fig_reg.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_reg, use_container_width=True)

with tab2:
    st.subheader("Impacto Climático e Causa das Ocorrências")
    if 'condicao_metereologica' in df_filtrado.columns and not df_filtrado.empty:
        df_clima = df_filtrado.groupby('condicao_metereologica')['id'].count().reset_index()
        fig_clima = px.pie(df_clima, values='id', names='condicao_metereologica', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_clima.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_clima, use_container_width=True)

with tab3:
    st.subheader("Registros Detalhados")
    st.dataframe(df_filtrado, use_container_width=True)

st.markdown("---")

st.markdown("## 💡 Conclusão Executiva & Planos de Ação")
st.write("A análise detalhada dos dados do sistema de trânsito revela padrões críticos que exigem intervenções direcionadas. Abaixo estão sintetizadas as diretrizes estratégicas para mitigação de acidentes e aumento da segurança viária:")

st.markdown("""
<div class="action-grid">
    <div class="action-card action-blue">
        <h3>🚨 1. Fiscalização Preventiva</h3>
        <ul>
            <li><strong>Foco:</strong> Trechos de alta severidade e rodovias críticas.</li>
            <li><strong>Ação:</strong> Intensificação de patrulhamento inteligente em períodos noturnos e de visibilidade reduzida.</li>
            <li><strong>Objetivo:</strong> Reduzir colisões de alta velocidade e capotamentos.</li>
        </ul>
    </div>
    <div class="action-card action-yellow">
        <h3>🌧️ 2. Gestão Climática Viária</h3>
        <ul>
            <li><strong>Foco:</strong> Períodos de chuva, neblina e pista molhada.</li>
            <li><strong>Ação:</strong> Instalação de painéis dinâmicos de mensagem para alerta de velocidade em tempo real.</li>
            <li><strong>Objetivo:</strong> Prevenir saídas de pista e aquaplanagem.</li>
        </ul>
    </div>
    <div class="action-card action-green">
        <h3>🛠️ 3. Engenharia & Infraestrutura</h3>
        <ul>
            <li><strong>Foco:</strong> Mapeamento de pontos pretos (black spots) recorrentes.</li>
            <li><strong>Ação:</strong> Implementação de defensas metálicas, melhoria do asfalto drenante e sinalização refletiva.</li>
            <li><strong>Objetivo:</strong> Minimizar a gravidade dos impactos e proteger vidas.</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📌 Síntese para Gestores e Tomadores de Decisão"):
    st.write("""
    A integração entre ações educativas, investimento direcionado na melhoria do pavimento e atuação focada da fiscalização rodoviária nos horários e locais de maior risco representa a estratégia de maior custo-benefício para a redução sustentada de vítimas fatais e acidentes graves.
    """)
