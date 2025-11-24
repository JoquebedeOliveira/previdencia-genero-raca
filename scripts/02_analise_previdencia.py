"""
Script 02_analise_previdencia.py
Objetivo: analisar desigualdades de gênero e raça na contribuição previdenciária
usando PNAD Contínua REAL (CSV baixado do BigQuery / Base dos Dados).

Entrada esperada:
    data_processed/pnad_trabalho_2019_2022.csv

Colunas mínimas necessárias:
    ano, trimestre, peso, sexo, cor, cond_ocupacao, contribui_prev, renda_trabalho
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

np.random.seed(42)

# -------------------------------------------------------------------
# Configuração de caminhos
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PROC = os.path.join(BASE_DIR, "data_processed")
OUTPUTS = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS, exist_ok=True)

# -------------------------------------------------------------------
# Função auxiliar para salvar CSV com segurança
# -------------------------------------------------------------------
def salvar_csv_seguro(df, caminho, **kwargs):
    """
    Tenta salvar um DataFrame em CSV.
    - Cria o diretório, se necessário.
    - Se o arquivo já existir e não estiver sendo usado, remove antes.
    - Se estiver aberto em outro programa (Excel), avisa claramente.
    """
    diretorio = os.path.dirname(caminho)
    os.makedirs(diretorio, exist_ok=True)

    if os.path.exists(caminho):
        try:
            os.remove(caminho)
        except PermissionError:
            print(
                f"⚠️ Não consegui remover '{caminho}'. "
                "Feche o arquivo se ele estiver aberto (por exemplo, no Excel) "
                "e rode o script novamente."
            )
            raise

    df.to_csv(caminho, **kwargs)

# -------------------------------------------------------------------
# 1. Carregar dados
# -------------------------------------------------------------------
csv_path = os.path.join(DATA_PROC, "pnad_trabalho_2019_2022.csv")
df = pd.read_csv(csv_path)

print("Colunas do arquivo:", df.columns.tolist())
print("Número de linhas bruto:", len(df))

# -------------------------------------------------------------------
# 2. Criar variável 'ocupado' e filtrar população de interesse
# -------------------------------------------------------------------
df["ocupado"] = df["cond_ocupacao"].str.contains(
    "ocupad", case=False, na=False
).astype(int)

df = df[df["ocupado"] == 1].copy()
print("Após filtrar ocupados:", len(df))

# -------------------------------------------------------------------
# 3. Variáveis de gênero, raça/cor e grupo interseccional
# -------------------------------------------------------------------
df["mulher"] = df["sexo"].str.contains(
    "Mulher", case=False, na=False
).astype(int)

df["negro"] = df["cor"].str.contains(
    "Preta|Parda", case=False, na=False
).astype(int)

def classificar_sexo_cor(row):
    if row["mulher"] == 0 and row["negro"] == 0:
        return "Homem branco"
    if row["mulher"] == 0 and row["negro"] == 1:
        return "Homem negro"
    if row["mulher"] == 1 and row["negro"] == 0:
        return "Mulher branca"
    if row["mulher"] == 1 and row["negro"] == 1:
        return "Mulher negra"
    return "Outro"

df["grupo_sexo_cor"] = df.apply(classificar_sexo_cor, axis=1)

# -------------------------------------------------------------------
# 4. Desfecho: contribuição previdenciária
# -------------------------------------------------------------------
df["y_contribui"] = df["contribui_prev"].str.contains(
    "Contribuinte|Contribui|Sim", case=False, na=False
).astype(int)

# -------------------------------------------------------------------
# 5. Renda, peso amostral e log-renda
# -------------------------------------------------------------------
df["renda_trabalho"] = df["renda_trabalho"].clip(lower=1)
df["log_renda"] = np.log(df["renda_trabalho"])
df["peso"] = df["peso"].astype(float)

# -------------------------------------------------------------------
# 6. Estatísticas descritivas ponderadas
# -------------------------------------------------------------------
def proporcao_ponderada(y, w):
    return (y * w).sum() / w.sum()

tab_descritiva = (
    df.groupby("grupo_sexo_cor", group_keys=False)[["y_contribui", "peso"]]
      .apply(lambda g: proporcao_ponderada(g["y_contribui"], g["peso"]))
      .rename("prop_contribui")
      .reset_index()
)

print("Proporção de contribuintes por grupo sexo x cor (ponderada):")
print(tab_descritiva)

tabela_path = os.path.join(OUTPUTS, "tabela_prop_contribuicao.csv")
salvar_csv_seguro(tab_descritiva, tabela_path, index=False)

# -------------------------------------------------------------------
# 7. Gráfico de barras
# -------------------------------------------------------------------
plt.figure(figsize=(8, 5))
plt.bar(tab_descritiva["grupo_sexo_cor"], tab_descritiva["prop_contribui"])
plt.ylabel("Proporção que contribui para a previdência")
plt.xlabel("Grupo de sexo e cor/raça")
plt.title("Contribuição previdenciária entre ocupados, por sexo e cor/raça")
plt.xticks(rotation=20)
plt.tight_layout()

grafico_path = os.path.join(OUTPUTS, "grafico_contribuicao_sexo_cor.png")
plt.savefig(grafico_path, dpi=300)
plt.close()

print(f"Gráfico salvo em: {grafico_path}")

# -------------------------------------------------------------------
# 8. Modelo LPM ponderado (WLS)
# -------------------------------------------------------------------
df["interacao_mulher_negro"] = df["mulher"] * df["negro"]

cols_reg = ["mulher", "negro", "interacao_mulher_negro", "log_renda"]
if "idade" in df.columns:
    cols_reg.insert(3, "idade")  # insere idade antes de log_renda

# Montar base do modelo e remover NaN / inf em exog e peso
cols_necessarias = cols_reg + ["y_contribui", "peso"]
df_model = df[cols_necessarias].copy()

df_model = df_model.replace([np.inf, -np.inf], np.nan).dropna()

print("Observações usadas no modelo (após remover NaN/inf):", len(df_model))

X = df_model[cols_reg].copy()
X = sm.add_constant(X)

y = df_model["y_contribui"]
w = df_model["peso"]

modelo_lpm = sm.WLS(y, X, weights=w)
resultado_lpm = modelo_lpm.fit(cov_type="HC1")

print(resultado_lpm.summary())

resumo = pd.DataFrame({
    "coef": resultado_lpm.params,
    "se_robusto": resultado_lpm.bse
})

lpm_path = os.path.join(OUTPUTS, "resultados_lpm_previdencia.csv")
salvar_csv_seguro(resumo, lpm_path, index_label="variavel")

print("Análise concluída. Resultados salvos na pasta 'outputs/'.")
