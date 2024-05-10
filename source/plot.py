
from chat2plot import chat2plot
import pandas as pd
#import spacy
import re
import json

chart_types_filename = "chart_types.json"

class GenPlot:
    
    def __init__(self):
        # Load the English language model
        #self.nlp = spacy.load("en_core_web_md")
        pass
    
    def generate_graph(self, data,column_names, plot_query=""):
        chart_html = ""
        try:
            df = pd.DataFrame(data, columns=column_names)
            c2p = chat2plot(df)
            #chart_types = self.__extract_chart_info(plot_query)
            final_query = plot_query
            result = c2p(final_query)
            if result.figure: 
                chart_html = result.figure.to_html(full_html=False)
        except Exception as e:
            print("Error in generate_graph:", e)
            raise Exception("Figure cannot be generated.")

        return chart_html,result.explanation

    def get_chart_lst(self):
      
        with open(chart_types_filename, 'r') as file:
            data = json.load(file)

        # Access the chart_types list
        chart_types = data['chart_types']

        # Initialize lists to store identified chart types and column names
        chart_lst = ",".join(str(c) for c in chart_types)
      
        # Tokenize the sentence
        #doc = self.nlp(sentence.lower())

        # Iterate over tokens and check for chart types and column names
        #for token in doc:
            # Check for chart types
            #for c in chart_types:
                #if re.search(c, token.text, re.IGNORECASE):
                    #print("inside if")
                    #chart_lst.append(c)
                
        return chart_lst



