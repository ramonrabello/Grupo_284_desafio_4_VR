import streamlit as st
import pandas as pd
import io

# Título da aplicação
st.title('Automação de VR')
st.markdown('### Carregue os arquivos para processamento')

# Dicionário para armazenar os arquivos carregados
uploaded_files = {
    'ATIVOS': st.file_uploader("1. Carregue 'ATIVOS.xlsx'", type=['xlsx']),
    'DESLIGADOS': st.file_uploader("2. Carregue 'DESLIGADOS.xlsx'", type=['xlsx']),
    'AFASTAMENTOS': st.file_uploader("3. Carregue 'AFASTAMENTOS.xlsx'", type=['xlsx']),
    'FÉRIAS': st.file_uploader("4. Carregue 'FÉRIAS.xlsx'", type=['xlsx']),
    'ADMISSAO_ABRIL': st.file_uploader("5. Carregue 'ADMISSÃO ABRIL.xlsx'", type=['xlsx']),
    'APRENDIZ': st.file_uploader("6. Carregue 'APRENDIZ.xlsx'", type=['xlsx']),
    'ESTAGIO': st.file_uploader("7. Carregue 'ESTÁGIO.xlsx'", type=['xlsx']),
    'EXTERIOR': st.file_uploader("8. Carregue 'EXTERIOR.xlsx'", type=['xlsx']),
    'DIAS_UTEIS': st.file_uploader("9. Carregue 'Base dias uteis.xlsx'", type=['xlsx']),
    'SINDICATO_VALOR': st.file_uploader("10. Carregue 'Base sindicato x valor.xlsx'", type=['xlsx']),
}

# Botão para iniciar o processamento
if st.button('Processar'):
    # Verifica se todos os arquivos foram carregados antes de iniciar o processamento
    if all(uploaded_files.values()):
        st.write("Iniciando o processamento dos dados...")
        
        try:
            # Dicionário para armazenar os DataFrames
            dataframes = {}
            for key, uploaded_file in uploaded_files.items():
                # Tenta ler com header na linha 1 e ajusta para casos específicos
                try:
                    df = pd.read_excel(uploaded_file, header=1)
                except Exception:
                    df = pd.read_excel(uploaded_file, header=0)
                
                # Limpa os nomes das colunas
                df.columns = df.columns.str.strip().str.upper()
                dataframes[key] = df

            st.success("Arquivos carregados com sucesso!")

            # --- Etapa 1: Consolidar as bases de dados ---
            st.write("Consolidando bases ATIVOS e ADMISSÃO ABRIL...")
            # Unir as bases de ativos e admissão
            base_final = pd.concat([dataframes['ATIVOS'], dataframes['ADMISSAO_ABRIL']], ignore_index=True)

            # --- Etapa 2: Excluir os colaboradores não elegíveis ---
            st.write("Excluindo colaboradores desligados, afastados, de férias, estagiários e aprendizes...")
            
            # Excluir desligados
            df_desligados = dataframes['DESLIGADOS']['MATRICULA'].astype(str).tolist()
            base_final = base_final[~base_final['MATRICULA'].astype(str).isin(df_desligados)]
            
            # Excluir afastados
            df_afastados = dataframes['AFASTAMENTOS']['MATRICULA'].astype(str).tolist()
            base_final = base_final[~base_final['MATRICULA'].astype(str).isin(df_afastados)]

            # Excluir de férias (se a coluna 'DESC. SITUACAO' for 'Férias')
            base_final = base_final[~base_final['DESC. SITUACAO'].str.contains('FÉRIAS', na=False, case=False)]
            
            # Excluir estagiários e aprendizes com base no TÍTULO DO CARGO
            titulos_a_excluir = pd.concat([
                dataframes['ESTAGIO']['TITULO DO CARGO'], 
                dataframes['APRENDIZ']['TITULO DO CARGO']
            ]).unique().tolist()
            base_final = base_final[~base_final['TITULO DO CARGO'].isin(titulos_a_excluir)]
            
            # Excluir quem está no exterior
            df_exterior = dataframes['EXTERIOR']['CADASTRO'].astype(str).tolist()
            base_final = base_final[~base_final['MATRICULA'].astype(str).isin(df_exterior)]
            
            st.success("Exclusões realizadas com sucesso!")

            # --- Etapa 3: Mesclar com bases de dias úteis e valores do sindicato ---
            st.write("Mesclando com as bases de dias úteis e valores de sindicato...")
            
            # Limpar coluna de sindicato na base_final para mesclar
            base_final['SINDICATO'] = base_final['SINDICATO'].str.strip()

            # Mesclar com a base de dias úteis
            dias_uteis_df = dataframes['DIAS_UTEIS'].copy()
            dias_uteis_df.rename(columns={'SINDICADO': 'SINDICATO', 'DIAS UTEIS ': 'DIAS'}, inplace=True) # Ajuste nos nomes das colunas
            dias_uteis_df['SINDICATO'] = dias_uteis_df['SINDICATO'].str.strip()
            base_final = pd.merge(base_final, dias_uteis_df[['SINDICATO', 'DIAS']], on='SINDICATO', how='left')
            
            # Mapear a sigla do estado para o nome completo para o merge com a base de valores
            sindicato_valor_df = dataframes['SINDICATO_VALOR'].copy()
            sindicato_valor_df.rename(columns={'ESTADO': 'ESTADO', 'VALOR': 'VALOR DIÁRIO VR'}, inplace=True)
            sindicato_valor_df['ESTADO'] = sindicato_valor_df['ESTADO'].str.strip().str.upper()

            sindicato_mapping = {
                'SP': 'SÃO PAULO',
                'RS': 'RIO GRANDE DO SUL',
                'PR': 'PARANÁ',
                'RJ': 'RIO DE JANEIRO'
            }
            # Extração mais robusta da sigla do estado
            base_final['ESTADO'] = base_final['SINDICATO'].str.split(' - ').str[0].str[-2:].str.strip().str.upper().map(sindicato_mapping)
            
            # Fazer o merge com a base de valores de sindicato
            base_final = pd.merge(base_final, sindicato_valor_df, on='ESTADO', how='left')

            st.success("Mesclagem concluída!")

            # --- Etapa 4: Calcular o valor do benefício ---
            st.write("Realizando os cálculos finais...")
            base_final['TOTAL'] = base_final['DIAS'] * base_final['VALOR DIÁRIO VR']
            base_final['Custo empresa'] = base_final['TOTAL'] * 0.80
            base_final['Desconto profissional'] = base_final['TOTAL'] * 0.20
            
            # Limpar colunas de mesclagem para o relatório final
            base_final.drop(columns=['ESTADO'], inplace=True, errors='ignore')
            
            st.success('Processamento concluído! O arquivo está pronto para download.')
            
            # --- Etapa 5: Gerar o arquivo Excel para download ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                base_final.to_excel(writer, index=False, sheet_name='Base Final')
            output.seek(0)
            
            st.download_button(
                label="Clique para baixar o arquivo",
                data=output,
                file_name="Base_VR_Pronta.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Ocorreu um erro durante o processamento: {e}")
            st.warning("Por favor, verifique se os arquivos estão corretos e tente novamente.")

    else:
        st.warning('Por favor, carregue todos os arquivos antes de processar.')