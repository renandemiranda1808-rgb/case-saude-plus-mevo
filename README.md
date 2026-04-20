# Saúde+ Analytics — Case Técnico Mevo

Análise completa de prescrições digitais da plataforma Saúde+, cobrindo volume, engajamento, conversão, segmentação de médicos e pacientes, com planos de ação acionáveis.

> **Desenvolvido inteiramente com IA** — Claude (Anthropic) foi usado em todas as etapas: exploração dos dados, geração de insights, criação dos gráficos, construção do dashboard e da apresentação executiva.

**Período:** Janeiro – Abril 2025 | 70.907 prescrições | 68.767 pacientes | 15.831 médicos

---

## 🤖 Como a IA foi usada

| Etapa | Ferramenta | O que fez |
|---|---|---|
| Exploração de dados | Claude | Auditoria de qualidade, detecção de anomalias (RJ, SEM ESP) |
| Análise estatística | Claude + Python | Segmentação RFM de médicos, coorte de retenção, funil |
| Visualizações | Claude | Gerou todos os scripts matplotlib/plotly com paleta Mevo |
| Dashboard interativo | Claude | Escreveu o `dashboard_mevo.py` completo (8 abas, filtros) |
| Apresentação executiva | Claude | 12 slides PPTX com brand Mevo, waterfall PDCA |
| Validação dos dados | Claude | Cruzou KPIs contra os CSVs, corrigiu 3 erros críticos |

---

## 🏗️ Arquitetura de Produção — Databricks

O dashboard foi construído em Streamlit e é **nativamente compatível com Databricks Apps**.
Em produção, a evolução natural seria:

```
┌─────────────────────────────────────────────────────┐
│                  DATABRICKS PLATFORM                │
│                                                     │
│  prescricaomedicamento.csv ──► Delta Lake           │
│  medicamentos.csv          ──► Unity Catalog        │
│  medicos.csv               ──► (governança + ACL)   │
│                                      │              │
│                               Databricks SQL        │
│                               (queries ao vivo)     │
│                                      │              │
│              dashboard_mevo.py ──► Databricks Apps  │
│              (mesmo código Streamlit)    │           │
│                                      │              │
│                               URL pública segura    │
│                               com SSO + RBAC        │
└─────────────────────────────────────────────────────┘
```

**Vantagens do Databricks Apps vs. Streamlit Cloud:**
- Dados em **Delta Lake** com versionamento e time travel
- **Unity Catalog** para governança e controle de acesso por coluna
- Queries ao vivo — dashboard sempre atualizado sem re-deploy
- **SSO** integrado — só quem deve ver, vê
- Escalabilidade automática de compute

A migração exige apenas trocar a leitura de CSV por queries Spark SQL — o código do dashboard permanece o mesmo.

---

## Estrutura do projeto

```
├── prescricaomedicamento.csv   # Dados de prescrições (nível medicamento)
├── medicamentos.csv            # Cadastro de medicamentos
├── medicos.csv                 # Cadastro de médicos (especialidade, estado)
│
├── dashboard_mevo.py           # Dashboard interativo (Streamlit / Databricks Apps)
├── requirements.txt            # Dependências Python
│
├── gerar_apresentacao_mevo.py  # Gerador do PPTX executivo
├── gerar_graficos_mevo.py      # Gerador de gráficos (paleta Mevo)
├── gerar_logo_mevo.py          # Gerador de variantes do logo
├── gerar_segmentacao.py        # Gráficos de segmentação
│
├── case_mevo_v4.pptx           # Apresentação executiva final
├── executive_summary.md        # Resumo executivo em Markdown
│
└── fig_*.png                   # Gráficos gerados
```

---

## Como rodar

### Dashboard (local)
```bash
pip install -r requirements.txt
streamlit run dashboard_mevo.py
```

### Dashboard (Databricks Apps)
```python
# Substituir leitura de CSV por Delta Lake:
# df = pd.read_csv("prescricaomedicamento.csv")
df = spark.table("saude_plus.prescricoes.prescricaomedicamento").toPandas()
```
Deploy via Databricks Apps UI — mesmo arquivo, zero alteração de lógica.

### Gerar apresentação PPTX
```bash
python gerar_graficos_mevo.py
python gerar_logo_mevo.py
python gerar_apresentacao_mevo.py
```

---

## Perguntas respondidas

| # | Pergunta | Dashboard | Slide |
|---|---|---|---|
| 1 | Prescrições diárias e sazonalidade | Tab 1 | Slide 3 |
| 2 | Pacientes atendidos | KPIs | Slide 2 |
| 3 | Especialidades que mais prescreveram | Tab 3 | Slide 8 |
| 4 | Taxa de Open Rate | Tab 4 | Slide 5 |
| 5 | Taxa de conversão por canal | Tab 5 | Slide 6 |
| 6 | Outras informações dos dados | Tabs 2, 6, 7 | Slides 4, 7, 9, 10 |
| 7 | Insights para eficiência operacional | Tab 8 | Slides 11–12 |

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

- **Python 3.12** — análise e geração de artefatos
- **pandas, numpy** — manipulação de dados
- **matplotlib, plotly** — visualizações estáticas e interativas
- **streamlit** — dashboard interativo (compatível com Databricks Apps)
- **python-pptx** — apresentação executiva programática
- **Pillow** — extração e processamento do logo Mevo
- **Claude (Anthropic)** — IA usada em todo o desenvolvimento
