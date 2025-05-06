import altair as alt
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(page_title="Análise de Exportação de Vinhos", page_icon="🍇")
st.title("🍇 Análise de Exportação de Vinhos")
st.write("""
    Esta aplicação visualiza dados de exportação de vinhos por país e ano.
    Você pode explorar a evolução da quantidade e do valor exportado ao longo do tempo.
""")

@st.cache_data
def load_data():
    df = pd.read_csv("data/ExpVinho.csv", sep=';', encoding='utf-8')

    # Renomear colunas
    novos_nomes = {}
    for col in df.columns:
        if '.' in col:
            ano, _ = col.split('.')
            novos_nomes[col] = f"{ano} valor"
        elif col.isdigit():
            novos_nomes[col] = f"{col} qtde (kg)"
    df.rename(columns=novos_nomes, inplace=True)

    # Verifica e padroniza nomes das colunas-chave
    if 'País' not in df.columns:
        pais_col = [col for col in df.columns if 'país' in col.lower()]
        if pais_col:
            df.rename(columns={pais_col[0]: 'País'}, inplace=True)
    if 'Id' not in df.columns:
        id_col = [col for col in df.columns if 'id' in col.lower()]
        if id_col:
            df.rename(columns={id_col[0]: 'Id'}, inplace=True)

    # Filtrar colunas de interesse
    anos_interesse = list(range(2009, 2025))
    colunas_interesse = []
    for ano in anos_interesse:
        colunas_interesse.append(f"{ano} qtde (kg)")
        colunas_interesse.append(f"{ano} valor")
    colunas_final = ['Id', 'País'] + [col for col in colunas_interesse if col in df.columns]

    return df[[col for col in colunas_final if col in df.columns]]


df = load_data()

# Widget de seleção de país
paises = st.multiselect("Selecione os países:", df["País"].unique().tolist(), default=["Estados Unidos", "China", "Angola"])

# Filtrar DataFrame
df_filtrado = df[df["País"].isin(paises)]

# Converter dados para formato longo (long format)
df_long_qtde = df_filtrado.melt(id_vars=["País"], 
                                 value_vars=[col for col in df.columns if "qtde (kg)" in col],
                                 var_name="Ano", 
                                 value_name="Quantidade (kg)")
df_long_qtde["Ano"] = df_long_qtde["Ano"].str.extract(r'(\d{4})').astype(int)

df_long_valor = df_filtrado.melt(id_vars=["País"], 
                                  value_vars=[col for col in df.columns if "valor" in col],
                                  var_name="Ano", 
                                  value_name="Valor")
df_long_valor["Ano"] = df_long_valor["Ano"].str.extract(r'(\d{4})').astype(int)

# Unir quantidade e valor
df_long = pd.merge(df_long_qtde, df_long_valor, on=["País", "Ano"])

# Exibir tabela
st.dataframe(df_long, use_container_width=True)

# Gráfico de linha para quantidade
chart_qtde = (
    alt.Chart(df_long)
    .mark_line(point=True)
    .encode(
        x=alt.X("Ano:O", title="Ano"),
        y=alt.Y("Quantidade (kg):Q", title="Quantidade Exportada (kg)"),
        color="País:N"
    )
    .properties(title="Evolução da Quantidade Exportada", height=300)
)
st.altair_chart(chart_qtde, use_container_width=True)

# Gráfico de linha para valor
chart_valor = (
    alt.Chart(df_long)
    .mark_line(point=True)
    .encode(
        x=alt.X("Ano:O", title="Ano"),
        y=alt.Y("Valor:Q", title="Valor Exportado (R$ ou US$)"),
        color="País:N"
    )
    .properties(title="Evolução do Valor Exportado", height=300)
)
st.altair_chart(chart_valor, use_container_width=True)

# Top 5 países importadores por valor total
df_total_por_pais = df.copy()
df_total_por_pais["Valor Total"] = df_total_por_pais[[col for col in df.columns if "valor" in col]].sum(axis=1)
df_top5 = df_total_por_pais.groupby("País")["Valor Total"].sum().sort_values(ascending=False).head(5).reset_index()

chart_top5 = (
    alt.Chart(df_top5)
    .mark_bar()
    .encode(
        x=alt.X("Valor Total:Q", title="Valor Total Importado"),
        y=alt.Y("País:N", sort='-x', title="País")
    )
    .properties(title="Top 5 Países Importadores de Vinho", height=300)
)
st.altair_chart(chart_top5, use_container_width=True)
