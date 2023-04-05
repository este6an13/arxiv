import pymongo
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import networkx as nx
from nltk.stem import WordNetLemmatizer
import igraph as ig
import spacy

# load the English language model
nlp = spacy.load('en_core_web_sm')

tag = 'FL'

'''
# Create a lemmatizer object
lemmatizer = WordNetLemmatizer()

# download stopwords if not already downloaded
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# get a set of stopwords
stop_words = set(stopwords.words('english'))

'''

# establish a connection to the MongoDB server
client = pymongo.MongoClient("mongodb://localhost:27017/")

# create a new database and collection
db = client["arxiv"]
collection = db["arxiv"]

'''

# download the POS tagger if not already downloaded
nltk.download('averaged_perceptron_tagger')

# define the POS tags for technical words
tech_tags = ['NN', 'NNS', 'NNP', 'NNPS', 'JJ']

'''

# filter documents that have "cs.GT" in their "categories" attribute
regex = re.compile(f"cs\.{tag}")
query = {"categories": regex}
results = collection.find(query)

'''
# define regular expression to remove special characters and punctuation symbols
regex = re.compile('[^a-zA-Z0-9\s]')
'''

# open the output file in write mode
with open(f'cs{tag}/cs{tag}_links.txt', "w") as file:

    # iterate through the results and tokenize and tag the titles
    for doc in results:
        title = doc["title"]

        # apply NLP to extract noun phrases
        doc = nlp(title)
        noun_phrases = [chunk.text.lower().replace('(', '').replace(')', '').replace('\n', '') for chunk in doc.noun_chunks if chunk.root.pos_ not in ['PRON', 'AUX', 'DET', 'ADP', 'ADV', 'CONJ', 'CCONJ', 'INTJ', 'NUM', 'PART', 'PUNCT', 'SYM', 'SCONJ', 'VERB', 'X']]

        #words = word_tokenize(title.lower()) # convert to lowercase and tokenize
        #words = [w for w in words if w not in stop_words] # remove stopwords
        #words = [regex.sub('', w) for w in words] # remove special characters and punctuation symbols
        #words = [x for x in words if x]
        #tagged_words = pos_tag(words) # tag each word with its POS tag
        #tech_words = [w[0] for w in tagged_words if w[1] in tech_tags] # keep words with technical POS tags
        # Lemmatize the words
        #tech_words = [lemmatizer.lemmatize(word) for word in tech_words]

        # write pairs of words to the output file
        for i, w1 in enumerate(noun_phrases):
            for w2 in noun_phrases[i+1:]:
                file.write(w1 + " . " + w2 + "\n")

# WHOLE GRAPH

# create a new graph object
graph = nx.Graph()

# open the input file in read mode
with open(f'cs{tag}/cs{tag}_links.txt', "r") as file:

    # iterate over the lines in the file and add nodes and edges to the graph
    for line in file:
        words = line.strip().split(' . ')
        if len(words) == 2:
            word1, word2 = words
            if not graph.has_node(word1):
                graph.add_node(word1, frequency=1)
            else:
                graph.nodes[word1]["frequency"] += 1
            if not graph.has_node(word2):
                graph.add_node(word2, frequency=1)
            else:
                graph.nodes[word2]["frequency"] += 1
            if not graph.has_edge(word1, word2):
                graph.add_edge(word1, word2, weight=1)
            else:
                graph.edges[word1, word2]["weight"] += 1

# write the graph to the output file in GML format
nx.write_gml(graph, f'cs{tag}/cs{tag}_network.gml')

# TOP 1000 NODES SUBGRAPH

# load the graph from the input file
graph = nx.read_gml(f'cs{tag}/cs{tag}_network.gml')

# get a dictionary of {node: frequency} pairs
freq_dict = dict(graph.nodes(data="frequency"))

# sort the dictionary by frequency in descending order
sorted_dict = {k: v for k, v in sorted(freq_dict.items(), key=lambda item: item[1], reverse=True)}

# get the top 1000 nodes by frequency
top_nodes = list(sorted_dict.keys())[:1000]

# create a subgraph with only the top nodes and their edges
subgraph = graph.subgraph(top_nodes)

# write the subgraph to the output file in GML format
nx.write_gml(subgraph, f'cs{tag}/cs{tag}_network_top_nodes.gml')

# MOST IMPORTANT EDGES SUBRAPH: CURRENTLY NOT DONE

'''
g = ig.Graph.Read_GML(f"cs{tag}/cs{tag}_network_top_nodes.gml")
g.delete_edges(g.es.select(weight_gt=1))
ig.write(g, f"cs{tag}/cs{tag}_network_filtered.gml", format="gml")
'''