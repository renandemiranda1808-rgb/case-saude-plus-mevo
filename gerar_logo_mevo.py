"""
Cria logo Mevo + variantes para uso nos slides
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

BASE = os.path.dirname(os.path.abspath(__file__)) + os.sep

VERDE     = '#22C35E'
VERDE_ESC = '#179848'
ESCURO    = '#1A202C'
BRANCO    = '#FFFFFF'
ROSA_CLARO= '#FFF5F7'

def make_logo(bg_color, text_color, dot_color, filename, width=4, height=1.2, alpha_bg=1.0):
    fig, ax = plt.subplots(figsize=(width, height))
    fig.patch.set_alpha(0)
    ax.set_xlim(0, width); ax.set_ylim(0, height)
    ax.axis('off')

    # Fundo arredondado (opcional)
    if bg_color:
        fancy = FancyBboxPatch((0.05, 0.05), width-0.1, height-0.1,
                               boxstyle='round,pad=0.08',
                               facecolor=bg_color, edgecolor='none', alpha=alpha_bg)
        ax.add_patch(fancy)

    # Ponto verde antes do nome (identidade visual Mevo)
    ax.scatter([0.38], [height/2], s=280, color=dot_color, zorder=5)

    # Texto "mevo"
    ax.text(0.72, height/2, 'mevo', fontsize=52, fontweight='bold',
            color=text_color, va='center', ha='left',
            fontfamily='DejaVu Sans')

    plt.tight_layout(pad=0)
    plt.savefig(BASE + filename, dpi=200, bbox_inches='tight',
                transparent=(bg_color is None))
    plt.close()
    print(f'{filename} criado')

# Logo verde sobre fundo transparente (uso em slides claros)
make_logo(None,   VERDE,  VERDE,  'logo_mevo_verde.png', width=3.5, height=1.0)

# Logo escura sobre fundo transparente (uso em slides escuros)
make_logo(None,   ESCURO, VERDE,  'logo_mevo_escura.png', width=3.5, height=1.0)

# Logo branca sobre fundo transparente (uso em fundo verde/escuro)
make_logo(None,   BRANCO, BRANCO, 'logo_mevo_branca.png', width=3.5, height=1.0)

# Logo em pill verde (selo marca)
make_logo(VERDE,  BRANCO, BRANCO, 'logo_mevo_pill.png',   width=3.5, height=1.0)

print('Logos criados!')
