import pandas as pd
import ast

errorlist=['Guo','Parapsychology','Archimedean','Economy','Information','Theory','V','Pharmacology','C','Earthquake','X','Art','Systemics','Cyberneticist','Face/Off','1954','9','Kanada','A','Analysis','analysis','Women in Chemistry','Biology','Tucker County, West Virginia','AWM/MAA Falconer Lecture','Gastonia (dinosaur)','Engineering','E','Autodynamics','Ecology','Zen','Psychology','Philosophy','Neuroscience','Cybernetics','Alchemy in the medieval Islamic world','Deaths in October 1987','Mars in fiction','Science in classical antiquity']
errorlistcontains=['science','University','Academy ','Dialogue Concerning','Members of ','&',' and ',' Fellowships ','medicine in','List of','Lists of','century','analysis','Analysis','(name)','County','Women in','Women of','Lecture','theory','American Society']

def prep_data(df,gender):
    df = df.sort_values(['Name', 'Year'])
    for word in errorlist:
        df=df[df['Name']!=word]
    for i in range(len(errorlistcontains)):
        df=df[~df['Name'].str.contains(errorlistcontains[i])]
    df['Links'] = df['Links'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    df = pd.merge(df,gender, on='Name', how='left')
    return df

def fill_missing_years(df):
    full_years = list(range(2004, 2025))
    new_rows = []
    
    for name, group in df.groupby('Name'):
        group = group.sort_values('Year')  
        
        existing_years = set(group['Year'])
        
        missing_years = sorted(set(full_years) - existing_years)
        
        for missing_year in missing_years:
            previous_year_data = group[group['Year'] < missing_year].tail(1)
            
            if not previous_year_data.empty:
                new_row = previous_year_data.iloc[0].copy()
                
                new_row['Year'] = missing_year
                
                new_rows.append(new_row)
    
    if new_rows:
        df_new_rows = pd.DataFrame(new_rows)
        df = pd.concat([df, df_new_rows], ignore_index=True)
    
    df = df.sort_values(['Name', 'Year']).reset_index(drop=True)
    
    return df


def prep_links(df_missing,gender):
    output_rows = []

    df = fill_missing_years(df_missing)

    for i in range(1, len(df)):
        current_row = df.iloc[i]
        previous_row = df.iloc[i-1]

        current_links = set(current_row['Links'])
        previous_links = set(previous_row['Links'])

        added_links = current_links - previous_links
        removed_links = previous_links - current_links

        for link in current_links:
            if link in added_links:
                output_rows.append([current_row['Name'], current_row['Year'], link, 'added'])
            else:
                output_rows.append([current_row['Name'], current_row['Year'], link, 'unchanged'])

        for link in removed_links:
            output_rows.append([current_row['Name'], current_row['Year'], link, 'removed'])

    df = pd.DataFrame(output_rows, columns=['Name', 'Year', 'Link', 'added_or_removed'])

    for i in range(len(errorlist)):
        df = df[df['Link'] != errorlist[i]]

    for i in range(len(df)):
        if i < len(df) and len(df.iloc[i]['Link']) == 1:
            df = df[df['Link'] != df.iloc[i]['Link']]

    for i in range(len(errorlist)):
        df = df[df['Link'] != errorlist[i]]

    for i in range(len(errorlistcontains)):
        df = df[~df['Link'].str.contains(errorlistcontains[i])]

    df = pd.merge(df, gender, on='Name', how='left')

    return df


