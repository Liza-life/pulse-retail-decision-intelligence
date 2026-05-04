import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker("pt_BR")
random.seed(42)

# =====================================================
# PRODUTOS REALISTAS
# =====================================================
produtos_base = [
    ("Arroz 5kg", "Alimentos", 28.90, 0.22),
    ("Feijão Carioca 1kg", "Alimentos", 8.90, 0.25),
    ("Açúcar 1kg", "Alimentos", 5.20, 0.18),
    ("Café 500g", "Alimentos", 18.90, 0.30),
    ("Macarrão 500g", "Alimentos", 4.90, 0.22),
    ("Óleo de Soja 900ml", "Alimentos", 7.80, 0.18),
    ("Leite Integral 1L", "Bebidas", 5.60, 0.20),
    ("Refrigerante 2L", "Bebidas", 9.50, 0.28),
    ("Suco Natural 1L", "Bebidas", 12.90, 0.35),
    ("Água Mineral 1,5L", "Bebidas", 3.20, 0.25),
    ("Cerveja Lata 350ml", "Bebidas", 4.50, 0.32),
    ("Detergente 500ml", "Limpeza", 2.80, 0.35),
    ("Sabão em Pó 1kg", "Limpeza", 14.90, 0.30),
    ("Desinfetante 2L", "Limpeza", 8.50, 0.33),
    ("Água Sanitária 1L", "Limpeza", 4.20, 0.28),
    ("Papel Higiênico 12un", "Higiene", 18.90, 0.27),
    ("Shampoo 350ml", "Higiene", 16.90, 0.40),
    ("Condicionador 350ml", "Higiene", 17.90, 0.38),
    ("Creme Dental 90g", "Higiene", 6.50, 0.35),
    ("Sabonete 90g", "Higiene", 3.20, 0.32),
    ("Frango Congelado 1kg", "Carnes", 16.90, 0.22),
    ("Carne Bovina 1kg", "Carnes", 42.90, 0.25),
    ("Linguiça Toscana 1kg", "Carnes", 24.90, 0.28),
    ("Queijo Mussarela 500g", "Frios", 22.90, 0.30),
    ("Presunto 500g", "Frios", 18.90, 0.28),
    ("Iogurte 1L", "Laticínios", 9.90, 0.30),
    ("Manteiga 200g", "Laticínios", 12.50, 0.32),
    ("Ovos 12un", "Hortifruti", 13.90, 0.24),
    ("Banana 1kg", "Hortifruti", 6.90, 0.35),
    ("Tomate 1kg", "Hortifruti", 8.90, 0.30),
]

fornecedores = [
    "Distribuidora Alpha",
    "Atacado Brasil",
    "Mega Foods",
    "Fresh Market",
    "Higiene Prime",
    "Bebidas São Paulo",
]

formas_pagamento = ["Crédito", "Débito", "Pix", "Dinheiro"]

# =====================================================
# TABELA PRODUTOS
# =====================================================
produtos = []

for i, item in enumerate(produtos_base, start=1):
    nome, categoria, preco, margem = item
    produtos.append({
        "produto_id": i,
        "nome": nome,
        "categoria": categoria,
        "preco": preco,
        "custo": round(preco * (1 - margem), 2),
        "margem_percentual": margem,
        "fornecedor": random.choice(fornecedores),
        "estoque_atual": random.randint(20, 250),
        "estoque_minimo": random.randint(15, 60)
    })

df_produtos = pd.DataFrame(produtos)

# =====================================================
# CLIENTES
# =====================================================
clientes = []

for i in range(1, 301):
    clientes.append({
        "cliente_id": i,
        "nome_cliente": fake.name(),
        "cidade": random.choice(["São Paulo", "Osasco", "Barueri", "Guarulhos", "Santo André"]),
        "tipo_cliente": random.choice(["Novo", "Recorrente", "VIP"])
    })

df_clientes = pd.DataFrame(clientes)

# =====================================================
# VENDAS COM SAZONALIDADE
# =====================================================
vendas = []
data_inicio = datetime.today() - timedelta(days=240)

for venda_id in range(1, 2501):
    data_venda = data_inicio + timedelta(days=random.randint(0, 240))
    mes = data_venda.month

    # sazonalidade simples
    fator_sazonal = 1.0
    if mes in [11, 12]:
        fator_sazonal = 1.35
    elif mes in [1, 2]:
        fator_sazonal = 0.85
    elif mes in [4, 5]:
        fator_sazonal = 0.75

    produto = random.choice(produtos)
    cliente = random.choice(clientes)

    quantidade = max(1, int(random.randint(1, 5) * fator_sazonal))
    valor_total = round(produto["preco"] * quantidade, 2)
    custo_total = round(produto["custo"] * quantidade, 2)
    lucro = round(valor_total - custo_total, 2)

    vendas.append({
        "venda_id": venda_id,
        "data": data_venda.date(),
        "cliente_id": cliente["cliente_id"],
        "produto_id": produto["produto_id"],
        "quantidade": quantidade,
        "valor_total": valor_total,
        "custo_total": custo_total,
        "lucro": lucro,
        "forma_pagamento": random.choice(formas_pagamento),
        "canal_venda": random.choice(["Loja Física", "Delivery", "App", "Marketplace"])
    })

df_vendas = pd.DataFrame(vendas)

# =====================================================
# SALVAR
# =====================================================
df_produtos.to_csv("../data/produtos.csv", index=False)
df_clientes.to_csv("../data/clientes.csv", index=False)
df_vendas.to_csv("../data/vendas.csv", index=False)

print("Dados realistas gerados com sucesso!")
print("Arquivos criados:")
print("- data/produtos.csv")
print("- data/clientes.csv")
print("- data/vendas.csv")