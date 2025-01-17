import requests
import pandas as pd
import numpy as np

def identifier_conversion(input_type, compound_list):
    """
    Use Metaboanalyst API for identifier conversion
    Args:
        input_type (str): identifier type present in input data - any of ('name', 'hmdb', 'pubchem', 'chebi', 'metlin', 'kegg')
        compound_list (list): list of identifiers in the data
    Returns:
        (pd.DataFrame) Dataframe containing identifier matches 
    """
    print('Commencing ID conversion using Metaboanalyst API...')
    
    url = "https://www.xialab.ca/api/mapcompounds"

    compound_list_string = ";".join(compound_list)
    payload = f"{{\n\t\"queryList\": \"{compound_list_string};\",\n\t\"{input_type}\": \"name\"\n}}"
    headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache",
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    resp_dict = response.json()
    df_res = pd.DataFrame(resp_dict)
    return df_res

def map_identifiers(query_df, output_id_type, matrix):
    """
    Map desired identifiers to input data
    Args:
        query_df (pd.DataFrame): DataFrame obtained using the identifier_conversion function containing ID mappings
        output_id_type (str): Any of ('Match', 'HMDB', 'PubChem', 'ChEBI', 'KEGG', 'METLIN','SMILES')
        matrix (pd.DataFrame): sample-by-compound metabolomics data matrix
    Returns:
        Sample-by-compound metabolomics data matrix with mapped identifiers, any compounds without a matching ID will be dropped
    """


    # output id type can be any of ['HMDB', 'PubChem', 'ChEBI', 'KEGG', 'METLIN','SMILES']
    cpd_mapping_dict = dict(zip(query_df["Query"].tolist(), query_df[output_id_type].tolist()))
    cpd_mapping_dict = {k: v for k, v in cpd_mapping_dict.items() if v not in ["NA", np.nan, None, "None"]}
    renamed_mat = matrix.drop([i for i in matrix.columns if i not in cpd_mapping_dict.keys()], axis=1)
    renamed_mat = renamed_mat.rename(cpd_mapping_dict, axis=1)
    return renamed_mat
