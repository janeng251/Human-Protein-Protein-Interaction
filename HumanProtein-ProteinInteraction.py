import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

def retrieve_ppi_biogrid(target_protein):
    biogrid_url = "https://webservice.thebiogrid.org/interactions"
    params = {
        "accessKey": "2b065a842f2140bdd37acd828db09426",  # Replace with your valid API key
        "format": "json",
        "searchNames": True,
        "geneList": target_protein,
        "organism": 9606,  
        "searchbiogridids": True,
        "includeInteractors": True
    }
    response = requests.get(biogrid_url, params=params)
    network = response.json()
    network_df = pd.DataFrame.from_dict(network, orient='index')
    if not network_df.empty:
        network_df.OFFICIAL_SYMBOL_A = [gene.upper() for gene in network_df.OFFICIAL_SYMBOL_A]
        network_df.OFFICIAL_SYMBOL_B = [gene.upper() for gene in network_df.OFFICIAL_SYMBOL_B]
    return network_df

def retrieve_ppi_string(target_protein):
    string_url = "https://string-db.org/api/json/network"
    params = {
        "identifiers": target_protein,  
        "species": 9606  
    }
    response = requests.get(string_url, params=params)
    network = response.json()
    network_df = pd.json_normalize(network)
    return network_df
    
def generate_network(dataframe):
    global database_choice
    if database_choice == "STRING":
        column_a, column_b = "preferredName_A", "preferredName_B"
    else:
        column_a, column_b = "OFFICIAL_SYMBOL_A", "OFFICIAL_SYMBOL_B"
    network_graph = nx.from_pandas_edgelist(dataframe, column_a, column_b)
    return network_graph
   
def get_centralities(network_graph):
    centralities = {
        'Degree Centrality': nx.degree_centrality(network_graph),
        'Betweenness Centrality': nx.betweenness_centrality(network_graph),
        'Closeness Centrality': nx.closeness_centrality(network_graph),
        'Eigenvector Centrality': nx.eigenvector_centrality(network_graph),
        'PageRank Centrality': nx.pagerank(network_graph)
    }
    return centralities

st.title("Lab 2 - JANE NG JING YING")
st.header("Simple implementation of Human PPI retrieval from STRING or BioGRID")
protein_id = st.text_input("Enter protein ID:")
database_choice = st.selectbox("Select PPI DB", ["BioGRID", "STRING"])

if st.button("Retrieve"):
    if database_choice == "BioGRID":
        ppi_data = retrieve_ppi_biogrid(protein_id)
    else:
        ppi_data = retrieve_ppi_string(protein_id)

    if not ppi_data.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("PPI Data Information: ", protein_id)
            st.dataframe(ppi_data)

            st.subheader("Description of the network")
            network_graph = generate_network(ppi_data)
            st.write(f"Number of Nodes: {network_graph.number_of_nodes()}")
            st.write(f"Number of Edges: {network_graph.number_of_edges()}")
            
            centralities = get_centralities(network_graph)
            degree_centrality = centralities['Degree Centrality']
            highest_node = max(degree_centrality, key=degree_centrality.get)

            plt.figure(figsize=(10, 7))
            slayout = nx.spring_layout(network_graph, seed=123)
            nx.draw(network_graph, slayout, with_labels=True, node_size=1000, node_color='lightblue')
            nx.draw_networkx_nodes(network_graph, slayout, nodelist=[highest_node], node_size=1000, node_color='orange')
            st.pyplot(plt)

        with col2:
            st.subheader("Centrality Measures")
            if centralities:
                for name, values in centralities.items():
                    st.write(f"**{name}:**")
                    st.write(values)
