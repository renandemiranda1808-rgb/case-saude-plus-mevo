# Saúde+ Analytics — Case Técnico Mevo

Análise completa de prescrições digitais da plataforma Saúde+, cobrindo volume, engajamento, conversão, segmentação de médicos e pacientes, com planos de ação acionáveis.

## Período analisado
Janeiro – Abril 2025 | 70.907 prescrições | 68.767 pacientes | 15.831 médicos

---

## Estrutura do projeto

```
├── prescricaomedicamento.csv   # Dados de prescrições (nível medicamento)
├── medicamentos.csv            # Cadastro de medicamentos
├── medicos.csv                 # Cadastro de médicos (especialidade, estado)
│
├── dashboard_mevo.py           # Dashboard interativo (Streamlit)
│
├── gerar_apresentacao_mevo.py  # Gerador do PPTX executivo
├── gerar_graficos_mevo.py      # Gerador de gráficos (paleta Mevo)
├── gerar_logo_mevo.py          # Gerador de variantes do logo
├── gerar_segmentacao.py        # Gráficos de segmentação
├── gerar_apresentacao.py       # Versão anterior do PPTX
│
├── case_mevo_v4.pptx           # Apresentação executiva final
├── executive_summary.md        # Resumo executivo em Markdown
│
└── fig_*.png                   # Gráficos gerados
```

---

## Como rodar

### Dashboard interativo
```bash
pip install streamlit plotly pandas numpy pillow
streamlit run dashboard_mevo.py
```

### Gerar apresentação PPTX
```bash
pip install python-pptx matplotlib pandas numpy pillow
python gerar_graficos_mevo.py
python gerar_logo_mevo.py
python gerar_apresentacao_mevo.py
```

---

## Perguntas respondidas

| # | Pergunta | Onde |
|---|---|---|
| 1 | Prescrições diárias e sazonalidade | Dashboard Tab 1 · Slide 3 |
| 2 | Pacientes atendidos | Dashboard KPIs · Slide 2 |
| 3 | Especialidades que mais prescreveram | Dashboard Tab 3 · Slide 8 |
| 4 | Taxa de Open Rate | Dashboard Tab 4 · Slide 5 |
| 5 | Taxa de conversão por canal | Dashboard Tab 5 · Slide 6 |
| 6 | Outras informações dos dados | Dashboard Tabs 2, 6, 7 · Slides 4, 7, 9, 10 |
| 7 | Insights para eficiência operacional | Dashboard Tab 8 · Slides 11–12 |

---

## Principais findings

- **50,4% de Open Rate** — 35.135 receitas nunca acessadas
- **10,2% de conversão** s/ visualizadas — meta: 13% (+2,8 p.p.)
- **57% de churn** de médicos Jan→Abr — risco crítico de receita
- **Psiquiatria** converte 23,9% (2,3× a média) — canal digital obrigatório
- **RJ** anomalia: OR 54,7% mas conversão 3,8% — investigar urgente
- **SC + RS** melhores benchmarks nacionais — modelo a replicar

---

## Stack

- **Python 3.12**
- **pandas, numpy** — análise de dados
- **matplotlib, plotly** — visualizações
- **streamlit** — dashboard interativo
- **python-pptx** — geração da apresentação executiva
- **Pillow** — processamento de imagens/logo
