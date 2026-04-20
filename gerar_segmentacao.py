"""
Gerador de graficos de segmentacao de usuarios — Case Saude+
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

BASE = __file__.replace('gerar_segmentacao.py', '')

presc   = pd.read_csv(BASE + 'prescricaomedicamento.csv')
meds    = pd.read_csv(BASE + 'medicamentos.csv')
medicos = pd.read_csv(BASE + 'medicos.csv')

presc['dataprescricao']     = pd.to_datetime(presc['dataprescricao'])
presc['datavenda']          = pd.to_datetime(presc['datavenda'], errors='coerce')
presc['nascimentopaciente'] = pd.to_datetime(presc['nascimentopaciente'], errors='coerce')
presc_unica = presc.drop_duplicates(subset='idprescricao').copy()
presc_unica['convertido'] = presc_unica['itemvendido'] == 1
presc_unica['mes'] = presc_unica['dataprescricao'].dt.to_period('M')

REF = pd.Timestamp('2025-04-18')
presc_unica['idade'] = ((REF - presc_unica['nascimentopaciente']).dt.days / 365.25)
presc_unica['faixa'] = pd.cut(presc_unica['idade'], bins=[0,17,29,39,49,59,69,120],
    labels=['0-17','18-29','30-39','40-49','50-59','60-69','70+'])

CORES = ['#2E86AB','#A23B72','#F18F01','#C73E1D','#44BBA4','#1A1A2E']
plt.rcParams.update({'figure.dpi': 150, 'font.family': 'DejaVu Sans'})

# ── FIG 1: Matriz Comportamental ──────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

segs = [
    ('Inativo Digital\n48,2%  (34.165)', 0, 0, CORES[3]),
    ('Engajado Nao\nConvertido\n45,3%  (32.141)', 1, 0, CORES[2]),
    ('Comprou Sem\nDigital\n1,4%  (970)', 0, 1, CORES[0]),
    ('Convertido\nDigital\n5,1%  (3.631)', 1, 1, CORES[4]),
]

ax = axes[0]
ax.set_xlim(0, 2); ax.set_ylim(0, 2)
ax.set_facecolor('#EEEEEE')
ax.axvline(1, color='white', lw=4)
ax.axhline(1, color='white', lw=4)

for label, x, y, cor in segs:
    rect = plt.Rectangle((x, y), 1, 1, facecolor=cor, alpha=0.88)
    ax.add_patch(rect)
    ax.text(x+0.5, y+0.5, label, ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')

ax.set_xticks([0.5, 1.5])
ax.set_xticklabels(['Nao Abriu', 'Abriu'], fontsize=11, fontweight='bold')
ax.set_yticks([0.5, 1.5])
ax.set_yticklabels(['Nao Comprou', 'Comprou'], fontsize=11, fontweight='bold')
ax.set_xlabel('Engajamento Digital (Open Rate)', fontsize=11)
ax.set_ylabel('Conversao', fontsize=11)
ax.set_title('Matriz Comportamental de Prescricoes\n(70.907 prescricoes)', fontweight='bold', fontsize=12)

ax2 = axes[1]
etapas = ['Emitidas\n(100%)', 'Visualizadas\n(50,4%)', 'Convertidas\nDigital\n(5,1%)']
valores = [70907, 35772, 3631]
cores_f = [CORES[0], CORES[2], CORES[4]]
bars = ax2.barh(etapas, valores, color=cores_f, height=0.5)
for bar, v in zip(bars, valores):
    pct = v/70907*100
    ax2.text(v + 500, bar.get_y() + bar.get_height()/2,
             f'{v:,}  ({pct:.1f}%)', va='center', fontsize=11, fontweight='bold')
ax2.set_xlim(0, 88000)
ax2.set_title('Funil de Engajamento e Conversao', fontweight='bold', fontsize=12)
ax2.set_xlabel('Numero de Prescricoes')
ax2.invert_yaxis()

plt.suptitle('Segmentacao Comportamental — Saude+', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(BASE + 'fig_seg_comportamental.png', bbox_inches='tight', dpi=150)
plt.close()
print('fig_seg_comportamental.png criada')

# ── FIG 2: Segmentacao de Medicos ─────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

labels_seg  = ['VIP\n(50+)\n92 med.', 'High\n(10-49)\n1.596 med.', 'Mid\n(3-9)\n4.755 med.', 'Low\n(1-2)\n9.388 med.']
presc_vals  = [7591, 28379, 22781, 12156]
or_vals     = [61.4, 50.0, 47.4, 49.4]
conv_vals   = [8.1, 6.4, 6.0, 7.0]
cores_seg   = [CORES[3], CORES[0], CORES[2], CORES[4]]

ax1, ax2, ax3 = axes

bars = ax1.bar(range(4), presc_vals, color=cores_seg, width=0.6)
ax1.set_xticks(range(4)); ax1.set_xticklabels(labels_seg, fontsize=9)
ax1.set_title('Volume de Prescricoes\npor Segmento', fontweight='bold')
ax1.set_ylabel('Prescricoes')
for bar, v in zip(bars, presc_vals):
    pct = v/70907*100
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+300,
             f'{v:,}\n({pct:.0f}%)', ha='center', va='bottom', fontsize=9, fontweight='bold')

bars2 = ax2.bar(range(4), or_vals, color=cores_seg, width=0.6)
ax2.axhline(50.4, color='gray', ls='--', lw=1.5, label='Media geral 50,4%')
ax2.set_xticks(range(4)); ax2.set_xticklabels(labels_seg, fontsize=9)
ax2.set_title('Open Rate Medio dos Pacientes\npor Segmento de Medico', fontweight='bold')
ax2.set_ylabel('Open Rate (%)')
ax2.set_ylim(0, 78); ax2.legend(fontsize=8)
for bar, v in zip(bars2, or_vals):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
             f'{v:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Retencao mes a mes
med_mes = presc_unica.groupby(['idmedico','mes'])['idprescricao'].count().reset_index()
meses_str = ['2025-01','2025-02','2025-03','2025-04']
labels_m  = ['Jan', 'Fev', 'Mar', 'Abr']
jan_set = set(med_mes[med_mes['mes'].astype(str)=='2025-01']['idmedico'])
ativos  = [med_mes[med_mes['mes'].astype(str)==m]['idmedico'].nunique() for m in meses_str]
retidos = [len(jan_set & set(med_mes[med_mes['mes'].astype(str)==m]['idmedico'])) for m in meses_str]
novos   = [max(a - r, 0) for a, r in zip(ativos, retidos)]
novos[0] = 0

ax3.bar(labels_m, retidos, color=CORES[0], label='Retidos (base Jan)', width=0.55)
ax3.bar(labels_m, novos, bottom=retidos, color=CORES[4], label='Novos entrantes', width=0.55, alpha=0.85)
ax3.set_title('Retencao de Medicos\n(coorte Janeiro 2025)', fontweight='bold')
ax3.set_ylabel('N de Medicos Ativos')
ax3.legend(fontsize=9)
for i in range(1, 4):
    pct = retidos[i] / len(jan_set) * 100
    ax3.text(i, ativos[i] + 80, f'{pct:.0f}% ret.', ha='center', fontsize=9, color='#444')

plt.suptitle('Segmentacao de Medicos — Volume, Engajamento e Retencao', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(BASE + 'fig_seg_medicos.png', bbox_inches='tight', dpi=150)
plt.close()
print('fig_seg_medicos.png criada')

# ── FIG 3: Perfil — Faixa Etaria, Estado, Especialidade ──────────────────────
fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))

fe_stats = presc_unica.groupby('faixa').agg(
    presc=('idprescricao','count'),
    or_=('visualizadapaciente','mean')
).reset_index()
vis_fe = presc_unica[presc_unica['visualizadapaciente']].groupby('faixa')['convertido'].mean().reset_index()
vis_fe.columns = ['faixa','conv_vis']
fe_stats = fe_stats.merge(vis_fe, on='faixa')
fe_cores = [CORES[i % len(CORES)] for i in range(len(fe_stats))]

ax1 = axes[0]
ax1.scatter(fe_stats['or_']*100, fe_stats['conv_vis']*100,
            s=fe_stats['presc']/18, c=fe_cores, alpha=0.88, edgecolors='white', lw=1.5, zorder=3)
for _, row in fe_stats.iterrows():
    ax1.annotate(str(row['faixa']), (row['or_']*100, row['conv_vis']*100),
                 textcoords='offset points', xytext=(7, 4), fontsize=9, fontweight='bold')
ax1.axhline(10.2, color='gray', ls='--', lw=1, alpha=0.6, label='Media conv 10,2%')
ax1.axvline(50.4, color='gray', ls=':', lw=1, alpha=0.6, label='Media OR 50,4%')
ax1.set_xlabel('Open Rate (%)'); ax1.set_ylabel('Conversao s/ Visualizadas (%)')
ax1.set_title('Faixa Etaria\n(tamanho = volume de prescricoes)', fontweight='bold')
ax1.legend(fontsize=8)

ax2 = axes[1]
estados = [('SP',48.8,12.8,34700),('SC',61.5,12.7,3168),('RS',49.7,14.9,3504),
           ('PR',39.2,10.1,3955),('MG',35.7,7.4,3806),('ES',37.5,8.5,4054),
           ('RJ',54.7,3.8,3278),('DF',53.2,4.3,1000),('RN',39.3,6.6,1359),('BA',47.6,7.8,968)]
verde_p   = mpatches.Patch(color=CORES[0], label='Conv >= 10%')
amarelo_p = mpatches.Patch(color=CORES[2], label='Conv 7-10%')
vermelho_p= mpatches.Patch(color=CORES[3], label='Conv < 7%')
for uf, or_, conv, vol in estados:
    cor = CORES[0] if conv >= 10 else (CORES[2] if conv >= 7 else CORES[3])
    ax2.scatter(or_, conv, s=vol/28, color=cor, alpha=0.85, edgecolors='white', lw=1.5, zorder=3)
    ax2.annotate(uf, (or_, conv), textcoords='offset points', xytext=(6,3), fontsize=10, fontweight='bold')
ax2.axhline(10.2, color='gray', ls='--', lw=1, alpha=0.6)
ax2.axvline(50.4, color='gray', ls=':', lw=1, alpha=0.6)
ax2.set_xlabel('Open Rate (%)'); ax2.set_ylabel('Conversao s/ Visualizadas (%)')
ax2.set_title('Estados\n(tamanho = volume)', fontweight='bold')
ax2.legend(handles=[verde_p, amarelo_p, vermelho_p], fontsize=8)

ax3 = axes[2]
esps = [('Psiquiatria',57.0,23.9,2633),('Cirurgia\nGeral',71.8,8.9,5380),
        ('Med\nFamilia',60.1,11.2,2804),('Ortopedia',41.3,13.0,4473),
        ('Clinica\nMedica',43.2,9.3,15293),('SEM ESP',58.1,9.7,12959),
        ('Pediatria',47.6,7.4,8702),('Ginecologia',45.4,10.5,2687),
        ('Cardiologia',43.7,6.9,1945),('Endocrino',45.2,6.6,2088)]
for esp, or_, conv, vol in esps:
    cor = CORES[0] if conv >= 12 else (CORES[2] if conv >= 8 else CORES[3])
    ax3.scatter(or_, conv, s=vol/28, color=cor, alpha=0.85, edgecolors='white', lw=1.5, zorder=3)
    offset = (6, 4) if esp != 'Psiquiatria' else (6, -12)
    ax3.annotate(esp, (or_, conv), textcoords='offset points', xytext=offset, fontsize=8)
ax3.axhline(10.2, color='gray', ls='--', lw=1, alpha=0.6)
ax3.axvline(50.4, color='gray', ls=':', lw=1, alpha=0.6)
ax3.set_xlabel('Open Rate (%)'); ax3.set_ylabel('Conversao s/ Visualizadas (%)')
ax3.set_title('Especialidade Medica\n(tamanho = volume)', fontweight='bold')
ax3.legend(handles=[verde_p, amarelo_p, vermelho_p], fontsize=8)

plt.suptitle('Segmentacao por Perfil — Faixa Etaria, Estado e Especialidade', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(BASE + 'fig_seg_perfil.png', bbox_inches='tight', dpi=150)
plt.close()
print('fig_seg_perfil.png criada')
print('Todos os graficos de segmentacao gerados!')
