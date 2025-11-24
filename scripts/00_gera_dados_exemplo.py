"""
Script 00_gera_dados_exemplo.py
Objetivo: gerar um conjunto de dados FICTÍCIO com a mesma estrutura
que vamos usar na análise, para testar o pipeline.
"""

import os
import numpy as np
import pandas as pd

np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PROC = os.path.join(BASE_DIR, "data_processed")
os.makedirs(DATA_PROC, exist_ok=True)

# Tamanho do exemplo (poucas linhas, só pra testar)
n = 1000

# Gerar variáveis simples
sexo = np.random.choice([1, 2], size=n)               # 1=homem, 2=mulher
cor = np.random.choice([1, 2, 3], size=n)             # 1=branca, 2=preta, 3=parda
idade = np.random.randint(18, 65, size=n)
renda_trabalho = np.random.lognormal(mean=7, sigma=0.7, size=n)  # valores positivos
peso = np.random.uniform(0.5, 3.0, size=n)            # pesos amostrais fictícios

# Probabilidade "fake" de contribuir (só pra ter padrão desigual)
base_prob = 0.7
prob = (
    base_prob
    - 0.10 * (sexo == 2)          # mulheres um pouco menos
    - 0.10 * (cor != 1)           # pessoas negras um pouco menos
)

contribui_prev = np.random.binomial(1, np.clip(prob, 0.05, 0.95), size=n)

df = pd.DataFrame({
    "ano": np.random.choice([2019, 2022], size=n),
    "ocupado": 1,
    "contribui_prev": contribui_prev,
    "sexo": sexo,
    "cor": cor,
    "idade": idade,
    "renda_trabalho": renda_trabalho,
    "peso": peso,
})

saida_csv = os.path.join(DATA_PROC, "pnad_trabalho_2019_2022.csv")
df.to_csv(saida_csv, index=False)

print(f"Arquivo de exemplo criado em: {saida_csv}")
