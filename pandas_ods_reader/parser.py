"""Imports an ods file into a DataFrame object"""
import ezodf
import pandas as pd

from .tools import sanitize_df


def load_ods(doc, sheet, headers=True, columns=None):
    # convert the sheet to a pandas.DataFrame
    if isinstance(sheet, int):
        sheet = doc.sheets[sheet - 1]
    elif isinstance(sheet, str):
        sheets = [sheet.name for sheet in doc.sheets]
        if sheet not in sheets:
            raise ValueError("There is no sheet named {}".format(sheet))
        sheet_idx = sheets.index(sheet)
        sheet = doc.sheets[sheet_idx]
    df_dict = {}
    col_index = {}
    for i, row in enumerate(sheet.rows()):
        # row is a list of cells
        if headers and i == 0 and not columns:
            # columns as lists in a dictionary
            df_dict = {cell.value: [] for cell in row if cell.value}
            # create index for the column headers
            col_index = {
                j: cell.value for j, cell in enumerate(row) if cell.value}
            continue
        elif i == 0:
            columns = columns if columns else (
                ["column_%s" % j for j in range(len(row))])
            # columns as lists in a dictionary
            df_dict = {column: [] for column in columns}
            # create index for the column headers
            col_index = {j: column for j, column in enumerate(columns)}
            if headers:
                continue
        for j, cell in enumerate(row):
            if j < len(col_index):
                # use header instead of column index
                df_dict[col_index[j]].append(cell.value)
            else:
                continue
    # convert lists to pd.Series
    df_series = {}
    for col  in df_dict.keys():
        df_series[col] = pd.Series(df_dict[col])
    # and convert to a DataFrame
    df = pd.DataFrame(df_series)
    return df


def read_ods(file_or_path, sheet, headers=True, columns=None):
    """
    This function reads in the provided ods file and converts it to a
    dictionary. The dictionary is converted to a DataFrame. Empty rows and
    columns are dropped from the DataFrame, before it is returned.

    :param file_or_path: str
    the path to the ODS file
    :param sheet: int or str
    if int, the 1 based index of the sheet to be read in. If str, the name of
    the sheet to be read in
    :param header: bool, default True
    if True, the first row is read in as headers
    :param columns: list, default None
    a list of column names to be used as headers
    :returns: pandas.DataFrame
    the ODS file as a pandas DataFrame
    """
    doc = ezodf.opendoc(file_or_path)
    df = load_ods(doc, sheet, headers, columns)
    return sanitize_df(df)
