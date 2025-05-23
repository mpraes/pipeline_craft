"""
Data Cleaning Template Guide
--------------------------

This template provides a comprehensive framework for data cleaning using pandas.
Follow these guidelines when using this template:

1. BEFORE USING THIS TEMPLATE:
   - Make a backup of your original data
   - Understand your data structure and requirements
   - Document your initial data quality issues
   - Define acceptable values and ranges for your variables

2. CUSTOMIZATION POINTS:
   - Missing values: Adjust the filling strategy based on your data context
   - Outliers: Modify the IQR multiplier (1.5) based on your needs
   - Text cleaning: Add specific text cleaning rules for your case
   - Categories: Adjust the rare category threshold (currently 1%)
   - Sparse columns: Modify the missing value threshold (currently 70%)

3. BEST PRACTICES:
   - Always validate results after each cleaning step
   - Document any modifications made to the original template
   - Keep track of rows/values removed or modified
   - Consider the impact of each cleaning operation on your analysis

4. USAGE STEPS:
   1. Import this template
   2. Load your data
   3. Configure cleaning parameters
   4. Run the cleaning process
   5. Validate results
   6. Export cleaned data

5. VALIDATION CHECKLIST:
   - Check data types are correct
   - Verify missing values are handled appropriately
   - Confirm no unexpected nulls were introduced
   - Validate categorical variables are standardized
   - Review outlier treatment results

[PT-BR]
Guia do Template de Limpeza de Dados
----------------------------------

Este template fornece uma estrutura abrangente para limpeza de dados usando pandas.
Siga estas diretrizes ao usar este template:

1. ANTES DE USAR ESTE TEMPLATE:
   - Faça um backup dos seus dados originais
   - Compreenda a estrutura e requisitos dos seus dados
   - Documente os problemas iniciais de qualidade dos dados
   - Defina valores e intervalos aceitáveis para suas variáveis

2. PONTOS DE PERSONALIZAÇÃO:
   - Valores ausentes: Ajuste a estratégia de preenchimento baseado no contexto dos dados
   - Outliers: Modifique o multiplicador IQR (1.5) baseado em suas necessidades
   - Limpeza de texto: Adicione regras específicas de limpeza para seu caso
   - Categorias: Ajuste o limite para categorias raras (atualmente 1%)
   - Colunas esparsas: Modifique o limite de valores ausentes (atualmente 70%)

3. BOAS PRÁTICAS:
   - Sempre valide os resultados após cada etapa de limpeza
   - Documente quaisquer modificações feitas no template original
   - Mantenha registro das linhas/valores removidos ou modificados
   - Considere o impacto de cada operação de limpeza em sua análise

4. ETAPAS DE USO:
   1. Importe este template
   2. Carregue seus dados
   3. Configure os parâmetros de limpeza
   4. Execute o processo de limpeza
   5. Valide os resultados
   6. Exporte os dados limpos

5. CHECKLIST DE VALIDAÇÃO:
   - Verifique se os tipos de dados estão corretos
   - Confirme se os valores ausentes foram tratados apropriadamente
   - Confirme se não foram introduzidos nulos inesperados
   - Valide se as variáveis categóricas estão padronizadas
   - Revise os resultados do tratamento de outliers
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes column names by converting to lowercase, replacing spaces and special characters
    with underscores, removing leading/trailing underscores, and ensuring unique column names.
    
    [PT-BR]
    Padroniza os nomes das colunas convertendo para minúsculas, substituindo espaços e caracteres
    especiais por underscores, removendo underscores no início/fim e garantindo nomes únicos.
    
    Args:
        df (pd.DataFrame): Input DataFrame / DataFrame de entrada
        
    Returns:
        pd.DataFrame: DataFrame with standardized column names / DataFrame com nomes de colunas padronizados
    """
    df = df.copy()
    
    # Function to clean individual column names
    # Função para limpar nomes individuais de colunas
    def clean_column_name(col: str) -> str:
        col = col.lower()
        col = re.sub(r'[^a-z0-9]', '_', col)
        col = col.strip('_')
        col = re.sub(r'_+', '_', col)
        return col
    
    new_columns = [clean_column_name(col) for col in df.columns]
    
    # Handle duplicate column names by adding numbers
    # Tratar nomes de colunas duplicados adicionando números
    seen = {}
    for i, col in enumerate(new_columns):
        if col in seen:
            counter = seen[col]
            new_columns[i] = f"{col}_{counter}"
            seen[col] += 1
        else:
            seen[col] = 1
    
    df.columns = new_columns
    return df

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs comprehensive data cleaning on a pandas DataFrame
    
    [PT-BR]
    Realiza uma limpeza abrangente de dados em um DataFrame pandas
    
    Args:
        df (pd.DataFrame): Input DataFrame to be cleaned / DataFrame de entrada a ser limpo
        
    Returns:
        pd.DataFrame: Cleaned DataFrame / DataFrame limpo
    """
    
    # Create a copy to avoid modifying the original data
    # Criar uma cópia para evitar modificar os dados originais
    df_clean = df.copy()
    
    # Standardize column names (new step)
    # Padronizar nomes de colunas (novo passo)
    df_clean = standardize_column_names(df_clean)
    
    # 1. Remove duplicates
    # 1. Remover duplicatas
    df_clean = df_clean.drop_duplicates()
    
    # 2. Handle missing values
    # 2. Tratar valores ausentes
    def handle_missing_values(df):
        # Fill numeric columns with median
        # Preencher colunas numéricas com a mediana
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())
            
        # Fill categorical columns with mode
        # Preencher colunas categóricas com a moda
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")
            
        return df
    
    df_clean = handle_missing_values(df_clean)
    
    # 3. Fix data types
    # 3. Corrigir tipos de dados
    def fix_data_types(df):
        for col in df.columns:
            # Try to convert to numeric
            # Tentar converter para numérico
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except:
                    pass
                
                # Try to convert to datetime
                # Tentar converter para datetime
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass
        return df
    
    df_clean = fix_data_types(df_clean)
    
    # 4. Handle outliers using IQR method for numeric columns
    # 4. Tratar outliers usando o método IQR para colunas numéricas
    def handle_outliers(df, columns=None):
        if columns is None:
            columns = df.select_dtypes(include=['int64', 'float64']).columns
            
        for col in columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Cap the outliers
            # Limitar os outliers
            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        return df
    
    df_clean = handle_outliers(df_clean)
    
    # 5. Standardize text data
    # 5. Padronizar dados de texto
    def clean_text_data(df):
        text_cols = df.select_dtypes(include=['object']).columns
        
        for col in text_cols:
            # Convert to string type
            # Converter para tipo string
            df[col] = df[col].astype(str)
            
            # Remove leading/trailing whitespace
            # Remover espaços em branco no início/fim
            df[col] = df[col].str.strip()
            
            # Convert to lowercase
            # Converter para minúsculas
            df[col] = df[col].str.lower()
            
            # Remove special characters
            # Remover caracteres especiais
            df[col] = df[col].apply(lambda x: re.sub(r'[^\w\s]', '', x))
            
        return df
    
    df_clean = clean_text_data(df_clean)
    
    # 6. Remove columns with high percentage of missing values
    # 6. Remover colunas com alta porcentagem de valores ausentes
    def remove_sparse_columns(df, threshold=0.7):
        missing_percentages = df.isnull().sum() / len(df)
        columns_to_drop = missing_percentages[missing_percentages > threshold].index
        return df.drop(columns=columns_to_drop)
    
    df_clean = remove_sparse_columns(df_clean)
    
    # 7. Handle inconsistent categories
    # 7. Tratar categorias inconsistentes
    def standardize_categories(df):
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            # Get value counts
            # Obter contagem de valores
            value_counts = df[col].value_counts()
            
            # Find rare categories (less than 1% of data)
            # Encontrar categorias raras (menos de 1% dos dados)
            rare_categories = value_counts[value_counts / len(df) < 0.01].index
            
            # Replace rare categories with 'Other'
            # Substituir categorias raras por 'Other'
            df[col] = df[col].replace(rare_categories, 'Other')
            
        return df
    
    df_clean = standardize_categories(df_clean)
    
    return df_clean

def validate_data(df: pd.DataFrame) -> dict:
    """
    Validates the cleaned data and returns a summary of the cleaning process
    
    [PT-BR]
    Valida os dados limpos e retorna um resumo do processo de limpeza
    
    Args:
        df (pd.DataFrame): Cleaned DataFrame / DataFrame limpo
        
    Returns:
        dict: Validation summary / Resumo da validação
    """
    validation_summary = {
        'total_rows': len(df),
        'missing_values': df.isnull().sum().to_dict(),
        'data_types': df.dtypes.to_dict(),
        'unique_values': {col: df[col].nunique() for col in df.columns}
    }
    
    return validation_summary



# Example usage:
if __name__ == "__main__":
    # Load your data
    # Carregar seus dados
    # df = pd.read_csv('your_data.csv')
    
    # Clean the data
    # Limpar os dados
    # df_cleaned = clean_dataframe(df)
    
    # Validate the results
    # Validar os resultados
    # validation_results = validate_data(df_cleaned)
    
    # Export cleaned data
    # Exportar dados limpos
    # df_cleaned.to_csv('cleaned_data.csv', index=False)
    pass