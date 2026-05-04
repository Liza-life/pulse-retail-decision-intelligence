import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

st.set_page_config(
    page_title="Pulse | Retail Decision Intelligence",
    layout="wide"
)

# =====================================================
# CORES
# =====================================================
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

# =====================================================
# FUNÇÃO DE DADOS (CORRIGIDA PARA CLOUD)
# =====================================================
@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.dirname(__file__))

    vendas = pd.read_csv(os.path.join(base_path, "data", "vendas.csv"))
    produtos = pd.read_csv(os.path.join(base_path, "data", "produtos.csv"))
    clientes = pd.read_csv(os.path.join(base_path, "data", "clientes.csv"))

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
        font_color="#F8FAFC"
    )
    st.plotly_chart(fig, use_container_width=True)


# =====================================================
# IA SIMULADA
# =====================================================
def resposta_ia(pergunta, ctx):
    p = pergunta.lower()

    if "receita" in p:
        return f"A receita total foi {moeda(ctx['receita'])}."

    if "lucro" in p:
        return f"O lucro foi {moeda(ctx['lucro'])} com margem de {ctx['margem']:.1%}."

    if "estoque" in p:
        return f"Existem {ctx['criticos']} produtos em estado crítico."

    if "produto" in p:
        return f"O produto destaque é {ctx['top_produto']}."

    return "Analise receita, margem e estoque para melhores decisões."


# =====================================================
# LOAD
# =====================================================
df, df_produtos = load_data()

receita = df["valor_total"].sum()
lucro = df["lucro"].sum()
margem = lucro / receita
clientes = df["cliente_id"].nunique()

vendas_mes = df.groupby("mes", as_index=False)["valor_total"].sum()

top_produto = (
    df.groupby("nome")["valor_total"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
)

estoque_tmp = df_produtos.copy()
estoque_tmp["status"] = estoque_tmp.apply(
    lambda x: "Crítico" if x["estoque_atual"] <= x["estoque_minimo"]
    else "Atenção" if x["estoque_atual"] <= x["estoque_minimo"] * 1.5
    else "Saudável",
    axis=1
)

ctx = {
    "receita": receita,
    "lucro": lucro,
    "margem": margem,
    "top_produto": top_produto,
    "criticos": len(estoque_tmp[estoque_tmp["status"] == "Crítico"])
}

# =====================================================
# HEADER
# =====================================================
st.title("🧠 Pulse | Retail Decision Intelligence")

# =====================================================
# ABAS
# =====================================================
tabs = st.tabs([
    "📊 Executivo",
    "📦 Estoque",
    "🧠 Inteligência",
    "🤖 IA",
    "📈 Forecast",
    "📊 Qualidade"
])

# =====================================================
# EXECUTIVO
# =====================================================
with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Receita", moeda(receita))
    c2.metric("Lucro", moeda(lucro))
    c3.metric("Margem", f"{margem:.1%}")
    c4.metric("Clientes", clientes)

    fig = px.area(vendas_mes, x="mes", y="valor_total")
    plot(fig)

# =====================================================
# ESTOQUE
# =====================================================
with tabs[1]:
    estoque = df_produtos.copy()

    estoque["status"] = estoque_tmp["status"]
    status = estoque["status"].value_counts().reset_index()
    status.columns = ["status", "qtd"]

    fig = px.bar(
        status,
        x="status",
        y="qtd",
        color="status",
        color_discrete_map=STATUS_COLORS
    )
    plot(fig)

# =====================================================
# ABC
# =====================================================
with tabs[2]:
    abc = df.groupby("nome")["valor_total"].sum().reset_index()
    abc = abc.sort_values("valor_total", ascending=False)

    abc["acumulado"] = abc["valor_total"].cumsum() / abc["valor_total"].sum()

    def cls(x):
        if x <= 0.8:
            return "A - Alta relevância"
        elif x <= 0.95:
            return "B - Média relevância"
        return "C - Baixa relevância"

    abc["classe"] = abc["acumulado"].apply(cls)

    abc_count = abc["classe"].value_counts().reset_index()
    abc_count.columns = ["classe", "qtd"]

    fig = px.bar(
        abc_count,
        x="classe",
        y="qtd",
        color="classe",
        color_discrete_map=ABC_COLORS
    )
    plot(fig)

# =====================================================
# IA
# =====================================================
with tabs[3]:
    pergunta = st.text_input("Pergunte algo:")

    if pergunta:
        st.success(resposta_ia(pergunta, ctx))

# =====================================================
# FORECAST
# =====================================================
with tabs[4]:
    vendas_mes = vendas_mes.sort_values("mes")
    vendas_mes["idx"] = range(len(vendas_mes))

    coef = np.polyfit(vendas_mes["idx"], vendas_mes["valor_total"], 1)
    trend = np.poly1d(coef)

    futuro = pd.DataFrame({
        "idx": range(len(vendas_mes), len(vendas_mes) + 3)
    })

    futuro["valor_total"] = trend(futuro["idx"])
    futuro["mes"] = [f"Futuro {i}" for i in range(1, 4)]

    hist = vendas_mes.copy()
    hist["tipo"] = "Histórico"

    futuro["tipo"] = "Forecast"

    plot_df = pd.concat([hist, futuro])

    fig = px.line(plot_df, x="mes", y="valor_total", color="tipo")
    plot(fig)

# =====================================================
# QUALIDADE
# =====================================================
with tabs[5]:
    st.metric("Registros", len(df))
    st.metric("Colunas", len(df.columns))
    st.metric("Nulos", df.isnull().sum().sum())
    st.metric("Duplicados", df.duplicated().sum())

    nulls = df.isnull().sum().reset_index()
    nulls.columns = ["coluna", "qtd"]

    fig = px.bar(nulls, x="coluna", y="qtd")
    plot(fig)