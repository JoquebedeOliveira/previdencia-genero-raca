"""
Código (Python) – Análise de contribuição previdenciária por gênero e raça/cor
Entrada: data_processed/pnad_trabalho_2019_2022.csv
Colunas mínimas: ano, trimestre, peso, sexo, cor,
                 cond_ocupacao, contribui_prev, renda_trabalho
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Caminhos do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.dirname(BASE_DIR)
DATA_PROC = os.path.join(PROJ_DIR, "data_processed")
OUTPUTS = os.path.join(PROJ_DIR, "outputs")
os.makedirs(OUTPUTS, exist_ok=True)

# 1. Carregar base analítica e filtrar ocupados
df = pd.read_csv(os.path.join(DATA_PROC, "pnad_trabalho_2019_2022.csv"))
df = df[df["cond_ocupacao"].str.contains("ocupad", case=False, na=False)].copy()

# 2. Variáveis de gênero, raça/cor e grupo interseccional
df["mulher"] = df["sexo"].str.contains("Mulher", case=False, na=False).astype(int)
df["negro"] = df["cor"].str.contains("Preta|Parda", case=False, na=False).astype(int)

def grupo(row):
    if row["mulher"] == 0 and row["negro"] == 0:
        return "Homem branco"
    if row["mulher"] == 0 and row["negro"] == 1:
        return "Homem negro"
    if row["mulher"] == 1 and row["negro"] == 0:
        return "Mulher branca"
    if row["mulher"] == 1 and row["negro"] == 1:
        return "Mulher negra"
    return "Outro"

df["grupo_sexo_cor"] = df.apply(grupo, axis=1)

# 3. Desfecho: contribuição previdenciária
df["y_contribui"] = df["contribui_prev"].str.contains(
    "Contribuinte|Contribui|Sim", case=False, na=False
).astype(int)

# 4. Renda, peso, log-renda e interação
df["renda_trabalho"] = df["renda_trabalho"].clip(lower=1)
df["log_renda"] = np.log(df["renda_trabalho"])
df["peso"] = df["peso"].astype(float)
df["interacao_mulher_negro"] = df["mulher"] * df["negro"]

# 5. Proporção ponderada por grupo sexo x cor
def prop_pond(g):
    return (g["y_contribui"] * g["peso"]).sum() / g["peso"].sum()

tab = (
    df.groupby("grupo_sexo_cor")[["y_contribui", "peso"]]
      .apply(prop_pond)
      .rename("prop_contribui")
      .reset_index()
)
tab.to_csv(os.path.join(OUTPUTS, "tabela_prop_contribuicao.csv"), index=False)

# 6. Gráfico de barras
plt.figure(figsize=(6, 4))
plt.bar(tab["grupo_sexo_cor"], tab["prop_contribui"])
plt.ylabel("Proporção que contribui para a previdência")
plt.xlabel("Grupo de sexo e cor/raça")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, "grafico_contribuicao_sexo_cor.png"), dpi=300)
plt.close()

# 7. Modelo LPM ponderado (WLS) com erros robustos
cols_x = ["mulher", "negro", "interacao_mulher_negro", "log_renda"]
dfm = df[cols_x + ["y_contribui", "peso"]].replace([np.inf, -np.inf], np.nan).dropna()

X = sm.add_constant(dfm[cols_x])
y = dfm["y_contribui"]
w = dfm["peso"]

modelo = sm.WLS(y, X, weights=w).fit(cov_type="HC1")
resumo = pd.DataFrame({"coef": modelo.params, "se_robusto": modelo.bse})
resumo.to_csv(
    os.path.join(OUTPUTS, "resultados_lpm_previdencia.csv"),
    index_label="variavel"
)
