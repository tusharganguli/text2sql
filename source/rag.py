
import os
import json
from flask import session
from llama_index.core import VectorStoreIndex,Settings,Document
from llama_index.llms.openai import OpenAI

Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")

class Rag:

    root_dir = "./data"
    storage_dir = root_dir + "/index_storage"
    glossary_file = root_dir + "/glossary.json"
    glossary_storage_dir = storage_dir + "/glossary_index"
    
    def __init__(self):

        self.__create_tmp_dir()
        self._glossary,self._instruction,self._dashboard = self.load_data(self.glossary_file)
        
        
    def __del__(self):
        del self._glossary_index

    def __create_tmp_dir(self):
        dir_path = './tmp'
        # Check if the directory exists
        if not os.path.exists(dir_path):
            # If not, create it
            os.makedirs(dir_path)

    def load_data(self, filename):
        try:
            # Load the JSON file
            with open(filename, "r") as f:
                data = json.load(f)
            
            session_name = session.get('session')

            session_data = ""
            if session_name in data:
                # Extract the data under the specific key
                session_data = data[session_name]

            #if session_data == "":
            #    index = VectorStoreIndex.from_documents(documents=[])
            #    return index
            
            #print("Session Data:\n",session_data)
            glossary = ""
            if "Glossary" in session_data:
                glossary_dict = session_data["Glossary"]
                for k,v in glossary_dict.items():
                    glossary += k + ":" + v + "\n"
            instruction = ""
            if "AdditionalInstructions" in session_data:
                instruction_dict = session_data["AdditionalInstructions"]
                for k,v in instruction_dict.items():
                    #print("instruction k:{},v:{}".format(k,v))
                    instruction += v + "\n\n"
            dashboard = []
            if "Dashboard" in session_data:
                dashboard = session_data["Dashboard"]

        except Exception as e:
            print("Error in Rag:__init__:", e)
            raise Exception("Error retrieving user json content.")
        
        print("Glossary:",glossary)
        print("Additional Instruction",instruction)
        #print("Dashboard:",dashboard)

        return glossary,instruction,dashboard
        
    def get_content(self, query_str):

        #print("Query String in rag.get_content:",query_str)
        
        #documents = []
        #for dashboard in self._dashboard:
        #    for k,v in dashboard.items():
        #        if k == "Name":  # Check if the name is not None or empty
        #            documents.append(Document(text=v))
        
        #print("Glossary documents:\n",documents)
        
        #index = VectorStoreIndex.from_documents(documents)
        #retriever = index.as_retriever(similarity_top_k=1)
        #retrieved_key = retriever.retrieve(query_str)
        
        #print("Retrieved key:", retrieved_key[0].text)

        static_content = self._glossary + "\n\n\n" + self._instruction + "\n\n\n"
        
        instruction = None
        #print("self._dashboard:\n",self._dashboard)
        query_lower = query_str.lower()

        for dashboard in self._dashboard:
            #print("dashboard[Name]:\n",dashboard["Name"])
            #print("Query:\n",query_str)
            dashboard_words = dashboard["Name"].split()
            match = True    
            for word in dashboard_words:
                if word.lower() not in query_lower:
                    match = False
                    break
            if match == True:
                instruction = dashboard["Instruction"]
                #print("selected dashboard:\n",dashboard)
                break
        #print("Instruction:\n",instruction)
        
        #dashboard = self._dashboard[retrieved_key[0].text.strip('"')]
        #print("Glossary Content:\n",glossary_content)
        instruction_lst = []
        if isinstance(instruction, dict):
            instruction_lst = list(instruction.values())
        else:
            instruction_lst = [instruction]
        #print("Instruction List:\n",instruction_lst)

        return static_content, instruction_lst
    
    def get_dashboard_lst(self):
        dashboard_lst = []
        for dashboard in self._dashboard:
            name = dashboard["Name"]
            #description = dashboard["Description"]
            dashboard_lst.append(name)
        return dashboard_lst
    
    def glossary_match(self, word):
        import json

        # Read the JSON file
        with open(self.glossary_file, 'r') as file:
            data = json.load(file)

        # Iterate over the items in the dictionary
        for key, value in data.items():
            if word in key or key in word:
                print("Returning true for glossary match")
                return True
        return False
