Com certeza\! Abaixo está uma explicação detalhada e estruturada de todo o fluxo do nosso código. Você pode usar esta descrição para criar um documento `README.md` completo para o seu projeto.

-----

### **Visão Geral**

O script `automacao_vr.py` é uma ferramenta inteligente desenvolvida para automatizar o cálculo de Vale-Alimentação/Refeição (VR). Ele consolida dados de múltiplas planilhas, aplica regras de negócios complexas (como exclusões, descontos de férias e feriados) e gera um arquivo final pronto para uso. O objetivo é simplificar e agilizar o processamento mensal do benefício.

### **Requisitos**

Para executar o script, você precisa ter o Python instalado e as seguintes bibliotecas:

  * `streamlit`
  * `pandas`
  * `openpyxl`
  * `zipfile`
  * `xlsxwriter`

Você pode instalá-las usando o seguinte comando:

```bash
pip install streamlit pandas openpyxl xlsxwriter
```

### **Estrutura de Entrada**

O script opera a partir de um único arquivo `.zip` que deve conter as seguintes planilhas no formato `.xlsx`:

  * **`ATIVOS`**: Base principal de colaboradores ativos.
  * **`ADMISSÃO_ABRIL`**: Lista de colaboradores admitidos no mês de referência.
  * **`DESLIGADOS`**: Colaboradores que foram desligados.
  * **`FÉRIAS`**: Lista de colaboradores de férias com a quantidade de dias.
  * **`EXTERIOR`**: Colaboradores alocados fora do país.
  * **`ESTÁGIO`**: Colaboradores estagiários.
  * **`APRENDIZ`**: Colaboradores aprendizes.
  * **`VR_MENSAL`**: Base de valores de VR já atribuídos.
  * **`AFASTAMENTOS`**: Lista de colaboradores afastados.
  * **`BASE_SINDICATO_X_VALOR`**: Mapeamento de sindicato para valor diário do VR.
  * **`BASE_DIAS_UTEIS`**: Mapeamento de sindicato para a quantidade de dias úteis no mês.

### **Fluxo de Processamento**

O script executa uma série de passos lógicos para processar os dados e gerar o resultado final.

1.  **Consolidação das Bases:**

      * As bases **`ATIVOS`** e **`ADMISSÃO_ABRIL`** são mescladas em uma única base de dados principal.

2.  **Filtragem e Exclusão de Colaboradores:**

      * Os colaboradores que **não são elegíveis** ao benefício são removidos. Isso inclui:
          * **Estagiários** e **Aprendizes**, com base na coluna `TÍTULO DO CARGO`.
          * **Diretores**, com base na coluna `TÍTULO DO CARGO`.
          * Colaboradores em **Afastamentos** em geral (como licença-maternidade), utilizando a matrícula para exclusão.
          * Profissionais que atuam no **Exterior**, utilizando a matrícula para exclusão.
          * Colaboradores que foram **desligados**, utilizando a matrícula para exclusão.
          * Colaboradores com anotações de "não recebe VR" na coluna `OBSERVAÇÕES`.

3.  **Mapeamento Inteligente de Dados:**

      * Esta é a etapa mais crítica. O script usa uma lógica de "cascata" para preencher as informações necessárias:
          * Ele usa a coluna `TITULO_DO_CARGO` para preencher o **Sindicato** de colaboradores recém-admitidos, se a informação estiver faltando.
          * Em seguida, ele usa a planilha **`BASE_SINDICATO_X_VALOR`** para encontrar o **Estado** correspondente a cada sindicato.
          * Com o sindicato definido, ele busca o número de **Dias Úteis** na planilha **`BASE_DIAS_UTEIS`**.
          * Com o estado definido, ele busca o **Valor Diário do VR** na planilha **`BASE_SINDICATO_X_VALOR`**.

4.  **Ajustes e Descontos:**

      * O script **desconta os dias de férias** com base na planilha `FÉRIAS`.
      * Ele **desconta os feriados** com base no **Estado** de cada colaborador.
      * Ele ajusta o número de dias com base nas regras de `AFASTAMENTOS`.

5.  **Cálculos Finais:**

      * O valor **`TOTAL`** é calculado multiplicando os `DIAS` elegíveis pelo `VALOR_DIARIO_VR`.
      * O **`Custo_empresa`** é 80% do valor total.
      * O **`Desconto_profissional`** é 20% do valor total.

### **Saída**

Após o processamento, o script gera um único arquivo Excel chamado **`Base_VR_Pronta.xlsx`**, que contém todos os colaboradores elegíveis com os valores calculados em suas respectivas colunas. Este arquivo é disponibilizado para download.

### **Como Usar**

Para iniciar a automação, salve o código em um arquivo `automacao_vr.py` e execute o seguinte comando no terminal:

```bash
streamlit run automacao_vr.py
```

Isso abrirá uma interface web no seu navegador, onde você pode carregar o arquivo `.zip` para processar os dados.
