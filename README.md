# Desigualdades de gênero e raça/cor na contribuição previdenciária no Brasil 📊

Repositório do projeto de pesquisa **“Desigualdades de gênero e raça/cor na contribuição previdenciária entre pessoas ocupadas no Brasil”**, desenvolvido a partir de microdados da **PNAD Contínua (IBGE)**, acessados via **Base dos Dados / BigQuery** e analisados em **Python**.

O objetivo é montar um **pipeline reprodutível** para medir desigualdades na **probabilidade de contribuição previdenciária** entre homens e mulheres, brancos e negros, com foco na penalidade interseccional de **mulheres negras**.

---

## 1. Pergunta de pesquisa

> Entre pessoas **ocupadas** no Brasil, há desigualdades na probabilidade de contribuição previdenciária associadas à combinação de gênero e cor/raça, em especial para mulheres negras, quando comparadas a homens brancos?

---

## 2. Dados e variáveis

- **Fonte:** PNAD Contínua (IBGE), microdados.  
- **Período analisado:** 4º trimestre de **2019** e 4º trimestre de **2022**.  
- **Acesso:** tabela `basedosdados.br_ibge_pnadc.microdados` no BigQuery, com junção ao dicionário `basedosdados.br_ibge_pnadc.dicionario`.  
- **Unidade de análise:** pessoas de 14 anos ou mais, **ocupadas** na semana de referência.  
- **Ponderação:** fator de expansão da pessoa **V1028**.

O arquivo analítico final é um CSV chamado:
data_processed/pnad_trabalho_2019_2022.csv

**com as colunas principais:**
    ano – ano de referência (2019, 2022);
    trimestre – trimestre (restrito ao valor 4);
    peso – fator de expansão (V1028);
    sexo – rótulo textual (ex.: “Homem”, “Mulher”);
    cor – rótulo textual (ex.: “Branca”, “Preta”, “Parda”);
    cond_ocupacao – condição de ocupação (ex.: “Pessoas ocupadas”);
    contribui_prev – situação de contribuição à previdência;
    renda_trabalho – rendimento mensal habitual em todos os trabalhos (VD4019).

**As variáveis analíticas são construídas em Python (ver script scripts/02_analise_previdencia.py):**
    ocupado (dummy)
    mulher, negro (dummies)
    grupo_sexo_cor (Homem branco / Homem negro / Mulher branca / Mulher negra)
    y_contribui (dummy de contribuição previdenciária)
    log_renda (log da renda de trabalho)
    interacao_mulher_negro (efeito interseccional)
--

## 3. Estrutura do repositório

projeto_previdencia_genero_raca/
├── data_raw/                         # (opcional) arquivos originais, zips etc.
├── data_processed/
│   └── pnad_trabalho_2019_2022.csv   # base analítica pronta para uso
├── outputs/
│   ├── tabela_prop_contribuicao.csv  # tabela de proporções ponderadas
│   ├── grafico_contribuicao_sexo_cor.png
│   └── resultados_lpm_previdencia.csv
├── scripts/
│   └── 02_analise_previdencia.py     # script principal de análise
├── sql/
│   └── pnad_trabalho_2019_2022.sql   # consulta SQL usada no BigQuery
├── requirements.txt
└── README.md

## 4. Pré-requisitos

    Python 3.9+
    Conta no Google Cloud com acesso ao BigQuery
    Acesso ao projeto público basedosdados no BigQuery
**Bibliotecas Python (instaladas via requirements.txt)**:
    pandas
    numpy
    statsmodels
    matplotlib

## 5. Passo a passo para executar o projeto
## 5.1. Clonar o repositório

git clone https://github.com/<seu-usuario>/<seu-repo>.git
cd <seu-repo>
 
## 5.2. Criar e ativar ambiente virtual

**Windows (PowerShell):**
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1

**Linux / macOS (bash/zsh):**
    python -m venv .venv
    source .venv/bin/activate

## 5.3. Instalar dependências
   
    pip install -r requirements.txt

## 5.4. Gerar o CSV da PNAD no BigQuery
    **1.** Acesse o Console do Google Cloud → BigQuery.
    **2.**Selecione seu projeto (ex.: pnad-prev-genero-raca).
    **3.**Abra o Editor SQL.
    **4.**Copie o conteúdo de sql/pnad_trabalho_2019_2022.sql para o editor.
        A consulta realiza:
            junção com o dicionário da PNAD (br_ibge_pnadc.dicionario);
            seleção de 2019 e 2022, 4º trimestre;
            seleção das variáveis relevantes.
    **5.**Clique em Executar.
    **6.**Após a execução, clique em Salvar resultados (Save results) → Download → CSV.
    **7.**Salve o arquivo como:
        pnad_trabalho_2019_2022.csv
    **8.**Coloque o arquivo na pasta:
        data_processed/pnad_trabalho_2019_2022.csv

## 5.5. Rodar a análise em Python
    **Com o ambiente virtual ativo:**
        python scripts/02_analise_previdencia.py

**Esse script:**
    **1.**Carrega data_processed/pnad_trabalho_2019_2022.csv;
    **2.**Filtra apenas pessoas ocupadas;
    **3.**Cria as dummies mulher, negro, grupo_sexo_cor, y_contribui, log_renda;
    **4.**Calcula a proporção ponderada de contribuintes por grupo de sexo/cor;
    **5.**Gera:
        outputs/tabela_prop_contribuicao.csv
        outputs/grafico_contribuicao_sexo_cor.png
    **6.**Estima um modelo de probabilidade linear (LPM) ponderado e salva:
        outputs/resultados_lpm_previdencia.csv

## 6. Resultados principais
A partir da PNAD Contínua 2019/2022 (4º tri), entre pessoas ocupadas:

| Grupo         | Proporção que contribui (ponderada) |
| ------------- | ----------------------------------- |
| Homem branco  | ~0,94                               |
| Homem negro   | ~0,91                               |
| Mulher branca | ~0,91                               |
| Mulher negra  | ~0,86                               |

O gráfico gerado outputs/grafico_contribuicao_sexo_cor.png resume essas diferenças:

![Gráfico: contribuição previdenciária por sexo e cor/raça entre pessoas ocupadas](outputs/grafico_contribuicao_sexo_cor.png)

As proporções que contribuem para a previdência são aproximadamente 94% para homens brancos, 91% para mulheres brancas, 91% para homens negros e 86% para mulheres negras. O grupo de mulheres negras apresenta a menor taxa de contribuição.
Mesmo entre pessoas ocupadas, mulheres negras apresentam a menor probabilidade de contribuição previdenciária, com diferença de aproximadamente 8–9 pontos percentuais em relação a homens brancos, sugerindo uma vulnerabilidade interseccional na cobertura previdenciária.

O arquivo outputs/resultados_lpm_previdencia.csv traz os coeficientes e erros-padrão robustos do LPM ponderado, permitindo quantificar a penalidade específica de mulheres negras após controle por renda (e idade, se incluída).

## 7. Reprodutibilidade e transparência

Este projeto busca seguir boas práticas de ciência de dados aplicada a políticas públicas:

    ✅ Separação de etapas: extração (sql/), preparação (data_processed/) e análise (scripts/).
    ✅ Reprodutibilidade: um único comando (python scripts/02_analise_previdencia.py) reproduz as principais tabelas e gráficos a partir do CSV de entrada.
    ✅ Documentação: este README explica todas as etapas necessárias para replicar os resultados.
    ✅ Proteção de dados: apenas microdados públicos e anonimizados do IBGE são utilizados; nenhum dado individual identificável é versionado neste repositório.

## 8. Como citar

Sugestão de citação (ajuste com seu nome e ano):

    SILVA, Joquebede O. Teles da. Desigualdades de gênero e raça/cor na contribuição previdenciária entre pessoas ocupadas no Brasil. Repositório GitHub, ano. Disponível em: <link do repositório>. Acesso em: dd mmm. aaaa.
