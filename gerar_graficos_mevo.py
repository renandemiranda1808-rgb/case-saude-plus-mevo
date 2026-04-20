"""
Gerador de graficos — Paleta MEVO
Um grafico = um takeaway anotado diretamente no visual.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings('ignore')

BASE = __file__.replace('gerar_graficos_mevo.py', '')

# ── Paleta MEVO ──────────────────────────────────────────────────────────────
VERDE      = '#22C35E'   # Primary
VERDE_ESC  = '#179848'   # Dark green
AZUL       = '#3182CE'   # Blue accent
ESCURO     = '#1A202C'   # Dark navy (text / headers)
CINZA      = '#718096'   # Neutral text
CINZA_CLARO= '#EDF2F7'   # Light background
BRANCO     = '#FFFFFF'
ALERTA     = '#E53E3E'   # Red
TEAL       = '#319795'   # Teal accent

plt.rcParams.update({
    'figure.facecolor': BRANCO,
    'axes.facecolor':   CINZA_CLARO,
    'axes.edgecolor':   CINZA,
    'axes.labelcolor':  ESCURO,
    'text.color':       ESCURO,
    'xtick.color':      CINZA,
    'ytick.color':      CINZA,
    'grid.color':       '#CBD5E0',
    'grid.alpha':       0.5,
    'font.family':      'DejaVu Sans',
    'figure.dpi':       150,
    'axes.spines.top':  False,
    'axes.spines.right':False,
})

def callout(ax, text, xy, xytext, color=VERDE):
    ax.annotate(text, xy=xy, xytext=xytext,
        fontsize=10, fontweight='bold', color=BRANCO,
        ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.4', fc=color, ec='none', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=color, lw=1.8))

# ── Carregar dados ────────────────────────────────────────────────────────────
presc   = pd.read_csv(BASE + 'prescricaomedicamento.csv')
meds    = pd.read_csv(BASE + 'medicamentos.csv')
medicos = pd.read_csv(BASE + 'medicos.csv')

presc['dataprescricao']     = pd.to_datetime(presc['dataprescricao'])
presc['datavenda']          = pd.to_datetime(presc['datavenda'], errors='coerce')
presc['nascimentopaciente'] = pd.to_datetime(presc['nascimentopaciente'], errors='coerce')
presc_unica = presc.drop_duplicates(subset='idprescricao').copy()
presc_unica['convertido'] = presc_unica['itemvendido'] == 1
presc_unica['mes']         = presc_unica['dataprescricao'].dt.to_period('M')
presc_unica['hora']        = presc_unica['dataprescricao'].dt.hour
presc_unica['dia_semana']  = presc_unica['dataprescricao'].dt.day_name()

REF = pd.Timestamp('2025-04-18')
presc_unica['idade'] = ((REF - presc_unica['nascimentopaciente']).dt.days / 365.25)

def geracao(idade):
    if pd.isna(idade) or idade < 0:   return None
    if idade <= 12:  return 'Gen Alpha\n(0-12)'
    if idade <= 28:  return 'Gen Z\n(13-28)'
    if idade <= 44:  return 'Millennials\n(29-44)'
    if idade <= 60:  return 'Gen X\n(45-60)'
    if idade <= 79:  return 'Boomers\n(61-79)'
    return 'Silent+\n(80+)'

presc_unica['geracao'] = presc_unica['idade'].apply(geracao)

presc_full = presc_unica.merge(medicos[['idmedico','especialidade']], on='idmedico', how='left')
presc_full = presc_full.merge(meds[['idmedicamento','nome','controleespecial','mip']], on='idmedicamento', how='left')


# ═══════════════════════════════════════════════════════════════════
# FIG 1 — Volume diário
# Takeaway: crescimento +22%, pico quinta 13h
# ═══════════════════════════════════════════════════════════════════
daily = (presc_unica.groupby(presc_unica['dataprescricao'].dt.date)['idprescricao']
         .count().reset_index(name='presc'))
daily['data'] = pd.to_datetime(daily['dataprescricao'])
daily['mm7']  = daily['presc'].rolling(7, center=True).mean()

fig, ax = plt.subplots(figsize=(12, 4.5))
ax.bar(daily['data'], daily['presc'], color=VERDE, alpha=0.35, width=0.85, label='Diario')
ax.plot(daily['data'], daily['mm7'], color=VERDE_ESC, lw=2.5, label='Media movel 7d')
ax.set_facecolor(BRANCO)
ax.set_ylabel('Prescricoes / dia', color=CINZA, fontsize=11)
ax.tick_params(axis='x', rotation=0)
ax.legend(fontsize=10)

# Anotacao de pico
pico = daily.loc[daily['presc'].idxmax()]
callout(ax, f"PICO\n{int(pico.presc):,} presc\n{pico.data.strftime('%d/%m')}",
        xy=(pico.data, pico.presc),
        xytext=(pico.data - pd.Timedelta(days=12), pico.presc * 0.88))

# Anotacao de crescimento
ax.annotate('+22%\nJan→Mar', xy=(pd.Timestamp('2025-03-15'), 900),
    fontsize=11, fontweight='bold', color=VERDE,
    bbox=dict(boxstyle='round,pad=0.35', fc=CINZA_CLARO, ec=VERDE, lw=1.5))

# Separadores de mes
for m in pd.date_range('2025-02-01','2025-04-01', freq='MS'):
    ax.axvline(m, color=CINZA, lw=0.8, ls='--', alpha=0.5)
    ax.text(m, ax.get_ylim()[1]*0.96, m.strftime('%b'), fontsize=9, color=CINZA, ha='left')

ax.set_title('Crescimento consistente — pico de 1.271 prescricoes em 15/Abr',
             fontsize=12, fontweight='bold', color=ESCURO, pad=10)
plt.tight_layout()
plt.savefig(BASE + 'fig_mevo_volume.png', bbox_inches='tight', dpi=150)
plt.close()
print('fig_mevo_volume.png')


# ═══════════════════════════════════════════════════════════════════
# FIG 2 — Perfil por Geração (barras horizontais)
# Takeaway: Millennials + Gen X = 57% e lideram conversao
# ═══════════════════════════════════════════════════════════════════
ordem_ger = ['Silent+\n(80+)', 'Boomers\n(61-79)', 'Gen X\n(45-60)',
             'Millennials\n(29-44)', 'Gen Z\n(13-28)', 'Gen Alpha\n(0-12)']

g_ger = presc_unica[presc_unica['geracao'].notna()].groupby('geracao').agg(
    presc=('idprescricao','count'),
    or_=('visualizadapaciente','mean')
).reset_index()
vis_g = presc_unica[presc_unica['visualizadapaciente'] & presc_unica['geracao'].notna()]
conv_g = vis_g.groupby('geracao')['convertido'].mean().reset_index()
conv_g.columns = ['geracao','conv_vis']
g_ger = g_ger.merge(conv_g, on='geracao')
g_ger['geracao_ord'] = pd.Categorical(g_ger['geracao'], categories=ordem_ger, ordered=True)
g_ger = g_ger.sort_values('geracao_ord')

fig, axes = plt.subplots(1, 3, figsize=(14, 5.5))
fig.patch.set_facecolor(BRANCO)

cores_ger = [CINZA if g not in ['Millennials\n(29-44)','Gen X\n(45-60)'] else VERDE
             for g in g_ger['geracao']]

# Volume
ax1 = axes[0]
ax1.set_facecolor(BRANCO)
bars = ax1.barh(g_ger['geracao'], g_ger['presc'], color=cores_ger, height=0.6)
ax1.set_xlabel('Prescricoes', fontsize=10)
ax1.set_title('Volume', fontweight='bold', fontsize=11, color=ESCURO)
for bar, v in zip(bars, g_ger['presc']):
    pct = v / presc_unica['geracao'].notna().sum() * 100
    ax1.text(v + 200, bar.get_y() + bar.get_height()/2,
             f'{v:,}  ({pct:.0f}%)', va='center', fontsize=9)
ax1.set_xlim(0, g_ger['presc'].max() * 1.35)
ax1.spines['top'].set_visible(False); ax1.spines['right'].set_visible(False)

# Open Rate
ax2 = axes[1]
ax2.set_facecolor(BRANCO)
bars2 = ax2.barh(g_ger['geracao'], g_ger['or_']*100, color=cores_ger, height=0.6)
ax2.axvline(50.4, color=ALERTA, lw=1.5, ls='--', label='Media 50,4%')
ax2.set_xlabel('Open Rate (%)', fontsize=10)
ax2.set_title('Open Rate', fontweight='bold', fontsize=11, color=ESCURO)
ax2.set_xlim(0, 75); ax2.legend(fontsize=8)
for bar, v in zip(bars2, g_ger['or_']):
    ax2.text(v*100 + 0.5, bar.get_y() + bar.get_height()/2,
             f'{v*100:.1f}%', va='center', fontsize=9)
ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)

# Conversao
ax3 = axes[2]
ax3.set_facecolor(BRANCO)
bars3 = ax3.barh(g_ger['geracao'], g_ger['conv_vis']*100, color=cores_ger, height=0.6)
ax3.axvline(10.2, color=ALERTA, lw=1.5, ls='--', label='Media 10,2%')
ax3.set_xlabel('Conversao s/ Visualizadas (%)', fontsize=10)
ax3.set_title('Conversao', fontweight='bold', fontsize=11, color=ESCURO)
ax3.set_xlim(0, 18); ax3.legend(fontsize=8)
for bar, v in zip(bars3, g_ger['conv_vis']):
    ax3.text(v*100 + 0.1, bar.get_y() + bar.get_height()/2,
             f'{v*100:.1f}%', va='center', fontsize=9)
ax3.spines['top'].set_visible(False); ax3.spines['right'].set_visible(False)

# Label de destaque
for ax in axes:
    for i, g in enumerate(g_ger['geracao']):
        if g in ['Millennials\n(29-44)', 'Gen X\n(45-60)']:
            ax.get_yticklabels()[i].set_color(VERDE_ESC)
            ax.get_yticklabels()[i].set_fontweight('bold')

fig.suptitle('Millennials e Gen X: 57% do volume — maior conversao da plataforma',
             fontsize=12, fontweight='bold', color=ESCURO)
plt.tight_layout()
plt.savefig(BASE + 'fig_mevo_geracoes.png', bbox_inches='tight', dpi=150)
plt.close()
print('fig_mevo_geracoes.png')


# ═══════════════════════════════════════════════════════════════════
# FIG 3 — Open Rate (funil visual + por mes)
# Takeaway: 35.135 receitas nunca acessadas
# ═══════════════════════════════════════════════════════════════════
or_mes = presc_unica.groupby('mes').agg(
    total=('idprescricao','count'),
    vis=('visualizadapaciente','sum')
).reset_index()
or_mes['or'] = or_mes['vis'] / or_mes['total']
or_mes['mes_str'] = or_mes['mes'].astype(str).str[-2:].map({'01':'Jan','02':'Fev','03':'Mar','04':'Abr'})

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
fig.patch.set_facecolor(BRANCO)

ax1 = axes[0]
ax1.set_facecolor(BRANCO)
etapas = ['Emitidas', 'Visualizadas', 'Nao Abertas']
vals   = [70907, 35772, 35135]
cores  = [VERDE, AZUL, ALERTA]
bars = ax1.bar(etapas, vals, color=cores, width=0.55)
ax1.set_ylabel('Prescricoes', fontsize=10)
ax1.set_title('35.135 receitas nunca chegam\nao paciente', fontweight='bold', color=ESCURO)
for bar, v in zip(bars, vals):
    pct = v/70907*100
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+300,
             f'{v:,}\n({pct:.0f}%)', ha='center', fontsize=10, fontweight='bold', color=ESCURO)
ax1.set_ylim(0, 85000)
ax1.spines['top'].set_visible(False); ax1.spines['right'].set_visible(False)

callout(ax1, 'OPORTUNIDADE\n35.135 nao abertas',
        xy=(2, 35135), xytext=(1.6, 55000), color=ALERTA)

ax2 = axes[1]
ax2.set_facecolor(BRANCO)
cols = [VERDE if v >= 0.504 else AZUL for v in or_mes['or']]
bars2 = ax2.bar(or_mes['mes_str'], or_mes['or']*100, color=cols, width=0.5)
ax2.axhline(50.4, color=CINZA, lw=1.5, ls='--', label='Media 50,4%')
ax2.set_ylim(0, 70); ax2.legend(fontsize=9)
ax2.set_ylabel('Open Rate (%)', fontsize=10)
ax2.set_title('Open Rate estavel entre 47-55%\npor mes', fontweight='bold', color=ESCURO)
for bar, v in zip(bars2, or_mes['or']):
    ax2.text(bar.get_x()+bar.get_width()/2, v*100+0.5,
             f'{v*100:.1f}%', ha='center', fontsize=11, fontweight='bold', color=ESCURO)
ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(BASE + 'fig_mevo_openrate.png', bbox_inches='tight', dpi=150)
plt.close()
print('fig_mevo_openrate.png')


# ═══════════════════════════════════════════════════════════════════
# FIG 4 — Funil de Conversao por Canal
# Takeaway: digital potencial enorme, fisico ainda domina
# ═══════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
fig.patch.set_facecolor(BRANCO)

ax1 = axes[0]
ax1.set_facecolor(BRANCO)
etapas = ['Emitidas\n(100%)', 'Visualizadas\n(50,4%)', 'Convertidas\n(5,1%)']
vals   = [70907, 35772, 3631]
cores  = [VERDE, AZUL, VERDE_ESC]
bars = ax1.barh(etapas, vals, color=cores, height=0.5)
for bar, v in zip(bars, vals):
    pct = v/70907*100
    ax1.text(v+500, bar.get_y()+bar.get_height()/2,
             f'{v:,}  ({pct:.1f}%)', va='center', fontsize=10, fontweight='bold')
ax1.set_xlim(0, 88000)
ax1.invert_yaxis()
ax1.set_title('Funil: 89,8% das visualizacoes\nnao convertem — maior gap', fontweight='bold', color=ESCURO)
callout(ax1, '89,8% nao\nconvertem', xy=(3631, 1.0), xytext=(25000, 1.2), color=ALERTA)
ax1.spines['top'].set_visible(False); ax1.spines['right'].set_visible(False)

ax2 = axes[1]
ax2.set_facecolor(BRANCO)
canais = ['Farmacia\nFisica', 'Marketplace', 'Sem\nRastreio']
vals2  = [2909, 722, 970]
cores2 = [AZUL, VERDE, CINZA]
bars2  = ax2.bar(canais, vals2, color=cores2, width=0.5)
ax2.set_title('Marketplace: 16% das vendas\nmas potencial de escala digital', fontweight='bold', color=ESCURO)
ax2.set_ylabel('Vendas', fontsize=10)
for bar, v in zip(bars2, vals2):
    pct = v/sum(vals2)*100
    ax2.text(bar.get_x()+bar.get_width()/2, v+30,
             f'{v:,}\n({pct:.0f}%)', ha='center', fontsize=10, fontweight='bold', color=ESCURO)
ax2.set_ylim(0, 3800)
callout(ax2, 'Crescimento\ndigital aqui', xy=(1, 722), xytext=(1, 1800), color=VERDE)
ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(BASE + 'fig_mevo_conversao.png', bbox_inches='tight', dpi=150)
plt.close()
print('fig_mevo_conversao.png')


# ═══════════════════════════════════════════════════════════════════
# FIG 5 — Concentracao medicos (Pareto) + Retencao
# Takeaway: 36% fazem 80%, 57% abandonam
# ═══════════════════════════════════════════════════════════════════
presc_med = presc_unica.groupby('idmedico')['idprescricao'].count().sort_values(ascending=False).reset_index()
presc_med['cumsum'] = presc_med['idprescricao'].cumsum()
presc_med['pct_acum'] = presc_med['cumsum'] / presc_med['idprescricao'].sum()
presc_med['rank_pct'] = np.arange(1, len(presc_med)+1) / len(presc_med)
medicos_80 = (presc_med['pct_acum'] <= 0.80).sum()
pct_med_80 = medicos_80 / len(presc_med) * 100

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
fig.patch.set_facecolor(BRANCO)

ax1 = axes[0]
ax1.set_facecolor(BRANCO)
ax1.plot(presc_med['rank_pct']*100, presc_med['pct_acum']*100, color=VERDE, lw=2.5)
ax1.fill_between(presc_med['rank_pct']*100, presc_med['pct_acum']*100, alpha=0.1, color=VERDE)
ax1.axhline(80, color=ALERTA, lw=1.5, ls='--')
ax1.axvline(pct_med_80, color=ALERTA, lw=1.5, ls='--')
ax1.set_xlabel('% dos Medicos', fontsize=10)
ax1.set_ylabel('% das Prescricoes', fontsize=10)
ax1.set_title(f'{pct_med_80:.0f}% dos medicos fazem\n80% das prescricoes', fontweight='bold', color=ESCURO)
ax1.text(pct_med_80 + 2, 30, f'{pct_med_80:.1f}% dos\nmedicos', color=ALERTA, fontsize=10, fontweight='bold')
ax1.set_xlim(0,100); ax1.set_ylim(0,100)
ax1.spines['top'].set_visible(False); ax1.spines['right'].set_visible(False)

# Retencao
med_mes = presc_unica.groupby(['idmedico','mes'])['idprescricao'].count().reset_index()
meses_str = ['2025-01','2025-02','2025-03','2025-04']
labels_m  = ['Jan','Fev','Mar','Abr']
jan_set = set(med_mes[med_mes['mes'].astype(str)=='2025-01']['idmedico'])
ativos  = [med_mes[med_mes['mes'].astype(str)==m]['idmedico'].nunique() for m in meses_str]
retidos = [len(jan_set & set(med_mes[med_mes['mes'].astype(str)==m]['idmedico'])) for m in meses_str]
novos   = [max(a-r,0) for a,r in zip(ativos,retidos)]; novos[0]=0
churn_abr = 1 - retidos[-1]/len(jan_set)

ax2 = axes[1]
ax2.set_facecolor(BRANCO)
ax2.bar(labels_m, retidos, color=VERDE,   label='Retidos (base Jan)', width=0.5)
ax2.bar(labels_m, novos,   bottom=retidos, color=AZUL, label='Novos entrantes', width=0.5, alpha=0.8)
ax2.set_ylabel('Medicos ativos', fontsize=10)
ax2.set_title(f'{churn_abr*100:.0f}% dos medicos de Janeiro\nnao estao em Abril', fontweight='bold', color=ESCURO)
ax2.legend(fontsize=9)
for i in range(1,4):
    pct = retidos[i]/len(jan_set)*100
    ax2.text(i, ativos[i]+80, f'{100-pct:.0f}% churn', ha='center', fontsize=9,
             color=ALERTA, fontweight='bold')
ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(BASE + 'fig_mevo_medicos.png', bbox_inches='tight', dpi=150)
plt.close()
print('fig_mevo_medicos.png')


# ═══════════════════════════════════════════════════════════════════
# FIG 6 — Especialidades: OR x Conversao (scatter)
# Takeaway: Psiquiatria outlier positivo, Pneumologia outlier negativo
# ═══════════════════════════════════════════════════════════════════
esp_stats = presc_full[presc_full['especialidade'].notna()].groupby('especialidade').agg(
    presc=('idprescricao','count'),
    or_=('visualizadapaciente','mean')
).reset_index()
vis_esp = presc_full[presc_full['visualizadapaciente'] & presc_full['especialidade'].notna()]
conv_esp = vis_esp.groupby('especialidade')['convertido'].mean().reset_index()
conv_esp.columns = ['especialidade','conv_vis']
esp_stats = esp_stats.merge(conv_esp, on='especialidade')
esp_stats = esp_stats[esp_stats['presc'] >= 500]

fig, ax = plt.subplots(figsize=(11, 5.5))
ax.set_facecolor(BRANCO)

for _, row in esp_stats.iterrows():
    cor = VERDE if row['conv_vis'] >= 0.12 else (AZUL if row['conv_vis'] >= 0.08 else CINZA)
    ax.scatter(row['or_']*100, row['conv_vis']*100,
               s=row['presc']/25, color=cor, alpha=0.85,
               edgecolors=BRANCO, linewidth=1.5, zorder=3)
    label = row['especialidade'].replace('E METABOLOGIA','').replace('E COMUNIDADE','').replace('E OBSTETRICIA','').strip()
    offset = (7, 5)
    if 'PSIQUIATRIA' in row['especialidade']:   offset = (7, -12)
    if 'CIRURGIA'    in row['especialidade']:   offset = (7, 5)
    ax.annotate(label.title(), (row['or_']*100, row['conv_vis']*100),
                textcoords='offset points', xytext=offset, fontsize=8.5, color=ESCURO)

ax.axhline(10.2, color=ALERTA, lw=1.5, ls='--', alpha=0.7, label='Media conversao 10,2%')
ax.axvline(50.4, color=CINZA,  lw=1.5, ls=':', alpha=0.7,  label='Media OR 50,4%')
ax.set_xlabel('Open Rate (%)', fontsize=11)
ax.set_ylabel('Conversao s/ Visualizadas (%)', fontsize=11)
ax.legend(fontsize=9)
ax.set_title('Psiquiatria converte 2,3x a media — controlados criam dependencia de canal',
             fontsize=12, fontweight='bold', color=ESCURO)

verde_p = mpatches.Patch(color=VERDE, label='Conv >= 12%')
azul_p  = mpatches.Patch(color=AZUL,  label='Conv 8-12%')
cinza_p = mpatches.Patch(color=CINZA, label='Conv < 8%')
ax.legend(handles=[verde_p, azul_p, cinza_p], fontsize=9, loc='lower right')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(BASE + 'fig_mevo_especialidades.png', bbox_inches='tight', dpi=150)
plt.close()
print('fig_mevo_especialidades.png')


# ═══════════════════════════════════════════════════════════════════
# FIG 7 — Segmentacao Comportamental (matriz 2x2)
# ═══════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
fig.patch.set_facecolor(BRANCO)

segs = [
    ('Inativo Digital\n48,2%  |  34.165 presc', 0, 0, ALERTA),
    ('Engajado\nNao Convertido\n45,3%  |  32.141', 1, 0, '#ED8936'),
    ('Comprou\nSem Rastreio\n1,4%  |  970', 0, 1, AZUL),
    ('Convertido\nDigital\n5,1%  |  3.631', 1, 1, VERDE),
]

ax = axes[0]
ax.set_xlim(0,2); ax.set_ylim(0,2)
ax.set_facecolor('#F0F4F8')
ax.axvline(1, color=BRANCO, lw=5)
ax.axhline(1, color=BRANCO, lw=5)
for label, x, y, cor in segs:
    rect = plt.Rectangle((x,y), 1, 1, facecolor=cor, alpha=0.88)
    ax.add_patch(rect)
    ax.text(x+0.5, y+0.5, label, ha='center', va='center',
            fontsize=10, fontweight='bold', color=BRANCO,
            multialignment='center')

ax.set_xticks([0.5,1.5]); ax.set_xticklabels(['Nao Abriu','Abriu'], fontsize=11, fontweight='bold')
ax.set_yticks([0.5,1.5]); ax.set_yticklabels(['Nao Comprou','Comprou'], fontsize=11, fontweight='bold')
ax.set_title('Apenas 5,1% chegam ao quadrante ideal\n— 93% estao nos 3 quadrantes de perda',
             fontweight='bold', fontsize=11, color=ESCURO)

# Funil
ax2 = axes[1]
ax2.set_facecolor(BRANCO)
etapas2 = ['Inativas\n(48,2%)', 'Abertas\nnao conv.\n(45,3%)', 'Comprou sem\ndigital (1,4%)', 'Convertidas\nDigital (5,1%)']
vals2 = [34165, 32141, 970, 3631]
cores2 = [ALERTA, '#ED8936', AZUL, VERDE]
bars = ax2.barh(etapas2, vals2, color=cores2, height=0.55)
for bar, v in zip(bars, vals2):
    pct = v/70907*100
    ax2.text(v+300, bar.get_y()+bar.get_height()/2,
             f'{v:,}', va='center', fontsize=10, fontweight='bold')
ax2.set_xlim(0, 42000)
ax2.invert_yaxis()
ax2.set_title('Distribuicao por perfil\nde engajamento', fontweight='bold', color=ESCURO)
ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(BASE + 'fig_mevo_comportamental.png', bbox_inches='tight', dpi=150)
plt.close()
print('fig_mevo_comportamental.png')


# ═══════════════════════════════════════════════════════════════════
# FIG 8 — Estados: OR x Conversao
# Takeaway: RJ anomalia, SC/RS lideram
# ═══════════════════════════════════════════════════════════════════
estados_data = [
    ('SP',48.8,12.8,34700), ('SC',61.5,12.7,3168), ('RS',49.7,14.9,3504),
    ('PR',39.2,10.1,3955),  ('MG',35.7, 7.4,3806), ('ES',37.5, 8.5,4054),
    ('RJ',54.7, 3.8,3278),  ('DF',53.2, 4.3,1000), ('RN',39.3, 6.6,1359),
    ('BA',47.6, 7.8, 968),
]

fig, ax = plt.subplots(figsize=(11, 5.5))
ax.set_facecolor(BRANCO)

for uf, or_, conv, vol in estados_data:
    if conv >= 10:    cor = VERDE
    elif conv >= 7:   cor = AZUL
    else:             cor = ALERTA
    ax.scatter(or_, conv, s=vol/28, color=cor, alpha=0.85,
               edgecolors=BRANCO, linewidth=1.5, zorder=3)
    offset = (7, 4)
    if uf == 'RJ': offset = (7, -12)
    if uf == 'SC': offset = (7, 5)
    ax.annotate(uf, (or_, conv), textcoords='offset points', xytext=offset,
                fontsize=11, fontweight='bold', color=ESCURO)

ax.axhline(10.2, color=CINZA, lw=1.5, ls='--', alpha=0.7, label='Media conv 10,2%')
ax.axvline(50.4, color=CINZA, lw=1.5, ls=':', alpha=0.7, label='Media OR 50,4%')

# Callout RJ
callout(ax, 'RJ: OR alto\nmas conv 3,8%\n— anomalia',
        xy=(54.7, 3.8), xytext=(46, 6.5), color=ALERTA)
callout(ax, 'RS lidera\nem conversao\n14,9%',
        xy=(49.7, 14.9), xytext=(42, 14.5), color=VERDE)

ax.set_xlabel('Open Rate (%)', fontsize=11)
ax.set_ylabel('Conversao s/ Visualizadas (%)', fontsize=11)
ax.set_title('RJ e DF: alta abertura, baixa conversao — investigar fricção no canal fisico',
             fontsize=12, fontweight='bold', color=ESCURO)

verde_p = mpatches.Patch(color=VERDE,  label='Conv >= 10%  (SP, SC, RS, PR)')
azul_p  = mpatches.Patch(color=AZUL,   label='Conv 7-10%  (ES, BA)')
alerta_p= mpatches.Patch(color=ALERTA, label='Conv < 7%   (RJ, DF, MG, RN)')
ax.legend(handles=[verde_p, azul_p, alerta_p], fontsize=9)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(BASE + 'fig_mevo_estados.png', bbox_inches='tight', dpi=150)
plt.close()
print('fig_mevo_estados.png')

print('\nTodos os graficos Mevo gerados!')
