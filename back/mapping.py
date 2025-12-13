import pandas as pd

def extraer_correos(campo):
    """
    Recibe una cadena del tipo:
        "azamora@fi.upm.es(ALFONSO ...)"
        "brios@fi.upm.es(...)-f.perozo@repsol.com(...)"
    Devuelve:
        [correo_tutor]  o  [correo_tutor, correo_cotutor]
    """
    if pd.isna(campo):
        return []

    partes = campo.split("-")   # separa tutor y cotutor si existe
    correos = []

    for parte in partes:
        correo = parte.split("(")[0]   # extrae lo que está antes de "("
        correo = correo.strip()
        if correo:
            correos.append(correo)

    return correos


def build_profesor_departamento(df_xls, path, filename):
    """
    Construye mapeo profesor → departamento a partir del Excel de disponibilidad.
    
    Args:
        df_xls (pd.ExcelFile): objeto ExcelFile con disponibilidad
        path (str): ruta a la carpeta
        filename (str): nombre del archivo
    
    Returns:
        tuple: (profesor_departamento dict, profesores_por_dpto dict)
    """
    profesor_departamento = {}
    profesores_por_dpto = {}
    for sheet in df_xls.sheet_names[:-1]:
        pf = pd.read_excel(path + filename, header=[0,1,2], sheet_name=sheet)
        keys_pf = pf.keys()
        lista = []
        for i in range(pf.shape[0]):
            correo = pf[keys_pf[1]][i]
            profesor_departamento[correo] = sheet
            lista.append(correo)
        profesores_por_dpto[sheet] = lista
    return profesor_departamento, profesores_por_dpto