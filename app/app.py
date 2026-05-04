import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

st.set_page_config(page_title="Pulse | Retail Decision Intelligence", layout="wide")

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
# LOAD DATA (CORRIGIDO PARA CLOUD)
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
# LOAD
# =====================================================
df, df_produtos = load_data()

receita = df["valor_total"].sum()
lucro = df["lucro"].sum()
margem = lucro / receita
clientes = df["cliente_id"].nunique()

vendas_mes = df.groupby("mes", as_index=False)["valor_total"].sum()

# =====================================================
# HEADER
# =====================================================
st.markdown("# 🧠 Pulse | Retail Decision Intelligence")

# =====================================================
# ABAS
# =====================================================
tabs = st.tabs([
    "📊 Executivo",
    "📈 Receita",
    "📦 Estoque",
    "🧠 Inteligência",
    "🤖 IA Analítica",
    "📉 Forecast",
    "🧪 Simulador",
    "📊 Qualidade",
    "ℹ️ Sobre"
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
# RECEITA
# =====================================================
with tabs[1]:
    receita_cat = df.groupby("categoria", as_index=False)["valor_total"].sum()

    fig = px.bar(
        receita_cat,
        x="categoria",
        y="valor_total",
        color="categoria",
        color_discrete_map=CATEGORY_COLORS
    )
    plot(fig)

# =====================================================
# ESTOQUE
# =====================================================
with tabs[2]:
    estoque = df_produtos.copy()

    estoque["status"] = estoque.apply(
        lambda x: "Crítico" if x["estoque_atual"] <= x["estoque_minimo"]
        else "Atenção" if x["estoque_atual"] <= x["estoque_minimo"] * 1.5
        else "Saudável",
        axis=1
    )

    estoque["valor_estoque"] = estoque["estoque_atual"] * estoque["preco"]

    status_count = estoque["status"].value_counts().reset_index()
    status_count.columns = ["status", "qtd"]

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            status_count,
            x="status",
            y="qtd",
            color="status",
            color_discrete_map=STATUS_COLORS
        )
        plot(fig)

    with col2:
        fig = px.bar(
            estoque.sort_values("valor_estoque", ascending=False).head(10),
            x="valor_estoque",
            y="nome",
            orientation="h",
            color="categoria",
            color_discrete_map=CATEGORY_COLORS
        )
        plot(fig)

# =====================================================
# INTELIGÊNCIA (ABC)
# =====================================================
with tabs[3]:
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
# IA ANALÍTICA
# =====================================================
with tabs[4]:
    pergunta = st.text_input("Pergunte algo sobre os dados:")

    if pergunta:
        if "receita" in pergunta.lower():
            st.success(f"A receita foi {moeda(receita)}")
        elif "lucro" in pergunta.lower():
            st.success(f"O lucro foi {moeda(lucro)}")
        elif "estoque" in pergunta.lower():
            st.success("Existem itens críticos que precisam reposição")
        else:
            st.info("Analise receita, lucro, estoque e produtos")

# =====================================================
# FORECAST
# =====================================================
with tabs[5]:
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
# SIMULADOR
# =====================================================
with tabs[6]:
    aumento = st.slider("Aumento de vendas (%)", 0, 100, 10)
    nova_receita = receita * (1 + aumento / 100)
    st.metric("Receita Projetada", moeda(nova_receita))

# =====================================================
# QUALIDADE
# =====================================================
with tabs[7]:
    st.metric("Registros", len(df))
    st.metric("Colunas", len(df.columns))
    st.metric("Nulos", df.isnull().sum().sum())
    st.metric("Duplicados", df.duplicated().sum())

    nulls = df.isnull().sum().reset_index()
    nulls.columns = ["coluna", "qtd"]

    fig = px.bar(nulls, x="coluna", y="qtd")
    plot(fig)

# =====================================================
# SOBRE
# =====================================================
with tabs[8]:
    st.markdown("""
    Plataforma de Decision Intelligence para varejo.

    Inclui:
    - Receita e lucro
    - Estoque
    - Curva ABC
    - Forecast
    - IA analítica
    - Qualidade de dados
    """)

st.caption("Pulse | Retail Decision Intelligence")