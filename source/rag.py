
import os
from llama_index.core import (
    VectorStoreIndex, StorageContext, load_index_from_storage
)

from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

from llama_index.readers.file.rtf import RTFReader
from llama_index.readers.json import JSONReader

import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")

class Rag:

    class MyHandler(FileSystemEventHandler):

        def __init__(self, rag_instance):
            self.rag_instance = rag_instance

        def on_modified(self, event):
            with open(event.src_path, 'r') as file:
                self.rag_instance.glossary_index = self.rag_instance.load_index(self.rag_instance.glossary_file, 
                                             self.rag_instance.glossary_storage_dir, "json" )
                # Do something with the updated data

    def __watch_file(self,path):
        event_handler = Rag.MyHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


    root_dir = "./data"
    storage_dir = root_dir + "/index_storage"
    
    instruction_file = root_dir + "/rag_info.rtf"
    instruction_storage_dir = storage_dir + "/instruction_index"
    
    glossary_file = root_dir + "/glossary.json"
    glossary_storage_dir = storage_dir + "/glossary_index"
    
    def __init__(self):
        self._instruction_index = self.load_index(self.instruction_file, 
                                                   self.instruction_storage_dir,
                                                   "rtf" )
        self._glossary_index = self.load_index(self.glossary_file, 
                                             self.glossary_storage_dir,
                                             "json" )
        
        # Start file monitoring in a separate thread
        self._file_monitoring_thread = threading.Thread(target=self.__watch_file, args=(self.glossary_file,))
        self._file_monitoring_thread.daemon = True
        self._file_monitoring_thread.start()

    def __del__(self):
        # Cleanup tasks when the object is destroyed
        if hasattr(self, '_file_monitoring_thread') and self._file_monitoring_thread.is_alive():
            self._file_monitoring_thread.join()
    
    def load_index(self, filename, storage_dir, reader_type):

        try:
            # check if storage already exists
            #if not os.path.exists(storage_dir):
            # load the documents and create the index
            if reader_type == "rtf":
                reader = RTFReader()
            elif reader_type == "json":
                reader = JSONReader()
            
            documents = reader.load_data(filename)
            index = VectorStoreIndex.from_documents(documents)
            # store it for later
            #index.storage_context.persist(persist_dir=storage_dir)
            #else:
                # load the existing index
            #    storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
            #    index = load_index_from_storage(storage_context)
        except Exception as e:
            print("Error in Rag:__init__:", e)
            raise Exception("Error retrieving user specific content.")
        
        return index
        
    def get_content(self, query_str):
        retriever = self._instruction_index.as_retriever(similarity_top_k=1)
        retrieved_nodes = retriever.retrieve(query_str)
        
        content = retrieved_nodes[0].text + "\n\n\n"
        
        retriever = self._glossary_index.as_retriever(similarity_top_k=1)
        retrieved_nodes = retriever.retrieve(query_str)
        
        content += retrieved_nodes[0].text
        return content  
    
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
