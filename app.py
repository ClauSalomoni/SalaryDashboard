import streamlit as st
import pandas as pd
import plotly.express as px
import os


# --- Configuração da Página ---
# Define o título da página é o que vai aparecer titulo navegador, o ícone e o layout para ocupar a largura inteira.
#podemos mudar!



st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)


# Caminho do arquivo local dentro da pasta 'data'
arquivo_local = os.path.join("data", "dados-imersao-final.csv")


# Carrega o arquivo CSV local
df = pd.read_csv(arquivo_local)




# --- Barra Lateral (Filtros/Posso editar para o que quiser, e adicionar icones?) ---
st.sidebar.header("🔍 Filtros")
st.sidebar.markdown("Remova os filtros indesejados")


# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)


# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)


# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)


# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)


# --- Filtragem do DataFrame ---
# aqui é o codigo para aplicar os filtros, segundo o que o usuario selecionar
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
].copy()


# --- Conteúdo Principal  o st.titulo = h1; o markdown um <p> abaixo do titulo---
st.title("🎲🎲 Dashboard de Análise de Salários | Área de Dados 🎲🎲")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")


# --- Métricas Principais (KPIs) st.subheader=h2---
st.subheader("Métricas gerais (Salário anual em USD)")


if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, ""


## com o st podemos dividir a pagina em colunas(define as colunas e= ST.COLUMNS(numero de colunas):
col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)


st.markdown("---")


# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")
## ABAIXO definido 2 colunas para mostrar graficos
##novamente QUANTAS COLUNAS vou usar:: ST.COLUMNS(numero de colunas)
col_graf1, col_graf2 = st.columns(2)


with col_graf1:
    if not df_filtrado.empty:## "NLARGEST(numero), define os "top 10", neste caso, 
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h', ## H de horizontal, ou "v" para VERTICAL
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial/ano (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True) ## aqui exibe o grafico
    else:
        ##se o grafico nao aparecer vem o recado:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")


with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")
## aqui mais 2 colunas  abaixo dos graficos 1 e 2
col_graf3, col_graf4 = st.columns(2)


with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5  
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")


with col_graf4:
    if not df_filtrado.empty:
        # Lógica para decidir qual categoria usar na cor do gráfico
        if len(senioridades_selecionadas) > 1:
            categoria = "senioridade"
        elif len(df_filtrado["remoto"].unique()) > 1:
            categoria = "remoto"
        else:
            categoria = None


        # Agrupa os dados
        if categoria:
            if categoria == "senioridade":
                ordem_categorias = ["executivo", "senior", "pleno", "junior"]
                df_filtrado.loc[:, categoria] = pd.Categorical(df_filtrado[categoria], categories=ordem_categorias, ordered=True)
            df_agrupado = (
                df_filtrado
                .groupby(["ano", categoria], observed=True)["usd"]
                .mean()
                .reset_index()
            )
            grafico_linha = px.line(
                df_agrupado,
                x="ano",
                y="usd",
                color=categoria,
                markers=True,
                title="Evolução Salarial ao Longo dos Anos/Ano",
                labels={
                    "ano": "Ano",
                    "usd": "Salário Médio (USD)",
                    categoria: categoria.capitalize()
                }
            )
        else:
            df_agrupado = (
                df_filtrado
                .groupby("ano")["usd"]
                .mean()
                .reset_index()
            )
            grafico_linha = px.line(
                df_agrupado,
                x="ano",
                y="usd",
                markers=True,
                title="Salário médio (USD) por ano",
                labels={"ano": "Ano", "usd": "Salário Médio (USD)"}
            )


        # Estilo do gráfico
        grafico_linha.update_layout(
            title_x=0.1,           # centraliza o título
            height=400,            # define altura semelhante aos outros
            margin=dict(t=100)      # margem superior para o título não colar
        )


        # Exibe o gráfico
        st.plotly_chart(grafico_linha, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir a evolução salarial.")



if not df_filtrado.empty:
    df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
    ## RESIDENCIA_ISO3 quer dizer as 3 primeiras letras dos paizes, vem de alguma biblio
    media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
    grafico_paises = px.choropleth(media_ds_pais,
        locations='residencia_iso3',
        color='usd',##ver paletas da DOC da PLOTLY abaixo: cores do mapa
        color_continuous_scale='viridis',
        title='Salário médio de Cientista de Dados por país',
        labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
    grafico_paises.update_layout(title_x=0.1)
    st.plotly_chart(grafico_paises, use_container_width=True)
else:
    st.warning("Nenhum dado para exibir no gráfico de países.") 





# --- Tabela de Dados Detalhados ---
st.subheader("Tabela Completa")
st.dataframe(df_filtrado)