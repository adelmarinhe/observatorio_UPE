# Observatório Financeiro da UPE
Repositório para o observatório desenvolvido para a Pro-reitoria Administrativa da UPE. Este projeto foi desenvolvido como parte da Residência em Ciência de Dados e Analytics da UPE. A fonte de dados utilizada para o desenvolvimento é proveniente do acervo de dados abertos do Portal da Transparência do Governo de Pernambuco.

Nota: Este observatório foi desenvolvido como modelo piloto para potenciais aplicações futuras.

# Guia de Configuração e Execução do Dashboard

Este guia orienta o processo de preparação do ambiente e execução da aplicação utilizando a biblioteca **Streamlit**.

## 1. Instalação do Streamlit

O Streamlit é uma biblioteca Python e pode ser instalado diretamente via gerenciador de pacotes `pip`.

> **Recomendação:** Embora não seja obrigatório, recomenda-se a utilização de um ambiente virtual (como `venv` ou `conda`) para evitar potenciais conflitos de dependências entre diferentes versões do Python e de outras bibliotecas de seu sistema.

1. Para criação de novo ambiente:

```bash
conda create --name nome_do_ambiente python=3.10
```

2. Para ativação do ambiente:

```bash
conda activate nome_do_ambiente
```

3. Execute o comando abaixo no terminal para realizar a instalação:

```bash
pip install streamlit

```

Obs.: Para verificar se a instalação foi concluída com sucesso, execute:

```bash
streamlit hello

```

Uma nova aba será aberta automaticamente no seu navegador padrão confirmando o funcionamento.

## 2. Instalação das Dependências

Para a manipulação de dados e renderização dos gráficos do dashboard, deve-se instalar as seguintes bibliotecas:

```bash
pip install pandas plotly numpy scikit-learn xgboost

```

## 3. Estrutura Padrão da Aplicação

O fluxo de desenvolvimento do pipeline visual deste projeto segue a seguinte arquitetura de código:

1. **Carregamento de Dados:** Upload ou leitura do arquivo de dados (dataset).
2. **Tratamento de Dados:** Limpeza, conversão de tipos e formatação de strings (etapa opcional caso os dados já tenham passado por um processo prévio de ETL em ferramentas como Apache Hop).
3. **Componentes de Filtragem:** Definição dos parâmetros dinâmicos de seleção localizados na barra lateral.
4. **Visualizações:** Construção e exibição dos gráficos e KPIs na área principal.

## 4. Execução do Dashboard

Para rodar o dashboard localmente, clone ou baixe o repositório na máquina local, navegue via terminal até o diretório onde o arquivo principal do projeto está localizado e execute o comando abaixo (certifique-se de substituir `dashboard.py` pelo nome exato do seu arquivo, caso seja diferente):

```bash
streamlit run .\dashboard.py --server.port 8888

```

Após a inicialização do servidor, a aplicação estará acessível no navegador através da porta indicada (`http://localhost:8888`).

### Referências Úteis

Para entender melhor a sintaxe e as possibilidades de customização do Streamlit, os seguintes repositórios servem como ótimas fontes de consulta prática:

* [Exemplo de Dashboard Base - rvats20](https://github.com/rvats20/streamlit-Dashboard/blob/main/Dashboard.py)
* [Estrutura de Aplicação Web - ScriptsRemote](https://github.com/ScriptsRemote/Streamlit_dash/blob/main/app.py)
* [Tutorial de Streamlit - UFRJ Analytica](https://github.com/UFRJ-Analytica/streamlit-tutorial/blob/main/dashboard.py)
