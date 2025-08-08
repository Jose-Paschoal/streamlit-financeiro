# %%

from multiprocessing import Value
import streamlit as st

import pandas as pd

import requests
import datetime

@st.cache_data(ttl='1day')
def get_selic():
    url = "https://bcb.gov.br/api/servico/sitebcb/historicotaxasjuros"
    resp = requests.get(url)
    df = pd.DataFrame(resp.json()['conteudo'])

    df['DataInicioVigencia'] = pd.to_datetime(df['DataInicioVigencia']).dt.date
    df['DataFimVigencia'] = pd.to_datetime(df['DataFimVigencia']).dt.date
    df['DataFimVigencia'] = df['DataFimVigencia'].fillna(datetime.datetime.today().date())

    return df

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

    
    ## criando uma aba de metas

    with st.expander('Metas'):
         
        # tab_main, tab_data, tab_graph = st.tabs(tabs=['Configuração', 'Dados', 'Gráficos'])
         ## criando colunas para não deixar os dados empilhados

         col1, col2 = st.columns(2)
         
         data_inicio_meta = col1.date_input('Início da Meta', max_value = df_stats.index.max())
         data_filtrada =  df_stats.index[df_stats.index <= data_inicio_meta][-1]

         custos_fixos = col1.number_input('Custos Fixos', min_value=0., format='%.2f')

         salario_bruto = col2.number_input('Salário Bruto', min_value=0., format='%.2f')
         salario_liquido = col2.number_input('Salário Líquido', min_value=0., format='%.2f')

         valor_inicio = df_stats.loc[data_filtrada]['Valor']
         col1.markdown(f'**Patrimônio no Início da Meta**: R$ {valor_inicio:.2f}')

         ## selic
         selic_gov = get_selic()
         filter_selic_date = (selic_gov['DataInicioVigencia'] < data_inicio_meta) & (selic_gov['DataFimVigencia'] > data_inicio_meta)
         selic_default =  selic_gov[filter_selic_date]['MetaSelic'].iloc[0]

         selic = st.number_input('Selic', min_value=0., value=selic_default, format= "%.2f")
         selic_ano = selic / 100

         selic_mes = (selic_ano + 1) ** (1/12) - 1

         ## rendimento

         rendimento_ano = valor_inicio * selic_ano
         rendimento_mes = valor_inicio * selic_mes
         

         ## criando outra estrutura de coluna

         col1_pot, col2_pot = st.columns(2)
         salario_mensal = salario_liquido - custos_fixos + rendimento_mes
         salario_anual = 12 * (salario_liquido - custos_fixos) + rendimento_ano

         with col1_pot.container(border=True):
         
            st.markdown(f"""**Potencial Arrecadação Mês**:\n\n R$ {salario_mensal:.2f}""")

         with col2_pot.container(border=True):
            
            st.markdown(f"""**Potencial Arrecadação Anual**:\n\n R$ {salario_anual:.2f}""")

         with st.container(border=True):
            col1_meta, col2_meta = st.columns(2)
            with col1_meta:

               meta_estipulada = st.number_input('Meta Estipulada', min_value=0., format='%.2f', value=salario_anual)

            with col2_meta:

               patrimonio_final = meta_estipulada + valor_inicio
               st.markdown(f"Patrimônio Estimado pós meta:\n\n R$ {patrimonio_final:.2f}")

         meses = pd.DataFrame({
             'Data Referência':[data_inicio_meta + pd.DateOffset(months=i) for i in range(1,13)],
             'Meta Mensal': [valor_inicio + round(meta_estipulada/12,2) * i for i in range(1,13)],
             
             })
         meses['Data Referência'] = meses['Data Referência'].dt.strftime('%Y-%m')
         

         df_patrimonio = df_stats.reset_index()[['Data', 'Valor']]
         df_patrimonio['Data Referência'] = pd.to_datetime(df_patrimonio['Data']).dt.strftime('%Y-%m')
         meses = meses.merge(df_patrimonio, how='left', on='Data Referência')

         meses = meses[['Data Referência', 'Meta Mensal', 'Valor']]
         meses['Atingimento (%)'] = meses['Valor'] / meses['Meta Mensal']

         meses['Atingimento Ano'] = meses['Valor'] / patrimonio_final

         st.dataframe(meses)
         