"""
Module for: 
- reading databases; 
- modifying them in case of merging or dropping rows. 
"""

import os
from pathlib import Path
import pandas as pd
import re


def merge_db(directory, show_merge, save_opt):
    """
    This function permits to read a db, modify its columns 
    and merge it with others. If you want, you can also drop
    patients looking at other dbs in case.

    :param directory: directory of the general analyses.
    :param show_merge: if true, all forms of databases are showed.
    :param save_opt: if true, merged or dropped row's databases are saved.
    
    """

    if "y" in show_merge.lower():
        show = True
        print("The showing option is set on: ", show)
    else:
        show = False
        print("The showing option is set on: ", show)
    
    if "y" in save_opt.lower():
        save = True
        print("The saving option is set on: ", save)
    else:
        save = False
        print("The saving option is set on: ", save)

    
    db_1 = read_db(directory, show)       
        
    for i in range(0, 100):
        print("")
        comb = str(input("Do you have a database that has to be merged?"))
        if "y" in comb.lower():                
            db_2 = read_db(directory, show)
            
            print("")
            merge_col_1 = str(input("Do you need to merge or modify first db columns for merging?"))
            if "y" in merge_col_1.lower():
                db_1 = merge_column(db_1, show)
                
            print("")
            merge_col_2 = str(input("Do you need to merge or modify the second db columns for merging?"))
            if "y" in merge_col_2.lower():
                db_2 = merge_column(db_2, show)

            db_1, dropped_in_df1, dropped_in_df2 = merge_df(db_1, db_2, show)
            save_merge(db_1, dropped_in_df1, dropped_in_df2, directory, save)
            
        else:
            dropped_db = drop_pz(db_1, directory, show)
            save_merge(dropped_db, dropped_in_df1, dropped_in_df2, directory, save)
            print("")
            print("You have finished.")
            break



def read_db(directory, show):   
    """
    This function permits to read a db into the directory path,
    matched by name.

    :param directory: directory of the general analyses.
    :param show: if true, all forms of databases are showed.

    :return df: database read.
    """
    
    for attempt in range(0, 100):
        print("")
        name = input("Insert the name of the database: ")        
        file_path = None        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if name in file:
                    file_path = os.path.join(root, file)
                    break

        if file_path is not None:
            print(f"The database is in: {file_path}")
            df = pd.read_excel(file_path)
            if show:
                display(df)
            
            print("")
            ok = input("Is this the file you were looking for? ").lower()
            if "y" in ok.lower():
                return df
            else:
                print("\nTry again.")
        else:
            print("")
            print(f"No Excel file found with the name '{name}'. Try again.")


def merge_column(df, show):    
    """
    This function permits to modify and drop db columns 
    for merging with other databases.

    :param df: database of which you want to modify columns for merging.
    :param show: if true, all forms of databases are showed.

    :return df: database modified.    
    """
    
    found_cols = match_column(df)
    
    df['LinkCol'] = ""    
    df['LinkCol'] = df.apply(lambda row: ''.join(map(lambda col: str(row[col[0]]), found_cols)), axis=1)
    
    df['LinkCol'] = df['LinkCol'].apply(lambda x: re.sub(r'[^a-zA-Z0-9]', '', x.lower()))
    print("")
    print("The new column for the merge is: ")
    display(df['LinkCol'])
    
    for i in range(0, 100):
        print("")
        delete = str(input("Do you want to delete anything from the column values? "))
        if "y" in delete.lower():
            pattern = str(input("What do you want to delete? "))
            df['LinkCol'] = df['LinkCol'].str.replace(pattern, '', regex=True).str.strip()
        else:
            print("")
            print("The column for the merge is: ")
            display(df['LinkCol'])
            break
                
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = df[cols]

    if show:
        display(df)

    df = drop_columns(df, show)
    
    return df


def match_column(df):
    """
    This function permits to match a specific number of columns 
    for merging with other databases.

    :param df: database of which you want to find columns for merging.

    :return found_cols: columns found for merging.    
    """
    
    print("The columns names are:")
    # print(df.columns.str.strip().str.lower())
    print(df.columns)

    print("")
    n_col = int(input("How many columns you have to modify? You can combine more than 1 of them. "))
    found_cols = []
    found = []
    
    for i in range(0, 100):
        if len(found_cols) != n_col:            
            if len(found) != 1:
                print("")
                col = str(input("Which column do you want to modify?"))        
                found = []
                for column in df.columns:
                    if col in column.strip():
                        found.append(column)
                        # break
                print("")
                print("I found these columns: ", found)
                   
            else:
                found_cols.append(found)
                found = []
        else:
            print("")
            print("I found these columns: ", found_cols)
            break

    return found_cols


def drop_columns(df, show):
    """
    This function permits to drop columns of a database.

    :param df: database of which you want to drop columns.
    :param show: if true, all forms of databases are showed.

    :return df: database without dropped columns.
    
    """
    
    print("")
    print("The columns names are:")
    print(df.columns)
    
    for i in range(0,100):
        print("")
        drop_col = str(input("Do you want to drop a column? "))
        if "y" in drop_col.lower():
            print("")
            print("The columns names are:")
            print(df.columns)

            print("")
            name_col = str(input("Insert the name of the column you want to drop: "))
            for column in df.columns:
                    if name_col in column.strip():
                        print("I matched the name: ", column)
                        df = df.drop(columns=column)
                        break
                    
        else:
            break
    
    if show:
        display(df)        
    
    return df


def merge_df(df1, df2, show):
    """
    This function permits to merge 2 databases.

    :param df1: left database you want to merge.
    :param df2: right database you want to merge.
    :param show: if true, all forms of databases are showed.

    :return merge: merged database.    
    """
    
    print("")
    print("The columns names of the left db are:")
    print(df1.columns)

    print("")
    print("The columns names of the right db are:")
    print(df2.columns)
    
    print("")
    name_col_sx = str(input("Which column you want to merge left db on?"))
    for column in df1.columns:
        if name_col_sx in column.strip():
            print("I matched the name: ", column)
            df1['LinkCol'] = df1[column].astype(str)
            df1 = df1.sort_values(by='LinkCol', ascending=True).reset_index(drop=True)
            break

    print("")
    name_col_dx = str(input("Which column you want to merge right db on?"))
    for column in df2.columns:
        if name_col_dx in column.strip():
            print("I matched the name: ", column)
            df2['LinkCol'] = df2[column].astype(str)
            df2 = df2.sort_values(by='LinkCol', ascending=True).reset_index(drop=True)
            break
                        
    merged_in = pd.merge(df1, df2, on=['LinkCol'], how='inner')

    merged_out = pd.merge(df1, df2, on=['LinkCol'], how='outer', indicator=True)
    # Selezionare le righe che sono presenti solo in uno dei DataFrame
    dropped_in_df1 = merged_out[merged_out['_merge'] == 'left_only'].drop('_merge', axis=1)
    dropped_in_df2 = merged_out[merged_out['_merge'] == 'right_only'].drop('_merge', axis=1)
    
    if show:
        display(merged_in)
        # Stampa le righe mancanti in ciascun DataFrame
        print("Dropped rows in df1:")
        display(dropped_in_df1)

        print("\nDropped rows in df2:")
        display(dropped_in_df2)
    
    merge = drop_columns(merged_in, show)
    
    return merge, dropped_in_df1, dropped_in_df2
    

def save_merge(df, dropped_in_df1, dropped_in_df2, directory, save):
    """
    This function permits to save a database.

    :param df: database you want to save.
    :param directory: directory of the general analyses.
    :param save: if true, merged or dropped row's databases are saved.
    """
    
    if save:
        dir_merge = Path(directory) / "Merged_db"
        Path(dir_merge).mkdir(exist_ok=True, parents=True)

        print("")
        name = str(input("Which is the name of these merged dataframes? "))
        
        print('')
        print(f'Saving the merged database {name} with not matched rows in {dir_merge}.')
        with pd.ExcelWriter(dir_merge / f'{name}.xlsx') as writer:
            df.to_excel(writer, sheet_name="matched_rows", index=False)
            dropped_in_df1.to_excel(writer, sheet_name="left_db_rows_not_in_right_one", index=False)
            dropped_in_df2.to_excel(writer, sheet_name="right_db_rows_not_in_left_one", index=False)



def drop_pz(df_tot, directory, show):
    """
    This function permits to drop database rows looking at other database values.

    :param df_tot: database whose rows you want to drop.
    :param directory: directory of the general analyses.
    :param show: if true, all forms of databases are showed.

    :return df_tot: database whose rows you have dropped.
    """
    
    # ['BERTOGLIO, ALDINA' , 'SIGNORELLI, PAOLA' , 'MANINCHEDDA, SILVANA' , 'GOMES, IZABEL CRISTINA', 'SALA, PAOLA']
    # ['70263936', '70102927', '70362000', 50242541, 12484472]
    
    print("")
    drop_or_no = str(input("Do you want to drop patients from the merged db?"))
    if "y" in drop_or_no.lower():

        if 'y' in str(input(f"\nDo you want to drop all patients from a column of another db?")).lower():
            print("The columns names of the db merged are:")
            print(df_tot.columns)
                
            column_tot = search_col(df_tot, show)
            
            print("\nNow you are looking for the db whose values will be dropped from the merged one.")
            df_drop = read_db(directory, show)
            print("")
            print("The columns names from the drop db are:")
            print(df_drop.columns)
    
            column_drop = search_col(df_drop, show)
            
            df_tot = df_tot[~df_tot[column_tot].isin(df_drop[column_drop])]
            print('')
            print(f"Dropping all patients with values in column {column_drop} present in the db tot.")
            print("")
            display(df_tot)
        
        else:
            for check_row in range(0, 100):
                value_drop=None
                
                print("The columns names of the db merged are:")
                print(df_tot.columns)                
                column_tot = search_col(df_tot, show)

                print("\nNow you are looking for the db whose values will be dropped from the merged one.")
                df_drop = read_db(directory, show)
                print("")
                print("The columns names from the drop db are:")
                print(df_drop.columns)        
                column_drop = search_col(df_drop, show)

                value_tot = search_value(df_tot, column_tot)

                values_db_2 = df_drop[column_drop].astype(str).values.tolist()
                print(f"\nThese are the values of the column {column_drop} you chose from the checking db.")
                display(values_db_2)
                print('')
        
                
                value_drop = value_tot
                if value_drop is not None:
                    row_drop = str(input(f"\nDo you want to drop the row of the column {column_tot} where {value_drop} is?"))
                    if "y" in row_drop.lower():
                        print("\nYou found the value.")
                        df_tot = df_tot[df_tot[column_tot].astype(str) != value_drop]
                        display(df_tot)
                        if "y" in str(input("\nHave you finished? ")):
                            break
                        else:
                            print("\nYou are continuing.")
                    else:
                        print("\nTry again in values.")
                else:
                    print("")
                    print(f"No values found with the name '{value_drop}'. Try again.")
        
        print("\nYou have finished.")
        display(df_tot)
    
    else:
        print('')
        print("You chose to not drop patients.")

    return df_tot


def search_col(df, show):
    """
    This function permits to match a specific column in a database. 

    :param df: database of which you want to find column by name.
    :param show: if true, the column is showed.

    :return column_found: column found.    
    """
    
    for attempt in range(0, 100):
        print("")
        name_col = str(input("Insert the name of the column whose value you want to drop: "))
        column_found=None
        for column in df.columns:
            if name_col in column.strip():
                column_found = column
                print("I matched the name: ", column_found)                
                break
        
        if column_found is not None:
            if show:
                display(df[column_found])
            
            print("")
            ok = input("Is this the column you were looking for? ")
            if "y" in ok.lower():
                print("\nYou found the column.")
                break
            else:
                print("\nTry again.")
        else:
            print("")
            print(f"No column found with the name '{name_col}'. Try again.")

    return column_found


def search_value(df, column_found):
    """
    This function permits to match a specific value in a database. 

    :param df: database of which you want to find value by name.
    :param column_found: column of which you want to find a value.

    :return value_tot: value found.    
    """
    
    for attempt_row in range(0, 100):
        values = df[column_found].astype(str).values.tolist()
        print(f"\nThese are the values of the column {column_found} you chose from the dropping db.")
        display(values)
        print('')
        name_value_drop = str(input("Insert the value's row you want to drop: "))
        value_tot=None
        for value in values:
            if name_value_drop in value:
                value_tot = value
                print("I matched the value: ", value_tot)                
                break
        
        if value_tot is not None:
            print("")
            ok = input("Is this the value you were looking for? ")
            if "y" in ok.lower():
                print("\nYou found the value.")
                break                   
            else:
                print("\nTry again in values.")
        else:
            print("")
            print(f"No values found with the name '{value_tot}'. Try again.")

    return value_tot