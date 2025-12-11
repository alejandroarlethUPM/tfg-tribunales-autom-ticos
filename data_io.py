import pandas as pd

def load_disponibilidad(path, filename="disponibilidad_TFG.xlsx"):
    """
    Carga el archivo Excel con disponibilidad de profesores.
    
    Args:
        path (str): ruta a la carpeta con los archivos
        filename (str): nombre del archivo de disponibilidad
    
    Returns:
        pd.ExcelFile: objeto ExcelFile con las hojas de disponibilidad por departamento
    """
    return pd.ExcelFile(path + filename)


def load_tfgs_por_dptos(path, filename="TFGs_por_dptos.xlsx"):
    """
    Carga el archivo Excel con TFGs agrupados por departamento.
    
    Args:
        path (str): ruta a la carpeta con los archivos
        filename (str): nombre del archivo de TFGs por departamento
    
    Returns:
        pd.ExcelFile: objeto ExcelFile con las hojas de TFGs por departamento
    """
    return pd.ExcelFile(path + filename)


def read_sheet(file, sheet_name, header=0):
    """
    Lee una hoja específica de un archivo Excel.
    
    Args:
        file (pd.ExcelFile or str): objeto ExcelFile o ruta al archivo
        sheet_name (str): nombre de la hoja a leer
        header (int or list): filas a usar como encabezados
    
    Returns:
        pd.DataFrame: DataFrame con los datos de la hoja
    """
    if isinstance(file, str):
        return pd.read_excel(file, sheet_name=sheet_name, header=header)
    else:
        return pd.read_excel(file, sheet_name=sheet_name, header=header)


def get_sheet_names(file):
    """
    Obtiene la lista de nombres de hojas de un archivo Excel.
    
    Args:
        file (pd.ExcelFile): objeto ExcelFile
    
    Returns:
        list: lista con nombres de hojas
    """
    return file.sheet_names


def get_column_by_index(df, col_index):
    """
    Obtiene una columna del DataFrame por índice.
    
    Args:
        df (pd.DataFrame): DataFrame
        col_index (int): índice de la columna
    
    Returns:
        pd.Series: serie con los datos de la columna
    """
    return df.iloc[:, col_index]


def get_cell(df, row_index, col_index):
    """
    Obtiene el valor de una celda específica.
    
    Args:
        df (pd.DataFrame): DataFrame
        row_index (int): índice de fila
        col_index (int): índice de columna
    
    Returns:
        valor en la celda
    """
    return df.iloc[row_index, col_index]


def get_num_rows(df):
    """
    Obtiene el número de filas de un DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame
    
    Returns:
        int: número de filas
    """
    return df.shape[0]


def get_num_columns(df):
    """
    Obtiene el número de columnas de un DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame
    
    Returns:
        int: número de columnas
    """
    return df.shape[1]