
from source.prompt import context,instruction,predibase_cntxt
from source.rag import Rag
from source.sql_connect import SQLConnect
from source.prompt import Prompt
import openai
import os
import re
import time

from predibase import Predibase, PredibaseClient

openai_api_key = os.environ.get('OPENAI_API_KEY')
predibase_token = os.environ.get('PREDIBASE_TOKEN') 

class TextToSQL:
    
    def __init__(self):
        try:
            #self.pc = PredibaseClient(token=predibase_token)
            #self.pb = Predibase(api_token=predibase_token)
            pass
        except Exception as e:
            print("Error:", e)
        
        self.prompt = Prompt()
        self.rag = Rag()
        self.sql_conn = SQLConnect()
    
    def __del__(self):
        del self.rag
        del self.sql_conn
        
    def get_sql_statement(self, question, llm_model="gpt"):
        sql_stmt = ""
        rag_content = self.rag.get_content(question)

        if llm_model == "gpt":
            #print("rag content:", rag_content)
            query = self.prompt.create_query(question, rag_content)  
            print("get_sql_statement - Full Query:\n\n", query)  
            model = "gpt-4-0125-preview"
            response = self.get_completion(query,model)
            sql_stmt = self.__extract_sql(response)
        else: # we assume it is predibase
            print("Model Predibase")
            context = self.__create_predibase_context(rag_content)
            #sql_stmt = self.__get_predibase_response(question,context)
            sql_stmt = self.__get_new_pb_response(question,context)

        print("SQL Statement:\n",sql_stmt)
        return sql_stmt

    def __create_predibase_context(self, rag_content):
        
        #cntxt = instruction + """ 
        cntxt = """   
                For the following question please generate a sql statement based on the context. 
                
                ### Question : {} 
        
                ### Context: """ + predibase_cntxt + """

                """
        return cntxt

    def validate_query(self, query: str) -> dict:
        #print("Validating query")
        #words = self.__extract_words(query)
        words = self.__extract_word_using_llm(query)
        words = eval(words)
        word_dict = {}
        for w in words:
            # here we assume that if the word is matched to any of the column names
            # or to any of the keywords in the glossary file then it would successfully
            # generate a sql statment and we do not need to match it against the data 
            # in the database
            print("Word:\n",w)
            if self.__column_match(w) == False and self.rag.glossary_match(w) == False:
                # if the word does not match the column names and 
                # does not match the glossary keys then we need to 
                # see whether it matches data in one of the columns
                column_dict = {}
                
                # Record the start time
                #start_time = time.time()

                table_schemas = self.prompt.get_table_schemas()
                table_names = self.prompt.get_table_names()
                for table_name,table_schema in zip(table_names,table_schemas):
                    column_names = self.__get_column_names(table_schema)
                    #print("Column Names:",column_names)
                    #matched_columns = self.sql_conn.match_data(w,table_name, column_names)
                    matched_columns = self.sql_conn.match_data2(w,table_name, column_names)
                    #print("Matched Columns:", matched_columns)        
                    if len(matched_columns) > 0:
                        column_dict[table_name] = matched_columns
                
                # Record the end time
                #end_time = time.time()
                # Calculate the duration
                #duration = end_time - start_time
                #write_to_file("match_data2, duration:{}".format(duration))
                
                if len(column_dict) > 0:
                    word_dict[w] = column_dict
        word_dict = self.__validate_words_with_query(query, word_dict)
        return word_dict
    
    def __validate_words_with_query( self, query, word_dict):
        prompt = """
                    Does the query contain an explanation for the word {}, by providing context 
                     to any of the following: {}?. Make a case
                    insensitive comparison. Respond strictly with a "yes" or "no".
                    Also provide an explanation for choosing yes or no.

                    ### Query: {}

                    ### Response:
                """
        
        prompt2 = """
                    Does the query explain the meaning of the word {}, 
                    that relates it to any of the following words: {}?. 
                    Make a case insensitive comparison. Respond strictly with a "yes" or "no".
                    Also provide an explanation for choosing yes or no.

                    ### Query: {}

                    ### Response:
                """
        #print("Inside __validate_words_with_query for:\n",word_dict)

        word_dict_copy = word_dict.copy()
        for word,table_dict in word_dict.items():
            ref_list = ""
            for table_name,column_names in table_dict.items():
                ref_list += ", ".join(column_names)
                ref_list += ","
            ref_list = ref_list.rstrip(", ")

            final_prompt = prompt2.format(word,ref_list,query)
            print("Prompt for validation words context within query:\n",final_prompt)
            response = self.get_completion(final_prompt)
            print("Response:",response)
            if "yes" in response.lower():
                del word_dict_copy[word]
        #print("Final word dict:", word_dict_copy)
        return word_dict_copy

    def __get_column_names(self, table_schema):
        # Regular expression pattern to match column names, any subsequent addition of a different
        # column type should be catered in this pattern

        #column_pattern = r'([A-Za-z_]+)\s+(?:NUMBER|VARCHAR|TIMESTAMP_NTZ|BOOLEAN)'
        #column_names = re.findall(column_pattern, table_schema)
        
        # Use a regular expression to match column names preceded by the opening parenthesis 
        # or a comma and space, and followed by a space and any word characters
        column_names = re.findall(r'(?:\(|,\s*)(\b[A-Za-z_0-9]+\b)\s+\w+', table_schema)
        return column_names
    
    def __get_table_name(self, table_schema):
        # this pattern is as specified in the table schema
        pattern = r"Table Name: (\w+)"
        # Search for the table name in the string
        match = re.search(pattern, table_schema)
        # Extract the table name if a match is found
        table_name = ""
        if match:
            table_name = match.group(1)
        return table_name

    def __column_match(self, word): 
        table_schemas = self.prompt.get_table_schemas()   
        for table_schema in table_schemas:
            column_names = self.__get_column_names(table_schema)
            #print("Column Names for column match:",column_names)
            is_subword = any(word.lower() in col.lower() for col in column_names)
            if is_subword == True:
                #print("True for column match.")
                return True
        return False

    
    def __extract_words(self, sentence):
        from nltk.tokenize import word_tokenize
        from nltk.tag import pos_tag

        # Tokenize the sentence into words
        words = word_tokenize(sentence)
        # Tag each word with its part of speech
        tagged_words = pos_tag(words)
        print("Tagged Words:\n", tagged_words)

        # Filter out nouns (NN, NNS, NNPS, NNP)
        #nouns = [word for word, tag in tagged_words if tag.startswith('NN')]
        curr_idx = 0
        word_lst = []
        idx_lst = []
        for word,tag in tagged_words:
            if tag.startswith('NN'):
                if idx_lst and curr_idx == idx_lst[-1]+1:
                    word_lst[-1] = word_lst[-1] + " " + word
                    idx_lst.append(curr_idx)
                else:
                    word_lst.append(word)
                    idx_lst.append(curr_idx)
            curr_idx += 1
        return word_lst

    def __extract_word_using_llm(self, sentence):
        prompt = """
                        Consider the following sentence and retrieve all unique nouns.
                        If the nouns are together in the sentence then consider them as one word. 
                        In the end return a unique python list of the words. 

                        ### Query: """ + sentence + """

                        ### Response: 

                    """
        
        prompt2 = """
                        Consider the following sentence and retrieve all unique nouns.
                        If the nouns are adjacent to each other in the original sentence then consider 
                        them as a single word in the list. generate a python list with all nounse and
                        if they are adjacent to each other then consider them in the same word. 

                        ### Query: """ + sentence + """

                        ### Response: 

                    """

        prompt3 = """
                        Given a sentence, I want to extract all unique nouns. 
                        If two nouns are adjacent to each other, they should be combined 
                        into a single word. For example, in the sentence 
                        "What zip codes should I market to if I want to reach all 
                        customers in Knoxville, Tennessee?", 
                        the desired output would be ['zip codes', 'customers', 'Knoxville, Tennessee']. 
                        `Please implement this behavior.


                        ### Query: """ + sentence + """

                        ### Response: 

                    """        
        response = self.get_completion(prompt2)
        print("Response for unique nouns:",response)
        return response

    def __validate(self, query):
        prompt = """
                    Analyze the following query and respond with a "yes" if the above query can generate 
                    a valid snowflake sql statement using the table schema below, if the query is 
                    referring to values that do not match to any of the columns of the table below 
                    then respond with a "no":

                    ### Query: """ + query + """

                    ### Context: """ + context + """

                    ### Response: 

                """
        response = self.get_completion(prompt)
        if "yes" in response:
            return query
        # if the response is no retireve the column which contains that data
        prompt = """
                    Retrieve the column names which contain the data in the below query.
                """

    def get_completion(self, prompt, model="gpt-3.5-turbo"):
        
        messages = [{"role": "user", "content": prompt}]
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )
        #print("Prompt:\n",prompt)
        #print("The complete response:\n",response)
        return response.choices[0].message.content
        
    def __get_predibase_response(self, question, context):
        # we currently assume it is a predibase llm request
        # Since our model was fine-tuned from a Llama-2-7b base, we'll use the shared deployment with the same model type.
        #base_deployment = self.pc.LLM("pb://deployments/llama-2-7b")
        base_deployment = self.pc.LLM("pb://deployments/gemma-2b")
        #base_deployment = self.pc.LLM("pb://deployments/llama-3-8b")

        # Now we just specify the adapter to use, which is the model we fine-tuned.
        #model = self.pc.get_model("Llama-2-7b-hf-sql_create_context_v4")
        model = self.pc.get_model("gemma-2b-sql_create_context_v4")
        #model = self.pc.get_model("llama3_8b")
        adapter_deployment = base_deployment.with_adapter(model)
        
        # Recall that our model was fine-tuned using a template that accepts an {instruction}
        # and an {input}. This template is automatically applied when prompting.
        result = adapter_deployment.prompt(
            {
              "question": question,
              "context": context
            },
            max_new_tokens=256)
           
        return result.response

    def __get_new_pb_response(self, question, context):
        # Specify the serverless deployment of the base model which was fine-tuned
        lorax_client = self.pb.deployments.client("llama-3-8b")

        context = context.format(question)
        query = "<s>[INST]"+ context +  "[/INST] "
        print("Final Query:\n",query)

        response = lorax_client.generate(query, adapter_id="llama3_8b/1", max_new_tokens=512).generated_text
        print("New Predibase response:\n",response)

        return response
    
    def __extract_sql(self, sql_response):
        start_tag = '```sql'
        end_tag = '```'
        #if sql_with_tags.startswith(start_tag) and sql_with_tags.endswith(end_tag):
        #    return sql_with_tags[len(start_tag):-len(end_tag)].strip()
        start_tag_idx = sql_response.find(start_tag)
        end_tag_idx = sql_response.rfind(end_tag)
        if start_tag_idx != -1 and end_tag_idx != -1:
            return sql_response[start_tag_idx+len(start_tag):end_tag_idx].strip()
        else:
            return sql_response

    
def write_to_file(data):
    # Open the file in append mode if it exists, or create it if it doesn't exist
    with open("timing.txt", "a+") as file:
        # Move the cursor to the beginning of the file
        file.seek(0)
        # Read the contents of the file
        contents = file.read()
        # If the file is empty, write the data directly
        if not contents:
            file.write(data)
        else:
            # If the file is not empty, append a new line before writing the data
            file.write("\n" + data)

