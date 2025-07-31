import streamlit as st

import pandas as pd

st.set_page_config(
    page_title='Finanças',
    page_icon='💰',
   # layout='wide',
   # initial_sidebar_state='expanded'
)

st.markdown("""
            
## Nosso APP Financeiro!

""" )

st.title("Dashboard de Finanças")

## subir arquivo

file_upload = st.file_uploader(label= 'Faça upload dos dados aqui.', type=['csv'])

# verificar se algum arquivo foi feito upload
if file_upload:

    # leitura dos dados
    df = pd.read_csv(file_upload)
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y').dt.date

    # exibicao dos dados
    exp1 = st.expander('Dados Brutos')
    columns_fmt = {'Valor': st.column_config.NumberColumn('Valor', format='R$ %d')}
    exp1.dataframe(df, hide_index=True, column_config = columns_fmt)


    # visao instituicao
    exp2 = st.expander('Instituições')
    df_instituicao = df.pivot_table(index='Data', columns='Instituição', values='Valor')

    # abas para diferentes visualizações
    tab_data, tab_history, tab_share =  exp2.tabs(['Dados', 'Histórico', 'Distribuição'])
    
    with tab_data:
        st.dataframe(df_instituicao)
    
    with tab_history:
        st.line_chart(df_instituicao)

    # ultima data de dados
    with tab_share:
            
            # formato de enxergar as data de acordo com as disponiveis
            date = st.selectbox('Filtro Data', options = df_instituicao.index)


    #    # formato abaixo de data para procurar no calendário
    #    date = st.date_input('Data para Distribuição', 
    #                         min_value = df_instituicao.index.min(), 
    #                         max_value = df_instituicao.index.max())
    #    if date not in df_instituicao.index:
    #        st.warning('Entre com uma data válida')
    #    
    #    else:
            st.bar_chart(df_instituicao.loc[date]) # gráfico de distribuição