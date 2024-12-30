import networkx as nx

def create_directed_graph(df,genderdf):
    G = nx.DiGraph()
    
    for index, row in df.iterrows():
        source = row['Name']
        target = row['Link']
        status = row['added_or_removed']
        source_year=row['Year']
        source_gender = row['gender']
        target_gender=genderdf[genderdf['Name']==target]['gender']
        df_temp=df[df['Name']==target]
        targetlen=len(df_temp)
        df_temp=df[df['Name']==source]
        sourcelen=len(df_temp)

        if (status == 'added' or status == 'unchanged') and target!=source:
            if source not in G:
                G.add_node(source, gender=source_gender,year=source_year)
            if targetlen>0 or sourcelen>0:
                if target not in G:
                    G.add_node(target,gender=target_gender,year=source_year)
                G.add_edge(source, target)    

    return G