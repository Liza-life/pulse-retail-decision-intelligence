# Pulse | Retail Decision Intelligence

Plataforma analítica desenvolvida em Python para simular uma solução de Decision Intelligence aplicada ao varejo.

O projeto transforma dados operacionais de supermercado em indicadores, diagnósticos, previsões e recomendações estratégicas.

## Objetivo

Criar uma solução de dados capaz de apoiar decisões sobre vendas, lucratividade, estoque, produtos, clientes e performance comercial.

## Funcionalidades

- Visão executiva de receita, lucro, margem e clientes
- Análise de receita por categoria
- Gestão de estoque com status crítico, atenção e saudável
- Curva ABC / Pareto de produtos
- IA analítica simulada para perguntas sobre os dados
- Forecast de receita
- Simulador estratégico de cenários
- Análise de qualidade dos dados
- Download da base analítica em CSV

## Tecnologias utilizadas

- Python
- Pandas
- Streamlit
- Plotly
- NumPy

## Estrutura do projeto

```text
pulse-decision-intelligence/
│
├── app/
│   └── app.py
│
├── data/
│   ├── vendas.csv
│   ├── produtos.csv
│   └── clientes.csv
│
├── src/
│   └── generate_data.py
│
├── README.md
├── requirements.txt
└── .gitignore