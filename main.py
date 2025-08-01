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

    def calc_estats(df:pd.DataFrame):
        df_data = df.groupby(by='Data')[['Valor']].sum()
        df_data['lag_1'] = df_data['Valor'].shift(1)
        df_data['Diferença Mensal Absoluto'] = df_data['Valor'] - df_data['lag_1']
        df_data['Média 6M Diferença Mensal Absolutol'] = df_data['Diferença Mensal Absoluto'].rolling(6).mean()
        df_data['Média 12M Diferença Mensal Absoluto'] = df_data['Diferença Mensal Absoluto'].rolling(12).mean()
        df_data['Média 24M Diferença Mensal Absoluto'] = df_data['Diferença Mensal Absoluto'].rolling(24).mean()

        df_data['Diferença Mensal Relativa'] = df_data['Valor'] / df_data['lag_1'] -1

        df_data['Evolução 6M Total'] = df_data['Valor'].rolling(6).apply(lambda x: x[-1] - x[0])
        df_data['Evolução 12M Total'] = df_data['Valor'].rolling(12).apply(lambda x: x[-1] - x[0])
        df_data['Evolução 24M Total'] = df_data['Valor'].rolling(24).apply(lambda x: x[-1] - x[0])

        df_data['Evolução 6M Relativa'] = df_data['Valor'].rolling(6).apply(lambda x: x[-1] / x[0] -1)
        df_data['Evolução 12M  Relativa'] = df_data['Valor'].rolling(12).apply(lambda x: x[-1] / x[0] -1)
        df_data['Evolução 24M  Relativa'] = df_data['Valor'].rolling(24).apply(lambda x: x[-1] / x[0] -1)

        df_data = df_data.drop('lag_1', axis=1)

        return df_data
    
    df_stats = calc_estats(df)

    ##

    exp3 = st.expander('Estatísticas Gerais')

    columns_config = {
         'Valor': st.column_config.NumberColumn('Valor', format='R$ %.2f'),
         'Diferença Mensal Absoluto': st.column_config.NumberColumn('Diferença Mensal Absoluto', format='R$ %.2f'),
         'Média 6M Diferença Mensal Absolutol': st.column_config.NumberColumn('Média 6M Diferença Mensal Absolutol', format='R$ %.2f'),
         'Média 12M Diferença Mensal Absoluto': st.column_config.NumberColumn('Média 12M Diferença Mensal Absoluto', format='R$ %.2f'),
         'Média 24M Diferença Mensal Absoluto': st.column_config.NumberColumn('Média 24M Diferença Mensal Absoluto', format='R$ %.2f'),
         'Diferença Mensal Relativa': st.column_config.NumberColumn('Diferença Mensal Relativa', format='percent'),
         'Evolução 6M Total': st.column_config.NumberColumn('Evolução 6M Total', format='R$ %.2f'),
         'Evolução 12M Total': st.column_config.NumberColumn('Evolução 12M Total', format='R$ %.2f'),
         'Evolução 24M Total': st.column_config.NumberColumn('Evolução 24M Total', format='R$ %.2f'),
         'Evolução 6M Relativa': st.column_config.NumberColumn('Evolução 6M Relativa', format='percent'),
         'Evolução 12M  Relativa': st.column_config.NumberColumn('Evolução 12M  Relativa', format='percent'),
         'Evolução 24M  Relativa': st.column_config.NumberColumn('Evolução 24M  Relativa', format='percent'),
    }

    tab_stats, tab_abs, tab_rel = exp3.tabs(tabs=['Dados', 'Histórico de Evolução', 'Crescimento Relativo'])

    with tab_stats:
         
        st.dataframe(df_stats, column_config=columns_config)

    with tab_abs:
        abs_cols = ['Diferença Mensal Absoluto',
                    'Média 6M Diferença Mensal Absolutol',
                    'Média 12M Diferença Mensal Absoluto',
                    'Média 24M Diferença Mensal Absoluto']
        st.line_chart(df_stats[abs_cols])

    with tab_rel:
         rel_cols = [
            'Diferença Mensal Relativa',
            'Evolução 6M Relativa',
            'Evolução 12M  Relativa',
            'Evolução 24M  Relativa',
         ]

         st.line_chart(data=df_stats[rel_cols])