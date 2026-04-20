# Executive Summary — Case Analytics Saúde+
**Período:** Janeiro – Abril 2025 | **Base:** 70.907 prescrições | **Elaborado em:** Abril/2025

---

## Contexto

A **Saúde+** é uma plataforma digital que integra prontuário eletrônico, prescrição de medicamentos, atestados e solicitação de exames. Esta análise cobre 108 dias de operação (01/01 a 18/04/2025), com dados de prescrições, pacientes, médicos e canais de venda.

---

## Resumo Executivo — 6 KPIs que definem o momento da plataforma

| Métrica | Valor | Referência |
|---|---|---|
| Prescrições emitidas | **70.907** | +22% de Jan para Mar |
| Pacientes únicos atendidos | **68.767** | 1,03 presc/paciente |
| Médicos ativos | **15.831** | de 45.025 cadastrados |
| Open Rate (receita aberta pelo paciente) | **50,4%** | 35.772 de 70.907 |
| Taxa de conversão (s/ visualizadas) | **10,2%** | 3.631 de 35.772 |
| Total de vendas realizadas | **4.601** | Farmácia física: 84% · Marketplace: 16% |

> **Leitura crítica:** Metade das prescrições nunca é acessada digitalmente pelo paciente. Das que são acessadas, apenas 1 em 10 resulta em venda rastreada. Há espaço significativo para crescimento sem aumentar o volume de prescrições.

---

## Análises-chave

### 1. Crescimento consistente, sazonalidade previsível
- Volume cresce mês a mês (+22% de Jan a Mar), indicando expansão ativa da base de médicos
- Queda expressiva nos fins de semana (comportamento esperado para consultas presenciais)
- **Pico de emissão: 13h** — pacientes saem da consulta matinal e o médico emite a receita digital no início da tarde
- Implicação: janela de ouro para notificação push é entre 13h e 14h

### 2. Base de médicos concentrada — Pareto claro
- **36,4% dos médicos** (5.767 de 15.831) geram **80% de todas as prescrições**
- Top 5 especialidades concentram mais de 50% do volume: Clínica Médica (21,6%), Sem Especialidade/CRO (2º), Pediatria (12,3%)
- 8.204 médicos cadastrados como "Sem Especialidade" — maioria são cirurgiões-dentistas (CROs), com risco de prescrições fora de escopo

### 3. Open Rate: 50,4% — a receita digital não está chegando ao paciente
- Apenas metade das prescrições é visualizada digitalmente
- Fins de semana têm open rate maior (pacientes com mais tempo), mas volume muito menor
- Especialidades com open rate abaixo da média são candidatas a campanhas de engajamento

### 4. Conversão: 10,2% sobre visualizadas, 6,5% sobre total
- Das 35.772 prescrições visualizadas, 3.631 resultaram em venda rastreada digitalmente
- **970 vendas adicionais** ocorreram em farmácia física sem abertura digital prévia — 21% das vendas no canal físico operam fora do funil digital
- O marketplace representa 16% das vendas (722), com potencial de crescimento via redução de fricção

### 5. Comportamento de compra: janela de 24h é decisiva
- **64% das compras** ocorrem nas primeiras 24 horas após a prescrição
- Mediana de tempo até a compra: **8,2 horas**
- Após 48h, a probabilidade de conversão cai drasticamente — o paciente provavelmente comprou em farmácia física sem rastreamento

---

## Insights Acionáveis — priorizados por impacto

| # | Problema | Evidência | Recomendação |
|---|---|---|---|
| 1 | 49,6% das receitas não são abertas | 35.135 de 70.907 não visualizadas | Notificação push/SMS em até 5 min após emissão, personalizada com nome do medicamento |
| 2 | 36% dos médicos fazem 80% do volume | 5.767 médicos = 80% das prescrições | Programa "Médicos Parceiros": suporte prioritário, NPS mensal, treinamento dedicado |
| 3 | Marketplace com baixa penetração | 722 vendas vs 3.879 em farmácia física | Investigar fricção (estoque, preço, UX) e testar desconto na 1ª compra digital |
| 4 | 970 vendas sem rastreamento digital | 21% das vendas físicas sem visualização | Implementar QR Code / código de rastreio offline para fechar o funil |
| 5 | Pacientes crônicos sem ferramenta de renovação | 2,9% com 2+ prescrições (alto LTV) | Funcionalidade de renovação automática para Glifage XR, Paracetamol, Aerolin |
| 6 | Pico de emissão às 13h sem SLA de notificação definido | Concentração no início da tarde | Garantir SLA < 5 min nos horários de pico e alocar suporte conforme curva |
| 7 | 8.204 médicos "Sem Especialidade" — risco de compliance | Maioria são CROs (dentistas) | Enriquecer cadastro separando CRM vs CRO; auditar prescrições de CROs |

---

## Roadmap de Ações

### Curto Prazo (0–30 dias)
- [ ] Implementar notificação push/SMS pós-prescrição com personalização por medicamento
- [ ] Definir SLA de notificação < 5 min nos horários de pico (13h, 9h–11h)
- [ ] Criar alerta de rastreabilidade para vendas sem visualização digital (970 casos)

### Médio Prazo (30–90 dias)
- [ ] Lançar programa "Médicos Parceiros" com os top 5.767 prescritores
- [ ] Testar campanha de incentivo ao marketplace (desconto na 1ª compra digital)
- [ ] Enriquecer cadastro de médicos — separar CRM vs CRO
- [ ] Campanha de re-engajamento nos fins de semana para prescrições não abertas

### Longo Prazo (90+ dias)
- [ ] Desenvolver funcionalidade de renovação de receita para crônicos
- [ ] Modelo preditivo de conversão por paciente (propensão a comprar online)
- [ ] Dashboard de monitoramento contínuo de KPIs (Open Rate, Conversão, Churn de médicos)
- [ ] Análise de churn de médicos: quantos do mês 1 deixaram de prescrever no mês 4?

---

## Notas Metodológicas

- **Open Rate** = prescrições visualizadas / total de prescrições únicas emitidas
- **Conversão** = vendas de prescrições visualizadas / total de prescrições visualizadas (10,2%)
- **Conversão Geral** = total de vendas / total de prescrições (6,5%)
- **Total de vendas**: 4.601 (3.879 farmácia física + 722 marketplace). O KPI "3.631" refere-se especificamente às vendas de prescrições que foram visualizadas digitalmente.
- Período analisado: 01/01/2025 a 18/04/2025 (108 dias úteis e fins de semana)
- Base de dados: `prescricaomedicamento.csv` (73.929 linhas / 70.907 prescrições únicas)
