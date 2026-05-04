import pandas as pd

# ------------------------
# CARREGAR DADOS
# ------------------------
df_vendas = pd.read_csv("../data/vendas.csv")
df_produtos = pd.read_csv("../data/produtos.csv")

# ------------------------
# TRATAMENTOS
# ------------------------
df_vendas["data"] = pd.to_datetime(df_vendas["data"])

# juntar dados
df = df_vendas.merge(df_produtos, on="produto_id")

# ------------------------
# MÉTRICAS
# ------------------------

# Receita total
receita_total = df["valor_total"].sum()

# Ticket médio
ticket_medio = df["valor_total"].mean()

# Produtos mais vendidos
top_produtos = df.groupby("nome")["quantidade"].sum().sort_values(ascending=False).head(5)

# Vendas por mês
df["mes"] = df["data"].dt.to_period("M")
vendas_mes = df.groupby("mes")["valor_total"].sum()

# ------------------------
# PRINTS (INSIGHTS)
# ------------------------

print("\n📊 RESUMO DO NEGÓCIO\n")

print(f"💰 Receita Total: R$ {receita_total:,.2f}")
print(f"🧾 Ticket Médio: R$ {ticket_medio:,.2f}")

print("\n🏆 Top 5 Produtos Mais Vendidos:")
print(top_produtos)

print("\n📅 Vendas por Mês:")
print(vendas_mes)