"""
Dashboard Interativo — Case Saude+ | Mevo
Streamlit + Plotly
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Saúde+ Analytics | Mevo",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta Mevo ───────────────────────────────────────────────────────────────
ROXO       = "#381267"
ROXO_MED   = "#5B2D8E"
ROSA_CLARO = "#FFE4EB"
ROSA_MED_C = "#FBBCCE"
ROSA_AC    = "#F687B3"
ALERTA     = "#E53E3E"
CINZA      = "#718096"
ESCURO     = "#1A202C"

PALETTE = [ROXO, ROXO_MED, ROSA_AC, "#ED8936", ALERTA, "#38A169", "#3182CE", CINZA]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    .stApp {{ background-color: #FAFAFA; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {ROSA_CLARO};
        border-radius: 6px 6px 0 0;
        padding: 8px 18px;
        color: {ROXO};
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {ROXO} !important;
        color: white !important;
    }}
    .metric-card {{
        background: white;
        border-radius: 10px;
        padding: 18px 20px;
        border-top: 4px solid {ROXO};
        box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {ROXO};
        line-height: 1.1;
    }}
    .metric-label {{
        font-size: 0.82rem;
        color: {CINZA};
        margin-top: 4px;
    }}
    .insight-box {{
        background: {ROSA_CLARO};
        border-left: 4px solid {ROXO};
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.9rem;
        color: {ESCURO};
    }}
    .alert-box {{
        background: #FFF5F5;
        border-left: 4px solid {ALERTA};
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.9rem;
        color: {ESCURO};
    }}
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():
    presc   = pd.read_csv(os.path.join(BASE, "prescricaomedicamento.csv"))
    meds    = pd.read_csv(os.path.join(BASE, "medicamentos.csv"))
    medicos = pd.read_csv(os.path.join(BASE, "medicos.csv"))

    presc["dataprescricao"]     = pd.to_datetime(presc["dataprescricao"])
    presc["datavenda"]          = pd.to_datetime(presc["datavenda"], errors="coerce")
    presc["nascimentopaciente"] = pd.to_datetime(presc["nascimentopaciente"], errors="coerce")

    # Nivel prescricao unica
    pu = presc.drop_duplicates(subset="idprescricao").copy()
    pu["convertido"] = pu["itemvendido"] == 1
    pu["mes"]        = pu["dataprescricao"].dt.to_period("M").astype(str)
    pu["dia_semana"] = pu["dataprescricao"].dt.day_name()
    pu["hora"]       = pu["dataprescricao"].dt.hour
    pu["data"]       = pu["dataprescricao"].dt.date

    REF = pd.Timestamp("2025-04-18")
    pu["idade"] = ((REF - pu["nascimentopaciente"]).dt.days / 365.25)

    def geracao(idade):
        if pd.isna(idade):  return "Desconhecido"
        if idade < 13:      return "Gen Alpha (0-12)"
        if idade < 29:      return "Gen Z (13-28)"
        if idade < 45:      return "Millennials (29-44)"
        if idade < 61:      return "Gen X (45-60)"
        if idade < 80:      return "Boomers (61-79)"
        return "Silent+ (80+)"

    pu["geracao"] = pu["idade"].apply(geracao)

    # Join com medicos
    pu = pu.merge(medicos[["idmedico","especialidade","estado"]], on="idmedico", how="left")

    return presc, pu, meds, medicos

presc_raw, pu_all, meds, medicos = load_data()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    logo_path = os.path.join(BASE, "logo_mevo_real.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=160)
    st.markdown("---")
    st.markdown(f"<h3 style='color:{ROXO}'>Filtros</h3>", unsafe_allow_html=True)

    meses_disp = sorted(pu_all["mes"].unique())
    meses_sel  = st.multiselect("Mês", meses_disp, default=meses_disp,
                                 help="Filtrar por período de prescrição")

    esps_disp = sorted(pu_all["especialidade"].dropna().unique())
    esps_sel  = st.multiselect("Especialidade", esps_disp, default=esps_disp)

    estados_disp = sorted(pu_all["estado"].dropna().unique())
    estados_sel  = st.multiselect("Estado", estados_disp, default=estados_disp)

    st.markdown("---")
    st.caption("Dados: Jan–Abr 2025  |  Saúde+ / Mevo")

# ── Filtro global ─────────────────────────────────────────────────────────────
mask = (
    pu_all["mes"].isin(meses_sel) &
    (pu_all["especialidade"].isin(esps_sel) | pu_all["especialidade"].isna()) &
    (pu_all["estado"].isin(estados_sel) | pu_all["estado"].isna())
)
pu = pu_all[mask].copy()

total_presc  = len(pu)
total_pac    = pu["idpaciente"].nunique() if "idpaciente" in pu.columns else pu_all["idpaciente"].nunique()
total_med    = pu["idmedico"].nunique()
total_vis    = pu["visualizadapaciente"].sum()
total_conv   = pu["convertido"].sum()
or_geral     = total_vis / total_presc * 100 if total_presc else 0
conv_geral   = total_conv / total_vis * 100 if total_vis else 0


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='background:{ROXO}; border-radius:12px; padding:22px 30px; margin-bottom:20px;
            display:flex; align-items:center; justify-content:space-between;'>
  <div>
    <div style='color:{ROSA_MED_C}; font-size:0.8rem; font-weight:600; letter-spacing:2px;'>
      SAÚDE+ ANALYTICS
    </div>
    <div style='color:white; font-size:1.6rem; font-weight:700; margin-top:4px;'>
      Dashboard de Prescrições Digitais
    </div>
    <div style='color:{ROSA_AC}; font-size:0.9rem; margin-top:4px;'>
      Janeiro – Abril 2025
    </div>
  </div>
  <div style='color:{ROSA_CLARO}; font-size:0.85rem; text-align:right;'>
    {len(meses_sel)} mes(es) selecionado(s)<br>
    {len(esps_sel)} especialidade(s)<br>
    {len(estados_sel)} estado(s)
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
kpis = [
    (f"{total_presc:,.0f}".replace(",","."), "Prescrições Emitidas", ROXO),
    (f"{total_pac:,.0f}".replace(",","."),   "Pacientes Únicos",     ROXO_MED),
    (f"{total_med:,.0f}".replace(",","."),   "Médicos Ativos",       "#ED8936"),
    (f"{or_geral:.1f}%",                     "Open Rate",            "#E53E3E" if or_geral < 50 else ROXO_MED),
    (f"{conv_geral:.1f}%",                   "Conversão s/ Visualiz.",ALERTA if conv_geral < 10 else ROXO),
    (f"{int(total_conv):,.0f}".replace(",","."), "Vendas Realizadas", "#38A169"),
]
cols = st.columns(6)
for col, (val, lbl, cor) in zip(cols, kpis):
    col.markdown(f"""
    <div class='metric-card' style='border-top-color:{cor};'>
      <div class='metric-value' style='color:{cor};'>{val}</div>
      <div class='metric-label'>{lbl}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📅 Volume & Sazonalidade",
    "👤 Perfil dos Pacientes",
    "🩺 Especialidades",
    "📬 Open Rate",
    "🛒 Conversão",
    "🏥 Médicos",
    "🗺️ Geografia",
    "🎯 Plano de Ação",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — VOLUME & SAZONALIDADE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.subheader("Volume & Sazonalidade")
    col1, col2 = st.columns([3, 1])

    with col1:
        # Volume diário
        vol_dia = pu.groupby("data")["idprescricao"].count().reset_index()
        vol_dia.columns = ["data", "prescricoes"]
        vol_dia["data"] = pd.to_datetime(vol_dia["data"])
        vol_dia["media7"] = vol_dia["prescricoes"].rolling(7, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=vol_dia["data"], y=vol_dia["prescricoes"],
            name="Diário", marker_color=ROSA_MED_C, opacity=0.7,
        ))
        fig.add_trace(go.Scatter(
            x=vol_dia["data"], y=vol_dia["media7"],
            name="Média 7d", line=dict(color=ROXO, width=2.5),
        ))
        fig.update_layout(
            title="Prescrições por Dia",
            xaxis_title="", yaxis_title="Prescrições",
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=1.02),
            font=dict(color=ESCURO),
            height=340,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Por dia da semana
        ordem_semana = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        nomes_pt     = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]
        semana = (pu.groupby("dia_semana")["idprescricao"]
                    .count()
                    .reindex(ordem_semana)
                    .reset_index())
        semana.columns = ["dia_en","presc"]
        semana["dia"] = nomes_pt
        fig2 = px.bar(semana, x="presc", y="dia", orientation="h",
                      color="presc", color_continuous_scale=[[0, ROSA_MED_C],[1, ROXO]],
                      title="Por Dia da Semana", labels={"presc":"Presc.","dia":""})
        fig2.update_layout(height=340, showlegend=False, coloraxis_showscale=False,
                           plot_bgcolor="white", paper_bgcolor="white",
                           font=dict(color=ESCURO))
        fig2.update_yaxes(autorange="reversed")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        # Por hora
        hora_df = pu.groupby("hora")["idprescricao"].count().reset_index()
        hora_df.columns = ["hora","presc"]
        fig3 = px.area(hora_df, x="hora", y="presc",
                       title="Distribuição por Hora do Dia",
                       labels={"hora":"Hora","presc":"Prescrições"},
                       color_discrete_sequence=[ROXO])
        fig3.update_traces(fill="tozeroy", fillcolor=ROSA_CLARO, line_color=ROXO)
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           height=280, font=dict(color=ESCURO))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Por mês
        mes_df = pu.groupby("mes")["idprescricao"].count().reset_index()
        mes_df.columns = ["mes","presc"]
        mes_df["variacao"] = mes_df["presc"].pct_change() * 100
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=mes_df["mes"], y=mes_df["presc"],
            marker_color=ROXO, name="Total",
        ))
        fig4.update_layout(
            title="Volume Mensal",
            plot_bgcolor="white", paper_bgcolor="white",
            height=280, font=dict(color=ESCURO),
            yaxis_title="Prescrições",
        )
        for _, row in mes_df.dropna(subset=["variacao"]).iterrows():
            cor_v = "#38A169" if row["variacao"] >= 0 else ALERTA
            fig4.add_annotation(x=row["mes"], y=row["presc"]+200,
                                text=f"{row['variacao']:+.0f}%",
                                showarrow=False, font=dict(color=cor_v, size=11))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown(f"""
    <div class='insight-box'>
    🔍 <b>Takeaway:</b> Pico semanal na <b>quinta-feira</b> e pico diário às <b>13h</b> — médico emite logo após a consulta matinal.
    SLA de notificação &lt;5 min nesse horário maximiza abertura.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PERFIL DOS PACIENTES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.subheader("Perfil dos Pacientes")

    geracao_order = ["Gen Alpha (0-12)","Gen Z (13-28)","Millennials (29-44)",
                     "Gen X (45-60)","Boomers (61-79)","Silent+ (80+)"]

    gen_df = (pu.groupby("geracao").agg(
        presc=("idprescricao","count"),
        or_=("visualizadapaciente","mean"),
        conv=("convertido","mean"),
    ).reindex(geracao_order).dropna().reset_index())
    gen_df["or_pct"]   = gen_df["or_"] * 100
    gen_df["conv_pct"] = gen_df["conv"] * 100

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(gen_df, x="geracao", y="presc",
                     color="presc", color_continuous_scale=[[0, ROSA_MED_C],[1, ROXO]],
                     title="Volume de Prescrições por Geração",
                     labels={"geracao":"","presc":"Prescrições"})
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          coloraxis_showscale=False, height=340, font=dict(color=ESCURO))
        fig.update_xaxes(tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Open Rate (%)", x=gen_df["geracao"], y=gen_df["or_pct"],
                               marker_color=ROXO_MED))
        fig2.add_trace(go.Bar(name="Conversão (%)", x=gen_df["geracao"], y=gen_df["conv_pct"],
                               marker_color=ROSA_AC))
        fig2.update_layout(barmode="group", title="OR e Conversão por Geração",
                           plot_bgcolor="white", paper_bgcolor="white",
                           height=340, font=dict(color=ESCURO),
                           legend=dict(orientation="h", y=1.02))
        fig2.update_xaxes(tickangle=-20)
        st.plotly_chart(fig2, use_container_width=True)

    # Scatter OR vs conversão por geração
    fig3 = px.scatter(gen_df, x="or_pct", y="conv_pct", size="presc",
                      color="geracao", text="geracao",
                      title="Open Rate vs. Conversão por Geração (tamanho = volume)",
                      labels={"or_pct":"Open Rate (%)","conv_pct":"Conversão (%)","geracao":"Geração"},
                      color_discrete_sequence=PALETTE)
    fig3.update_traces(textposition="top center")
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                       height=350, font=dict(color=ESCURO), showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(f"""
    <div class='insight-box'>
    🔍 <b>Millennials + Gen X</b> = 57% do volume com maior conversão (10-13%).
    <b>Gen Z</b>: OR 57% — o mais engajado, mas conversão 7% — não finaliza a compra online.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ESPECIALIDADES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.subheader("Especialidades Médicas")

    esp_df = (pu.groupby("especialidade").agg(
        presc=("idprescricao","count"),
        or_=("visualizadapaciente","mean"),
        conv=("convertido","mean"),
        medicos=("idmedico","nunique"),
    ).reset_index())
    esp_df["or_pct"]   = esp_df["or_"] * 100
    esp_df["conv_pct"] = esp_df["conv"] * 100
    esp_df = esp_df.sort_values("presc", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        top15 = esp_df.head(15)
        fig = px.bar(top15, x="presc", y="especialidade", orientation="h",
                     color="presc", color_continuous_scale=[[0,ROSA_MED_C],[1,ROXO]],
                     title="Top 15 Especialidades por Volume",
                     labels={"presc":"Prescrições","especialidade":""})
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          coloraxis_showscale=False, height=460,
                          yaxis=dict(autorange="reversed"), font=dict(color=ESCURO))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        esp_plot = esp_df[esp_df["presc"] >= 300].copy()
        fig2 = px.scatter(esp_plot, x="or_pct", y="conv_pct", size="presc",
                          color="conv_pct",
                          color_continuous_scale=[[0,ROSA_MED_C],[0.5,ROXO_MED],[1,ROXO]],
                          hover_name="especialidade",
                          text="especialidade",
                          title="OR vs. Conversão por Especialidade",
                          labels={"or_pct":"Open Rate (%)","conv_pct":"Conversão (%)","presc":"Volume"})
        fig2.update_traces(textposition="top center", textfont_size=9)
        fig2.add_hline(y=conv_geral, line_dash="dot", line_color=CINZA,
                       annotation_text=f"Média {conv_geral:.1f}%")
        fig2.add_vline(x=or_geral, line_dash="dot", line_color=CINZA,
                       annotation_text=f"Média OR {or_geral:.1f}%")
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           height=460, coloraxis_showscale=False, font=dict(color=ESCURO))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"""
    <div class='insight-box'>
    🔍 <b>Psiquiatria:</b> conversão 23,9% (2,3× a média) — 85% são controlados, canal digital obrigatório.<br>
    🔍 <b>Cirurgia Geral:</b> OR 71,8% (topo) mas conv. 8,9% — paciente abre mas compra no hospital.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — OPEN RATE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.subheader("Open Rate")

    col1, col2 = st.columns([2, 1])
    with col1:
        # OR por mês
        or_mes = (pu.groupby("mes")["visualizadapaciente"]
                    .mean().reset_index())
        or_mes.columns = ["mes","or"]
        or_mes["or_pct"] = or_mes["or"] * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=or_mes["mes"], y=or_mes["or_pct"],
            mode="lines+markers+text",
            text=[f"{v:.1f}%" for v in or_mes["or_pct"]],
            textposition="top center",
            line=dict(color=ROXO, width=3),
            marker=dict(size=10, color=ROXO),
            name="Open Rate",
        ))
        fig.add_hline(y=50, line_dash="dot", line_color=CINZA,
                      annotation_text="Meta 50%")
        fig.update_layout(
            title="Evolução do Open Rate Mensal",
            yaxis=dict(title="Open Rate (%)", range=[40, 65]),
            plot_bgcolor="white", paper_bgcolor="white",
            height=320, font=dict(color=ESCURO),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Funil
        n_total  = total_presc
        n_vis    = int(total_vis)
        n_conv   = int(total_conv)
        fig2 = go.Figure(go.Funnel(
            y=["Emitidas","Visualizadas","Convertidas"],
            x=[n_total, n_vis, n_conv],
            textinfo="value+percent initial",
            marker=dict(color=[ROXO_MED, ROXO, ROSA_AC]),
        ))
        fig2.update_layout(
            title="Funil de Engajamento",
            plot_bgcolor="white", paper_bgcolor="white",
            height=320, font=dict(color=ESCURO),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # OR por especialidade (top 10)
    or_esp = (pu.groupby("especialidade")
                .agg(or_=("visualizadapaciente","mean"), presc=("idprescricao","count"))
                .query("presc >= 300")
                .sort_values("or_", ascending=False)
                .head(10)
                .reset_index())
    or_esp["or_pct"] = or_esp["or_"] * 100

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=or_esp["or_pct"], y=or_esp["especialidade"],
        orientation="h",
        marker=dict(
            color=or_esp["or_pct"],
            colorscale=[[0, ROSA_MED_C],[1, ROXO]],
        ),
        text=[f"{v:.1f}%" for v in or_esp["or_pct"]],
        textposition="outside",
    ))
    fig3.add_vline(x=or_geral, line_dash="dot", line_color=CINZA,
                   annotation_text=f"Média {or_geral:.1f}%")
    fig3.update_layout(
        title="Open Rate por Especialidade (top 10, min 300 presc.)",
        xaxis_title="Open Rate (%)", yaxis=dict(autorange="reversed"),
        plot_bgcolor="white", paper_bgcolor="white",
        height=350, font=dict(color=ESCURO), showlegend=False,
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(f"""
    <div class='alert-box'>
    ⚠️ <b>35.135 receitas nunca acessadas.</b> Cada 1 p.p. de melhoria no OR = +709 pacientes alcançados.
    OR estável em ~50% há 4 meses — sinal de estagnação sem intervenção ativa.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — CONVERSÃO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.subheader("Conversão por Canal")

    col1, col2 = st.columns(2)
    with col1:
        # Canal de venda
        if "canalvenda" in pu.columns:
            canal_df = (pu[pu["convertido"]].groupby("canalvenda")["idprescricao"]
                          .count().reset_index())
            canal_df.columns = ["canal","vendas"]
            canal_df["pct"] = canal_df["vendas"] / canal_df["vendas"].sum() * 100
            canal_df = canal_df.sort_values("vendas", ascending=False)
        else:
            canal_df = pd.DataFrame({
                "canal": ["Farmacia Fisica","Marketplace","Sem Rastreio"],
                "vendas": [3879, 722, 970],
                "pct": [84.3, 15.7, 0],
            })

        fig = px.bar(canal_df, x="canal", y="vendas",
                     color="vendas", color_continuous_scale=[[0,ROSA_MED_C],[1,ROXO]],
                     text=[f"{v:.0f}\n({p:.1f}%)" for v, p in zip(canal_df["vendas"], canal_df["pct"])],
                     title="Vendas por Canal",
                     labels={"canal":"Canal","vendas":"Vendas"})
        fig.update_traces(textposition="outside")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          coloraxis_showscale=False, height=340, font=dict(color=ESCURO))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Conversão por mês
        conv_mes = (pu[pu["visualizadapaciente"]].groupby("mes")["convertido"]
                      .mean().reset_index())
        conv_mes.columns = ["mes","conv"]
        conv_mes["conv_pct"] = conv_mes["conv"] * 100

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=conv_mes["mes"], y=conv_mes["conv_pct"],
            mode="lines+markers+text",
            text=[f"{v:.1f}%" for v in conv_mes["conv_pct"]],
            textposition="top center",
            line=dict(color=ROXO_MED, width=3),
            marker=dict(size=10, color=ROXO_MED),
        ))
        fig2.add_hline(y=13, line_dash="dot", line_color="#38A169",
                       annotation_text="Meta 13%")
        fig2.update_layout(
            title="Conversão Mensal (s/ visualizadas)",
            yaxis=dict(title="Conversão (%)"),
            plot_bgcolor="white", paper_bgcolor="white",
            height=340, font=dict(color=ESCURO),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Waterfall Conversão → Meta
    st.markdown("#### Jornada de Conversão: Baseline → Meta")
    waterfall_data = {
        "label": ["Baseline","Push <5min","Marketplace","VIP Program","Segmentação","Meta"],
        "valor": [10.2, 0.8, 1.0, 0.6, 0.4, 13.0],
        "tipo":  ["base","add","add","add","add","total"],
    }
    wf = pd.DataFrame(waterfall_data)

    running = 0.0; bottoms = []; colors = []
    COR_ADD = ROSA_MED_C
    for _, row in wf.iterrows():
        if row["tipo"] == "base":
            bottoms.append(0); colors.append(ROXO_MED); running = row["valor"]
        elif row["tipo"] == "add":
            bottoms.append(running); colors.append(COR_ADD); running += row["valor"]
        else:
            bottoms.append(0); colors.append(ROXO)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=wf["label"], y=wf["valor"],
        base=bottoms,
        marker_color=colors,
        text=[f"+{v:.1f}pp" if t=="add" else f"{v:.1f}%" for v,t in zip(wf["valor"],wf["tipo"])],
        textposition="outside",
    ))
    fig3.add_hline(y=13, line_dash="dot", line_color="#38A169",
                   annotation_text="Meta: 13%")
    fig3.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(title="Conversão (%)", range=[0, 16]),
        height=340, font=dict(color=ESCURO), showlegend=False,
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(f"""
    <div class='insight-box'>
    🔍 <b>89,8%</b> das visualizações não convertem. Marketplace tem potencial de 5× via redução de fricção.
    <b>970 compras</b> sem abertura digital — QR Code fecha esse gap.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — MÉDICOS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.subheader("Segmentação de Médicos")

    med_vol = (pu.groupby("idmedico")["idprescricao"].count().reset_index())
    med_vol.columns = ["idmedico","presc"]

    def segmento(p):
        if p >= 50: return "VIP (50+)"
        if p >= 10: return "High (10-49)"
        if p >= 3:  return "Mid (3-9)"
        return "Low (1-2)"

    med_vol["segmento"] = med_vol["presc"].apply(segmento)
    seg_order = ["VIP (50+)","High (10-49)","Mid (3-9)","Low (1-2)"]

    seg_stats = (pu.merge(med_vol[["idmedico","segmento"]], on="idmedico")
                   .groupby("segmento").agg(
                       medicos=("idmedico","nunique"),
                       presc=("idprescricao","count"),
                       or_=("visualizadapaciente","mean"),
                       conv=("convertido","mean"),
                   ).reindex(seg_order).reset_index())

    seg_stats["or_pct"]   = seg_stats["or_"] * 100
    seg_stats["conv_pct"] = seg_stats["conv"] * 100

    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.bar(seg_stats, x="segmento", y="presc",
                     color="segmento", color_discrete_sequence=PALETTE,
                     title="Volume por Segmento",
                     text="presc", labels={"segmento":"","presc":"Prescrições"})
        fig.update_traces(textposition="outside")
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                          showlegend=False,height=320,font=dict(color=ESCURO))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(seg_stats, x="segmento", y="or_pct",
                      color="segmento", color_discrete_sequence=PALETTE,
                      title="Open Rate por Segmento",
                      text=[f"{v:.1f}%" for v in seg_stats["or_pct"]],
                      labels={"segmento":"","or_pct":"OR (%)"})
        fig2.add_hline(y=or_geral, line_dash="dot", line_color=CINZA)
        fig2.update_traces(textposition="outside")
        fig2.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                           showlegend=False,height=320,font=dict(color=ESCURO))
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        fig3 = px.bar(seg_stats, x="segmento", y="conv_pct",
                      color="segmento", color_discrete_sequence=PALETTE,
                      title="Conversão por Segmento",
                      text=[f"{v:.1f}%" for v in seg_stats["conv_pct"]],
                      labels={"segmento":"","conv_pct":"Conv. (%)"})
        fig3.add_hline(y=conv_geral, line_dash="dot", line_color=CINZA)
        fig3.update_traces(textposition="outside")
        fig3.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                           showlegend=False,height=320,font=dict(color=ESCURO))
        st.plotly_chart(fig3, use_container_width=True)

    # Retenção coorte Janeiro
    st.markdown("#### Retenção de Médicos — Coorte Janeiro 2025")
    pu_med = pu.groupby(["idmedico","mes"])["idprescricao"].count().reset_index()
    meses_str = sorted(pu["mes"].unique())
    jan_set   = set(pu_med[pu_med["mes"]==meses_str[0]]["idmedico"]) if meses_str else set()

    ret_data = []
    for m in meses_str:
        ativos_m  = set(pu_med[pu_med["mes"]==m]["idmedico"])
        retidos_m = len(jan_set & ativos_m) if jan_set else 0
        ret_pct   = retidos_m / len(jan_set) * 100 if jan_set else 0
        ret_data.append({"mes":m, "retidos":retidos_m, "ativos":len(ativos_m),
                         "novos":max(len(ativos_m)-retidos_m,0), "ret_pct":ret_pct})
    ret_df = pd.DataFrame(ret_data)

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(name="Retidos (base Jan)", x=ret_df["mes"],
                           y=ret_df["retidos"], marker_color=ROXO))
    fig4.add_trace(go.Bar(name="Novos no mês", x=ret_df["mes"],
                           y=ret_df["novos"], marker_color=ROSA_MED_C))
    for _, row in ret_df.iterrows():
        if row["ret_pct"] < 100:
            fig4.add_annotation(x=row["mes"], y=row["ativos"]+80,
                                text=f"{row['ret_pct']:.0f}% ret.",
                                showarrow=False, font=dict(color=CINZA, size=11))
    fig4.update_layout(barmode="stack", plot_bgcolor="white", paper_bgcolor="white",
                       height=320, font=dict(color=ESCURO),
                       legend=dict(orientation="h", y=1.02))
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown(f"""
    <div class='alert-box'>
    ⚠️ <b>57% dos médicos de Janeiro não prescreveram em Abril.</b>
    1 médico VIP perdido = 83 prescrições/mês a menos. Retenção VIP é prioridade crítica.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — GEOGRAFIA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.subheader("Inteligência Geográfica")

    geo_df = (pu.groupby("estado").agg(
        presc=("idprescricao","count"),
        or_=("visualizadapaciente","mean"),
        conv=("convertido","mean"),
    ).reset_index())
    geo_df["or_pct"]   = geo_df["or_"] * 100
    geo_df["conv_pct"] = geo_df["conv"] * 100
    geo_df = geo_df.sort_values("presc", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(geo_df, x="or_pct", y="conv_pct", size="presc",
                         text="estado", color="conv_pct",
                         color_continuous_scale=[[0,ALERTA],[0.5,ROSA_AC],[1,ROXO]],
                         title="OR vs. Conversão por Estado (tamanho = volume)",
                         labels={"or_pct":"Open Rate (%)","conv_pct":"Conversão (%)","presc":"Volume"})
        fig.update_traces(textposition="top center")
        fig.add_hline(y=conv_geral, line_dash="dot", line_color=CINZA,
                      annotation_text=f"Média {conv_geral:.1f}%")
        fig.add_vline(x=or_geral, line_dash="dot", line_color=CINZA)
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          coloraxis_showscale=False, height=400, font=dict(color=ESCURO))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(geo_df.head(10), x="conv_pct", y="estado", orientation="h",
                      color="conv_pct",
                      color_continuous_scale=[[0,ALERTA],[0.5,ROSA_AC],[1,ROXO]],
                      title="Top 10 Estados por Conversão",
                      text=[f"{v:.1f}%" for v in geo_df.head(10)["conv_pct"]],
                      labels={"conv_pct":"Conversão (%)","estado":""})
        fig2.add_vline(x=conv_geral, line_dash="dot", line_color=CINZA)
        fig2.update_traces(textposition="outside")
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False, height=400,
                           yaxis=dict(autorange="reversed"), font=dict(color=ESCURO))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"""
    <div class='insight-box'>
    🔍 <b>SC:</b> OR 61,5% + conv 12,7% — melhor combinação. Replicar modelo para outros estados.<br>
    🔍 <b>RS:</b> conversão 14,9% (topo nacional). Investigar o que gera mais compra.
    </div>
    <div class='alert-box'>
    ⚠️ <b>RJ:</b> OR 54,7% mas conversão 3,8% — anomalia crítica. Investigar estoque, preço local e UX.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — PLANO DE AÇÃO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.subheader("Plano de Ação & PDCA")

    # Cards de ação
    acoes = [
        (ALERTA,   "Inativo Digital (48%)",
         "Push/SMS < 5 min pós-emissão",
         "OR: 50,4% → 60%",
         "Alta", "90d"),
        (ROXO,     "Médicos VIP (92)",
         "Programa dedicado + NPS mensal",
         "Churn VIP → 0%",
         "Alta", "30d"),
        (ROXO_MED, "Marketplace (16% mix)",
         "Desconto 1ª compra digital",
         "Mix → 20%",
         "Alta", "60d"),
        ("#ED8936", "Engajado s/ Conv. (45%)",
         "Lembrete 2h e 24h pós-abertura",
         "Conv → 13%",
         "Média", "90d"),
        ("#38A169", "Psiquiatria (conv 24%)",
         "Parceria distribuidores controlados",
         "Conv → 30%",
         "Média", "120d"),
        (CINZA,    "RJ — Anomalia",
         "Diagnóstico: estoque + UX + preço",
         "Conv → 8% (média)",
         "Alta", "45d"),
        (ROSA_AC,  "Crônicos (renovação)",
         "Renovação automática de receita",
         "LTV +40%",
         "Baixa", "180d"),
    ]

    col1, col2 = st.columns(2)
    for i, (cor, seg, acao, meta, prio, prazo) in enumerate(acoes):
        c = col1 if i % 2 == 0 else col2
        c.markdown(f"""
        <div style='background:white; border-radius:10px; padding:14px 16px; margin:6px 0;
                    border-left:5px solid {cor}; box-shadow:0 1px 4px rgba(0,0,0,0.07);'>
          <div style='font-weight:700; color:{cor}; font-size:0.95rem;'>{seg}</div>
          <div style='color:{ESCURO}; margin:5px 0; font-size:0.88rem;'>📌 {acao}</div>
          <div style='display:flex; gap:12px; margin-top:6px;'>
            <span style='background:{ROSA_CLARO}; border-radius:4px; padding:2px 8px;
                         font-size:0.78rem; color:{ROXO}; font-weight:600;'>Meta: {meta}</span>
            <span style='background:#F7FAFC; border-radius:4px; padding:2px 8px;
                         font-size:0.78rem; color:{CINZA};'>⏱ {prazo}</span>
            <span style='background:{"#FFF5F5" if prio=="Alta" else "#F0FFF4"}; border-radius:4px;
                         padding:2px 8px; font-size:0.78rem;
                         color:{"#E53E3E" if prio=="Alta" else "#38A169"};
                         font-weight:600;'>Prio: {prio}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Waterfall de Conversão: Baseline → Meta")

    wf_labels = ["Baseline","Push <5min","Marketplace","VIP Program","Segmentação","Meta"]
    wf_deltas = [10.2, 0.8, 1.0, 0.6, 0.4, 0]
    wf_measure = ["absolute","relative","relative","relative","relative","total"]

    fig_wf = go.Figure(go.Waterfall(
        name="Conversão",
        orientation="v",
        measure=wf_measure,
        x=wf_labels,
        y=wf_deltas,
        text=[f"{v:.1f}%" if m in ("absolute","total") else f"+{v:.1f}pp"
              for v, m in zip(wf_deltas, wf_measure)],
        textposition="outside",
        connector=dict(line=dict(color="#CBD5E0", dash="dot")),
        increasing=dict(marker=dict(color=ROSA_MED_C)),
        decreasing=dict(marker=dict(color=ALERTA)),
        totals=dict(marker=dict(color=ROXO)),
    ))
    fig_wf.add_hline(y=13, line_dash="dot", line_color="#38A169",
                     annotation_text="Meta: 13%")
    fig_wf.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(title="Taxa de Conversão (%)", range=[0, 16]),
        height=380, font=dict(color=ESCURO), showlegend=False,
    )
    st.plotly_chart(fig_wf, use_container_width=True)

    # PDCA resumo
    st.markdown("#### Ciclo PDCA")
    pdca_cols = st.columns(4)
    pdca_items = [
        ("P", "PLAN", ROXO,
         ["OR: 50,4% → 60%","Conv: 10,2% → 13%","Churn médicos: <30%","Marketplace: 16% → 20%"]),
        ("D", "DO", ROXO_MED,
         ["Push <5 min após emissão","Programa Médicos VIP","Desconto marketplace","QR Code farmácia física"]),
        ("C", "CHECK", "#38A169",
         ["OR por especialidade","Conv. digital vs físico","Churn semanal de médicos","SLA de notificação"]),
        ("A", "ACT", ALERTA,
         ["OR <55%: revisar copy","Conv <11%: revisar UX","Churn >35%: entrevistas","Reunião quinzenal"]),
    ]
    for col, (letra, fase, cor, items) in zip(pdca_cols, pdca_items):
        items_html = "".join([f"<li style='margin:4px 0;'>{it}</li>" for it in items])
        col.markdown(f"""
        <div style='background:{ROSA_CLARO}; border-radius:10px; padding:16px;
                    border-top:5px solid {cor}; height:100%;'>
          <div style='background:{cor}; color:white; border-radius:50%; width:36px; height:36px;
                      display:flex; align-items:center; justify-content:center;
                      font-size:1.2rem; font-weight:700; margin-bottom:8px;'>{letra}</div>
          <div style='font-weight:700; color:{cor}; margin-bottom:8px;'>{fase}</div>
          <ul style='color:{ESCURO}; font-size:0.82rem; padding-left:16px; margin:0;'>
            {items_html}
          </ul>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align:center; color:{CINZA}; font-size:0.8rem; padding:16px;
            border-top:1px solid #E2E8F0;'>
  Saúde+ Analytics Dashboard · Jan–Abr 2025 · Desenvolvido com Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
