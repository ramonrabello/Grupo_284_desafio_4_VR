import streamlit as st
import pandas as pd
import zipfile
import io
import re

# Título da aplicação
st.title('Valle.ai - Assistente inteligente para projeto de Vale-Alimentação/Refeição')
st.markdown('### Carregue o arquivo zip contendo as planilhas para processamento')

# Dicionário para armazenar os DataFrames extraídos do ZIP
dataframes = {}

# Mapeamento de nomes de arquivos para chaves internas
file_name_mapping = {
    'ATIVOS': 'ATIVOS',
    'ADMISSAO_ABRIL': 'ADMISSÃO_ABRIL',
    'DESLIGADOS': 'DESLIGADOS',
    'AFASTAMENTOS': 'AFASTAMENTOS',
    'EXTERIOR': 'EXTERIOR',
    'ESTAGIO': 'ESTAGIO',
    'APRENDIZ': 'APRENDIZ',
    'BASE_DIAS_UTEIS': 'BASE_DIAS_UTEIS',
    'BASE_SINDICATO_X_VALOR': 'BASE_SINDICATO_X_VALOR',
    'VR_MENSAL': 'VR_MENSAL',
    'FERIAS': 'FERIAS'
}

# Dicionário para mapear sindicatos a valores fixos
valor_sindicato_fixo = {
    'SINDPD SP - SIND.TRAB.EM PROC DADOS E EMPR.EMPRESAS PROC DADOS ESTADO DE SP.': 37.50,
    'SITEPD PR - SIND DOS TRAB EM EMPR PRIVADAS DE PROC DE DADOS DE CURITIBA E REGIAO METROPOLITANA': 35.00
}

# Dicionário de feriados por estado para abril de 2025
feriados_por_estado = {
    'RIO GRANDE DO SUL': ['2025-04-18', '2025-04-21'],
    'RIO DE JANEIRO': ['2025-04-18', '2025-04-21', '2025-04-23']
}

# Função para padronizar nomes de colunas
def standardize_columns(df):
    new_cols = {}
    for col in df.columns:
        new_col = str(col).upper().strip().replace('.', '').replace(' ', '_').replace('Ç', 'C').replace('Ã', 'A').replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        new_cols[col] = new_col
    return df.rename(columns=new_cols)

# Função para encontrar a linha do cabeçalho
def find_header(file_data):
    file_data.seek(0)
    df_temp = pd.read_excel(file_data, nrows=10, header=None, engine='openpyxl')
    for i, row in df_temp.iterrows():
        header_names = [str(c).upper().strip().replace('.', '').replace(' ', '_').replace('Ç', 'C') for c in row if isinstance(c, str)]
        if any(col in header_names for col in ['MATRICULA', 'CADASTRO', 'SINDICATO', 'TITULO_DO_CARGO']):
            return i
    file_data.seek(0)
    return 0

# Função para encontrar a coluna de afastamento
def find_afastamento_column(df):
    for col in df.columns:
        col_normalized = str(col).upper().replace(' ', '').replace('.', '')
        if 'DESCSITUACAO' in col_normalized or 'TIPOAFASTAMENTO' in col_normalized:
            return col
    return None

# Passo 1: Upload do arquivo ZIP
zip_file = st.file_uploader("Selecione ou arraste o arquivo ZIP aqui", type=["zip"])

if zip_file is not None:
    with st.spinner("Extraindo arquivos..."):
        try:
            with zipfile.ZipFile(zip_file, 'r') as z:
                st.write("Arquivos encontrados no ZIP:")
                for file_name in z.namelist():
                    if file_name.endswith(".xlsx") and not file_name.startswith('__MACOSX'):
                        st.write(f"- {file_name.split('/')[-1]}")
                        
                        with z.open(file_name) as f:
                            file_data = io.BytesIO(f.read())
                            
                            try:
                                header_row = find_header(file_data)
                                df = pd.read_excel(file_data, header=header_row, engine='openpyxl')
                                df = standardize_columns(df)
                                df = df.loc[:, ~df.columns.str.contains('^UNNAMED', case=False, na=False)]

                                st.write(f"  → Cabeçalho encontrado e definido na linha: {header_row + 1}")
                                
                            except Exception as e:
                                st.warning(f"Erro ao tentar ler a planilha {file_name.split('/')[-1]}: {e}. O arquivo não será processado.")
                                continue

                            key_raw = file_name.split('/')[-1].upper().replace('.XLSX', '').replace(' ', '_').strip()
                            found_key = next((v for k, v in file_name_mapping.items() if k in key_raw), None)
                            
                            if found_key:
                                dataframes[found_key] = df
                            else:
                                dataframes[key_raw] = df

            st.success("Arquivos extraídos com sucesso!")
            st.info(f"Arquivos carregados com sucesso: {list(dataframes.keys())}")
            
        except Exception as e:
            st.error(f"Ocorreu um erro ao extrair o ZIP: {e}")
            dataframes = {}

# --- Botão e Lógica de Processamento ---
if dataframes and st.button('Processar'):
    st.write("Iniciando o processamento dos dados...")
    
    try:
        st.write("Consolidando bases ATIVOS e ADMISSÃO ABRIL...")
        
        if 'ATIVOS' in dataframes and 'ADMISSÃO_ABRIL' in dataframes:
            base_ativos = dataframes['ATIVOS'].reset_index(drop=True)
            base_admissao = dataframes['ADMISSÃO_ABRIL'].reset_index(drop=True)
            base_final = pd.concat([base_ativos, base_admissao], ignore_index=True)
        else:
            st.error("Arquivos ATIVOS ou ADMISSÃO_ABRIL não encontrados.")
            st.stop()
        
        st.write("Excluindo colaboradores desligados, de férias, e que não são elegíveis...")
        
        # Exclusão de diretores, estagiários e aprendizes por cargo
        cargos_a_excluir = ['ESTAGIARIO', 'APRENDIZ', 'DIRETOR']
        base_final = base_final[~base_final['TITULO_DO_CARGO'].astype(str).str.upper().str.contains('|'.join(cargos_a_excluir), na=False, case=False)]

        # Exclusão de colaboradores com anotação de 'não recebe VR'
        if 'OBSERVACOES' in base_final.columns:
            base_final = base_final[~base_final['OBSERVACOES'].astype(str).str.contains('nao recebe VR', na=False, case=False)]
        
        # Exclusão de desligados, exterior e afastados por matrícula
        matriculas_a_excluir = []
        if 'DESLIGADOS' in dataframes and 'MATRICULA' in dataframes['DESLIGADOS'].columns:
            matriculas_a_excluir.extend(dataframes['DESLIGADOS']['MATRICULA'].astype(str).tolist())
        
        if 'EXTERIOR' in dataframes and 'CADASTRO' in dataframes['EXTERIOR'].columns:
            matriculas_a_excluir.extend(dataframes['EXTERIOR']['CADASTRO'].astype(str).tolist())
            
        if 'AFASTAMENTOS' in dataframes and 'MATRICULA' in dataframes['AFASTAMENTOS'].columns:
            matriculas_a_excluir.extend(dataframes['AFASTAMENTOS']['MATRICULA'].astype(str).tolist())
            
        base_final = base_final[~base_final['MATRICULA'].astype(str).isin(matriculas_a_excluir)]
            
        st.success("Exclusões realizadas com sucesso!")

        st.write("Mesclando com as bases de dias úteis e valores de sindicato...")

        # 1. Cria um mapeamento SINDICATO -> ESTADO a partir da BASE_SINDICATO_X_VALOR
        sindicato_valor_df = dataframes['BASE_SINDICATO_X_VALOR'].copy()
        sindicato_valor_df.rename(columns={'UF': 'ESTADO', 'VALOR DIARIO': 'VALOR_DIARIO_VR'}, inplace=True)
        sindicato_valor_df['ESTADO'] = sindicato_valor_df['ESTADO'].astype(str).str.strip().str.upper()
        
        sindicato_estado_map = sindicato_valor_df.set_index('SINDICATO')['ESTADO'].to_dict()
        valores_diarios_ref = sindicato_valor_df.set_index('ESTADO')['VALOR_DIARIO_VR'].to_dict()

        # 2. Mapeia Sindicato e Estado na base_final
        base_final['SINDICATO'] = base_final.apply(
            lambda row: valor_sindicato_fixo.get(str(row['TITULO_DO_CARGO']).strip(), row['SINDICATO'])
            if pd.isna(row['SINDICATO']) else row['SINDICATO'],
            axis=1
        )
        base_final['SINDICATO'] = base_final.apply(
            lambda row: 'SINDPPD RS - SINDICATO DOS TRAB. EM PROC. DE DADOS RIO GRANDE DO SUL' 
            if 'ASSISTENTE_DE_BPO_I' in str(row['TITULO_DO_CARGO']).upper() and pd.isna(row['SINDICATO']) 
            else row['SINDICATO'],
            axis=1
        )

        base_final['ESTADO'] = base_final['SINDICATO'].map(sindicato_estado_map)

        # 3. Mescla com a base de dias úteis e valores de VR
        dias_uteis_ref = dataframes['BASE_DIAS_UTEIS'].set_index('SINDICATO')['DIAS_UTEIS'].to_dict()
        base_final['DIAS'] = base_final['SINDICATO'].map(dias_uteis_ref)
        base_final['VALOR_DIARIO_VR'] = base_final['ESTADO'].map(valores_diarios_ref)
        
        # 4. Preenche valores que não foram mapeados com valores padrão
        base_final['DIAS'] = base_final['DIAS'].fillna(0)
        base_final['VALOR_DIARIO_VR'] = base_final['VALOR_DIARIO_VR'].fillna(35.00)
        
        st.success("Valores de dias e sindicatos atribuídos!")
        
        # Mesclagem de férias e descontos de feriados
        if 'FERIAS' in dataframes and 'DIAS_DE_FERIAS' in dataframes['FERIAS'].columns:
            ferias_df = dataframes['FERIAS'].copy()
            base_final = pd.merge(base_final, ferias_df[['MATRICULA', 'DIAS_DE_FERIAS']], on='MATRICULA', how='left')
            base_final['DIAS_DE_FERIAS'] = pd.to_numeric(base_final['DIAS_DE_FERIAS'], errors='coerce').fillna(0)
            base_final['DIAS'] = base_final['DIAS'] - base_final['DIAS_DE_FERIAS']

        # Lógica para descontar feriados
        base_final['DIAS_FERIADOS'] = base_final['ESTADO'].apply(
            lambda x: len(feriados_por_estado.get(str(x).upper().strip(), []))
        )
        base_final['DIAS'] = base_final['DIAS'] - base_final['DIAS_FERIADOS']
        
        st.success("Mesclagem e atribuição de valores concluídas!")

        st.write("Realizando os cálculos finais...")

        base_final['DIAS'] = pd.to_numeric(base_final['DIAS'], errors='coerce').fillna(0)
        base_final['VALOR_DIARIO_VR'] = pd.to_numeric(base_final['VALOR_DIARIO_VR'], errors='coerce').fillna(0)
        
        base_final['TOTAL'] = base_final['DIAS'] * base_final['VALOR_DIARIO_VR']
        base_final['Custo_empresa'] = base_final['TOTAL'] * 0.80
        base_final['Desconto_profissional'] = base_final['TOTAL'] * 0.20
        
        base_final = base_final.drop(columns=['DIAS_DE_FERIAS', 'DIAS_FERIADOS'], errors='ignore')

        # Incluir linha de soma no final do DataFrame
        total_total = base_final['TOTAL'].sum()
        total_custo = base_final['Custo_empresa'].sum()
        total_desconto = base_final['Desconto_profissional'].sum()
        
        # Garantir que a linha de soma tenha o mesmo número de colunas
        linha_soma = pd.DataFrame([['TOTAIS'] + [''] * (len(base_final.columns) - 4) + [total_total, total_custo, total_desconto]],
                                  columns=base_final.columns)
        
        base_final = pd.concat([base_final, linha_soma], ignore_index=True)
        
        st.success('Processamento concluído! O arquivo está pronto para download.')
        
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
