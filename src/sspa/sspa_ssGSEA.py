import pandas as pd
import sspa.utils as utils
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter

# for rpy2
base = importr('base')

def sspa_ssGSEA(mat, pathway_df, min_entity=2):

    """
    Barbie et al ssGSEA method for single sample pathway analysis. 
    This is an rpy2 wrapper script to run the R implementation of ssGSEA using the GSVA package.

    Args:
        mat (pd.DataFrame): pandas DataFrame omics data matrix consisting of m rows (samples) and n columns (entities).
        Do not include metadata columns
        pathways (pd.DataFrame): Dictionary of pathway identifiers (keys) and corresponding list of pathway entities (values).
        Entity identifiers must match those in the matrix columns
        min_entity (int): minimum number of metabolites mapping to pathways for ssPA to be performed


    Returns:
        pandas DataFrame of pathway scores derived using the ssGSEA method. Columns represent pathways and rows represent samples.
    """

    pathways = utils.pathwaydf_to_dict(pathway_df)
    compounds_present = mat.columns.tolist()
    pathways = {k: v for k, v in pathways.items() if len([i for i in compounds_present if i in v]) >= min_entity}

    with localconverter(ro.default_converter + pandas2ri.converter):
        r_mat = ro.conversion.py2rpy(mat.T)
    r_mat = base.as_matrix(r_mat)  # abundance matrix
    row_vec = base.as_character(mat.columns.tolist())
    r_mat.rownames = row_vec
    r_list = ro.ListVector(pathways)  # pathways
    gsva_r = importr('GSVA')
    ssgsea_res = gsva_r.gsva(r_mat, r_list, method='ssgsea')
    with localconverter(ro.default_converter + pandas2ri.converter):
        ssgsea_df = ro.conversion.rpy2py(ssgsea_res)
    ssgsea_res_df = pd.DataFrame(ssgsea_df.T, columns=pathways.keys(), index=mat.index.tolist())

    return ssgsea_res_df