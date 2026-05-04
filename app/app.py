import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Pulse | Retail Decision Intelligence",
    layout="wide"
)

STATUS_COLORS = {
    "Saudável": "#22C55E",
    "Atenção": "#FBBF24",
    "Crítico": "#EF4444"
}

ABC_COLORS = {
    "A - Alta relevância": "#22C55E",
    "B - Média relevância": "#FBBF24",
    "C - Baixa relevância": "#EF4444"
}

CATEGORY_COLORS = {
    "Alimentos": "#38BDF8",
    "Bebidas": "#F97316",
    "Limpeza": "#A78BFA",
    "Higiene": "#EC4899",
    "Carnes": "#EF4444",
    "Frios": "#14B8A6",
    "Laticínios": "#FBBF24",
    "Hortifruti": "#22C55E"
}

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(56,189,248,0.18), transparent 30%),
        radial-gradient(circle at top right, rgba(251,191,36,0.12), transparent 24%),
        linear-gradient(180deg, #05070D 0%, #070B14 100%);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1220 0%, #070B14 100%);
    border-right: 1px solid #22304A;
}

.block-container {
    max-width: 1380px;
    padding-top: 2rem;
}

h1, h2, h3, p, label {
    color: #F8FAFC;
}

.ai-card {
    background: linear-gradient(135deg, rgba(56,189,248,0.16), rgba(16,26,46,0.98));
    padding: 24px;
    border-radius: 22px;
    border: 1px solid rgba(56,189,248,0.45);
    box-shadow: 0 18px 45px rgba(0,0,0,0.38);
}

.warning-card {
    background: linear-gradient(135deg, rgba(251,191,36,0.16), rgba(16,26,46,0.98));
    padding: 24px;
    border-radius: 22px;
    border: 1px solid rgba(251,191,36,0.45);
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #101A2E, #0B1220);
    padding: 18px;
    border-radius: 18px;
    border: 1px solid #22304A;
}

[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
}

[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-weight: 900 !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: #101A2E;
    border-radius: 14px 14px 0 0;
    padding: 12px 18px;
    color: #CBD5E1;
    border: 1px solid #22304A;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #38BDF8, #2563EB);
    color: white;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    vendas = pd.read_csv("../data/vendas.csv")
    produtos = pd.read_csv("../data/produtos.csv")
    clientes = pd.read_csv("../data/clientes.csv")

    vendas["data"] = pd.to_datetime(vendas["data"])

    df = vendas.merge(produtos, on="produto_id")
    df = df.merge(clientes, on="cliente_id")

    df["mes"] = df["data"].dt.to_period("M").astype(str)

    return df, produtos


def moeda(v):
    return f"R$ {v:,.0f}"


def plot(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#F8FAFC",
        title_font_size=20,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def resposta_ia(pergunta, contexto):
    pergunta = pergunta.lower()

    if "receita" in pergunta:
        return f"A receita total analisada foi de {moeda(contexto['receita'])}. A categoria com maior receita foi {contexto['top_categoria']}."

    if "lucro" in pergunta or "margem" in pergunta:
        return f"O lucro total foi de {moeda(contexto['lucro'])}, com margem média de {contexto['margem']:.1%}. Isso indica uma operação com rentabilidade {'saudável' if contexto['margem'] >= 0.25 else 'que precisa de atenção'}."

    if "estoque" in pergunta:
        return f"Foram identificados {contexto['produtos_criticos']} produtos em situação crítica de estoque. A recomendação é priorizar reposição dos itens críticos e revisar o estoque mínimo."

    if "produto" in pergunta or "produtos" in pergunta:
        return f"O produto com maior receita foi {contexto['top_produto']}. Produtos da classe A devem ser priorizados em campanhas e reposição."

    if "cliente" in pergunta or "clientes" in pergunta:
        return f"A base possui {contexto['clientes']} clientes únicos. A análise por cidade e perfil pode ajudar a entender concentração regional e comportamento de compra."

    if "previsão" in pergunta or "forecast" in pergunta:
        return "A previsão foi calculada com tendência linear simples dos meses anteriores. Ela serve como visão inicial, mas pode ser evoluída com modelos mais avançados."

    return (
        "Com base nos dados, recomendo analisar receita, margem, estoque crítico, produtos classe A "
        "e comportamento por categoria antes de tomar decisões comerciais."
    )


df, df_produtos = load_data()

st.markdown("""
# 🧠 Pulse | Retail Decision Intelligence
Plataforma analítica para varejo com foco em performance, diagnóstico, IA analítica e tomada de decisão.
""")

receita = df["valor_total"].sum()
lucro = df["lucro"].sum()
margem = lucro / receita
clientes = df["cliente_id"].nunique()
vendas_mes = df.groupby("mes", as_index=False)["valor_total"].sum()

top_categoria = (
    df.groupby("categoria")["valor_total"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
)

top_produto = (
    df.groupby("nome")["valor_total"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
)

estoque_temp = df_produtos.copy()
estoque_temp["status"] = estoque_temp.apply(
    lambda x: "Crítico" if x["estoque_atual"] <= x["estoque_minimo"]
    else "Atenção" if x["estoque_atual"] <= x["estoque_minimo"] * 1.5
    else "Saudável",
    axis=1
)
produtos_criticos = len(estoque_temp[estoque_temp["status"] == "Crítico"])

contexto_ia = {
    "receita": receita,
    "lucro": lucro,
    "margem": margem,
    "clientes": clientes,
    "top_categoria": top_categoria,
    "top_produto": top_produto,
    "produtos_criticos": produtos_criticos
}

abas = st.tabs([
    "📌 Executivo",
    "📊 Receita",
    "📦 Estoque",
    "🧠 Inteligência",
    "🤖 IA Analítica",
    "📈 Forecast",
    "🧪 Simulador",
    "📥 Dados",
    "📊 Qualidade",
    "ℹ️ Sobre"
])


with abas[0]:
    st.markdown("## 📌 Visão Executiva")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Receita", moeda(receita))
    c2.metric("Lucro", moeda(lucro))
    c3.metric("Margem", f"{margem:.1%}")
    c4.metric("Clientes", clientes)

    fig = px.area(
        vendas_mes,
        x="mes",
        y="valor_total",
        title="Evolução da Receita",
        color_discrete_sequence=["#38BDF8"]
    )
    plot(fig)

    st.markdown(f"""
    <div class="ai-card">
        <h3>🤖 Insight automático</h3>
        <p>
        A operação gerou <b>{moeda(receita)}</b> em receita e <b>{moeda(lucro)}</b> em lucro.
        A margem média foi de <b>{margem:.1%}</b>. A categoria com maior desempenho foi
        <b>{top_categoria}</b> e o produto líder foi <b>{top_produto}</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)


with abas[1]:
    st.markdown("## 📊 Receita por Categoria")

    receita_cat = df.groupby("categoria", as_index=False)["valor_total"].sum()

    fig = px.bar(
        receita_cat,
        x="categoria",
        y="valor_total",
        color="categoria",
        color_discrete_map=CATEGORY_COLORS,
        title="Receita por Categoria"
    )
    plot(fig)


with abas[2]:
    st.markdown("## 📦 Estoque")

    estoque = df_produtos.copy()

    estoque["status"] = estoque.apply(
        lambda x: "Crítico" if x["estoque_atual"] <= x["estoque_minimo"]
        else "Atenção" if x["estoque_atual"] <= x["estoque_minimo"] * 1.5
        else "Saudável",
        axis=1
    )

    estoque["valor_estoque"] = estoque["estoque_atual"] * estoque["preco"]

    status_count = estoque["status"].value_counts().reset_index()
    status_count.columns = ["status", "quantidade"]

    ordem_status = ["Saudável", "Atenção", "Crítico"]
    status_count["status"] = pd.Categorical(
        status_count["status"],
        categories=ordem_status,
        ordered=True
    )
    status_count = status_count.sort_values("status")

    c1, c2, c3 = st.columns(3)
    c1.metric("Valor em Estoque", moeda(estoque["valor_estoque"].sum()))
    c2.metric("Produtos Críticos", len(estoque[estoque["status"] == "Crítico"]))
    c3.metric("SKUs", estoque["produto_id"].nunique())

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            status_count,
            x="status",
            y="quantidade",
            color="status",
            color_discrete_map=STATUS_COLORS,
            title="Status do Estoque"
        )
        plot(fig)

    with col2:
        fig = px.bar(
            estoque.sort_values("valor_estoque", ascending=False).head(10),
            x="valor_estoque",
            y="nome",
            orientation="h",
            color="categoria",
            color_discrete_map=CATEGORY_COLORS,
            title="Top 10 Valor Parado em Estoque"
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        plot(fig)

    st.dataframe(estoque, use_container_width=True)


with abas[3]:
    st.markdown("## 🧠 Inteligência Analítica")

    abc = df.groupby("nome", as_index=False)["valor_total"].sum()
    abc = abc.sort_values("valor_total", ascending=False)

    abc["percentual"] = abc["valor_total"] / abc["valor_total"].sum()
    abc["acumulado"] = abc["percentual"].cumsum()

    def classe_abc(x):
        if x <= 0.8:
            return "A - Alta relevância"
        elif x <= 0.95:
            return "B - Média relevância"
        return "C - Baixa relevância"

    abc["classe"] = abc["acumulado"].apply(classe_abc)

    abc_count = abc["classe"].value_counts().reset_index()
    abc_count.columns = ["classe_abc", "quantidade"]

    ordem_abc = [
        "A - Alta relevância",
        "B - Média relevância",
        "C - Baixa relevância"
    ]

    abc_count["classe_abc"] = pd.Categorical(
        abc_count["classe_abc"],
        categories=ordem_abc,
        ordered=True
    )
    abc_count = abc_count.sort_values("classe_abc")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            abc,
            x="nome",
            y="acumulado",
            markers=True,
            title="Curva ABC / Pareto",
            color_discrete_sequence=["#FBBF24"]
        )
        plot(fig)

    with col2:
        fig = px.bar(
            abc_count,
            x="classe_abc",
            y="quantidade",
            color="classe_abc",
            color_discrete_map=ABC_COLORS,
            title="Distribuição ABC"
        )
        plot(fig)

    st.markdown("### Recomendações Estratégicas")
    st.markdown("- Produtos da classe A devem ser priorizados em estoque e campanhas.")
    st.markdown("- Produtos da classe C devem ser avaliados para redução, reposicionamento ou promoção.")
    st.markdown("- Categorias com maior margem devem receber mais visibilidade comercial.")

    st.dataframe(abc, use_container_width=True)


with abas[4]:
    st.markdown("## 🤖 IA Analítica")

    st.markdown("""
    <div class="ai-card">
        <h3>Assistente de Decisão</h3>
        <p>
        Faça perguntas sobre receita, lucro, margem, estoque, produtos, clientes ou previsão.
        Esta IA usa regras analíticas sobre a base do projeto.
        </p>
    </div>
    """, unsafe_allow_html=True)

    pergunta = st.text_input(
        "Digite sua pergunta:",
        placeholder="Ex: Qual produto devo priorizar? Como está o estoque?"
    )

    if pergunta:
        resposta = resposta_ia(pergunta, contexto_ia)

        st.markdown(f"""
        <div class="warning-card">
            <h3>Resposta da IA</h3>
            <p>{resposta}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Perguntas sugeridas")
    st.markdown("- Qual foi a receita total?")
    st.markdown("- Como está a margem?")
    st.markdown("- Quais produtos devo priorizar?")
    st.markdown("- Como está o estoque?")
    st.markdown("- O que a previsão indica?")


with abas[5]:
    st.markdown("## 📈 Previsão de Receita")

    vendas_forecast = vendas_mes.copy()
    vendas_forecast = vendas_forecast.sort_values("mes")
    vendas_forecast["mes_num"] = range(len(vendas_forecast))

    coef = np.polyfit(
        vendas_forecast["mes_num"],
        vendas_forecast["valor_total"],
        1
    )

    trend = np.poly1d(coef)

    ultimo_mes = pd.to_datetime(vendas_forecast["mes"].iloc[-1] + "-01")

    futuro = pd.DataFrame({
        "mes": [
            (ultimo_mes + pd.DateOffset(months=i)).strftime("%Y-%m")
            for i in range(1, 4)
        ],
        "mes_num": range(len(vendas_forecast), len(vendas_forecast) + 3)
    })

    futuro["valor_total"] = trend(futuro["mes_num"])

    historico_plot = vendas_forecast[["mes", "valor_total"]].copy()
    historico_plot["tipo"] = "Histórico"

    futuro_plot = futuro[["mes", "valor_total"]].copy()
    futuro_plot["tipo"] = "Forecast"

    vendas_plot = pd.concat([historico_plot, futuro_plot], ignore_index=True)

    fig = px.line(
        vendas_plot,
        x="mes",
        y="valor_total",
        color="tipo",
        markers=True,
        title="Histórico vs Previsão de Receita",
        color_discrete_map={
            "Histórico": "#38BDF8",
            "Forecast": "#FBBF24"
        }
    )

    plot(fig)

    st.markdown("### Receita prevista para os próximos meses")
    st.dataframe(futuro_plot, use_container_width=True)


with abas[6]:
    st.markdown("## 🧪 Simulador Estratégico")

    aumento_vendas = st.slider("Aumento de vendas (%)", 0, 100, 10)
    aumento_ticket = st.slider("Aumento do ticket médio (%)", 0, 100, 5)

    receita_proj = receita * (1 + aumento_vendas / 100) * (1 + aumento_ticket / 100)
    ganho = receita_proj - receita

    c1, c2, c3 = st.columns(3)
    c1.metric("Receita Atual", moeda(receita))
    c2.metric("Receita Projetada", moeda(receita_proj))
    c3.metric("Ganho Estimado", moeda(ganho))


with abas[7]:
    st.markdown("## 📥 Base Analítica")

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Baixar base em CSV",
        data=csv,
        file_name="pulse_retail_base.csv",
        mime="text/csv"
    )


with abas[8]:
    st.markdown("## 📊 Qualidade dos Dados")

    total_registros = len(df)
    total_colunas = len(df.columns)
    periodo_inicio = df["data"].min().date()
    periodo_fim = df["data"].max().date()
    valores_nulos = df.isnull().sum().sum()
    duplicados = df.duplicated().sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros", total_registros)
    c2.metric("Colunas", total_colunas)
    c3.metric("Valores Nulos", valores_nulos)
    c4.metric("Duplicados", duplicados)

    st.markdown(f"**Período analisado:** {periodo_inicio} até {periodo_fim}")

    null_df = df.isnull().sum().reset_index()
    null_df.columns = ["coluna", "qtd_nulos"]
    null_df["percentual"] = (null_df["qtd_nulos"] / total_registros) * 100

    fig = px.bar(
        null_df,
        x="coluna",
        y="percentual",
        title="Percentual de Valores Nulos por Coluna",
        color="percentual",
        color_continuous_scale="Reds"
    )
    plot(fig)

    st.markdown("### Tabela de Qualidade")
    st.dataframe(
        null_df.sort_values("percentual", ascending=False),
        use_container_width=True
    )


with abas[9]:
    st.markdown("""
## ℹ️ Sobre o Projeto

Este projeto simula uma plataforma de **Decision Intelligence para varejo**, com foco em:

- Monitoramento de performance
- Receita e lucratividade
- Gestão de estoque
- Curva ABC / Pareto
- IA analítica simulada
- Simulação de cenários
- Previsão de receita
- Qualidade dos dados

### Stack utilizada

- Python
- Pandas
- Streamlit
- Plotly
- NumPy

### Objetivo

Transformar dados operacionais em decisões estratégicas.
""")

st.caption("Pulse | Retail Decision Intelligence")