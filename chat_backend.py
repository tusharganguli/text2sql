

from t2sql import TextToSQL
from sql_connect import SQLConnect
from plot import GenPlot
from security import get_session_names

class ChatBackend:
    def __init__(self, app_cache):
        self.gplot = GenPlot() 
        self.cache = app_cache
        self.t2sql = None
        self.sql_conn = None

    # lazy initialization as we want the session name for initializing the objects.
    def set_session(self, session_name):
        self.t2sql = TextToSQL(session_name)
        self.sql_conn = SQLConnect(session_name)
    
    def __del__(self):
        del self.gplot
        del self.t2sql
        del self.sql_conn

    def get_session_names(self):
        return get_session_names()

        
    def get_data(self, user_query):
        stored_response = self.cache.get("response")
        self.cache.set("response","")
        if stored_response == "generate_sql_continue":
            try:
                stored_user_query = self.cache.get("user_query")
                #print("Stored query: {} \n new query:{}".format(stored_user_query, user_query))
                final_query = self.__rewrite_query(stored_user_query, user_query)
                print("Final Query:",final_query)
                sql_query = self.t2sql.get_sql_statement(final_query)
                #print("SQL Query:{}".format(sql_query))
                column_names,data = self.sql_conn.get_sql_data(sql_query)
            except Exception as err:
                print("Exception Raised in chat_backend.get_data:{}".format(err))
                print("SQL Query:{}".format(sql_query))
                return [{"error_msg": sql_query}]
            else:
                self.cache.set("column_names",column_names)
                self.cache.set("table_data",data)   
                table_data = [column_names] + data
                return [{"sql_query": sql_query},{"table_data": table_data}]

        chart_lst = self.gplot.get_chart_lst()
        system_prompt = """
                        if the user is asking about the list of available plots or charts, 
                        show the following list:""" + chart_lst + """ 
                
                        If the user is instructing to plot a specific chart or graph 
                        then return "plot_chart"
                        
                        If the user is asking to retrieve details or information then return the 
                        word "generate_sql".

                        ### User Query:
                    """
        final_prompt = system_prompt + user_query + "\n\n### Response: "
        response = self.t2sql.get_completion(final_prompt)
        #print("Response:",response)
        if "generate_sql" in response:
            try:
                #user_query = self.__formulate_query("generate_sql", user_query)
                word_dict = self.t2sql.validate_query(user_query)
                #print("Word Dictionary:\n",word_dict)
                if len(word_dict) != 0:
                    self.cache.set("response","generate_sql_continue")
                    self.cache.set("user_query", user_query)
                    return [{"word_mapping": word_dict}]
                sql_query = self.t2sql.get_sql_statement(user_query)
                #print("SQL Query:", sql_query)
                column_names,data = self.sql_conn.get_sql_data(sql_query)
            except Exception as err:
                print("Exception Raised:",err)
                print("SQL Query:", sql_query)
                return [{"error_msg": sql_query}]
            else:
                self.cache.set("column_names",column_names)
                self.cache.set("table_data",data)   
                table_data = [column_names] + data
                return [{"sql_query": sql_query},{"table_data": table_data}]
            
        elif "plot_chart" in response:
            column_names = self.cache.get("column_names")
            data = self.cache.get("table_data")
            if column_names == None:
                return [{"error_msg": "Graph cannot be generated for empty data."}]
            try:
                #user_query = self.__formulate_query("plot", user_query)
                chart_html,explanation = self.gplot.generate_graph(data,column_names,user_query)
                if chart_html == "":
                    msg =   "Could not understand the instructions. Can you please be more specific. \
                            If you are trying to plot a specific type of graph please indicate the columns \
                            for which you want to plot the graph."
                    return [{"error_msg": msg}]
            except Exception as err:
                return [{"error_msg": str(err)}]
            else:
                system_prompt = """
                        Please generate a concise explanation from the explanation below to explain the 
                        data used in x-axis and y-axis for genering this plot. Please keep the 
                        explanation limited to one or two sentence.
                        
                        ###Explanation: """ + explanation + """ 
                
                        ### Response:
                    """
                explanation = self.t2sql.get_completion(system_prompt)
                return [{"chart": chart_html},{"explanation": explanation}]
        elif "pie" in response:
            return [{"chart_lst": response}]
        else:
            #error_msg = "We cannot handle this request at the moment."
            return [{"error_msg": response}]

    def __rewrite_query( self, original_query, additional_instruction):
        prompt = """
                    Consider the original statement with the additional instruction and
                    respond with a new generated statement. Use the "where" keyword 
                    to regenerate the final statement in natural language. Refer to the example 
                    for a sample response. Do not generate SQL query only a sentence in natural language.
                    
                    ### Example: 
                    orignal statement: what is the current exposure to abc?
                    additional instruction: consider abc as an asset.
                    final response: What is the current exposure to abc where abc is an asset.

                    ### Original Statement: {}

                    ### Additional Instruction: {}

                    ### Response:
                """
        prompt = prompt.format(original_query, additional_instruction)
        final_query = self.t2sql.get_completion(prompt)

        return final_query

    def __formulate_query(self, curr_resp, query):
        prev_resp = self.cache.get("prev_resp")
        if prev_resp == curr_resp:
            prev_history = self.cache.get("prev_history")
            if curr_resp == "plot":
                chart_lst = self.gplot.get_chart_lst()
                system_prompt = """
                                If statement_2 is asking to plot a chart or graph from the following 
                                list: """ + chart_lst + """ then return the word "new_plot".
                                Otherwise consider statement_1 and statement_2 together and generate 
                                a concise statement which includes both the information in statement_1 
                                and statement_2.

                                ### statement_1: """ +  prev_history  + """

                                ### statement_2: 
                            """
            elif curr_resp == "generate_sql":
                system_prompt = """
                                Consider statement_1 and statement_2 together and generate a 
                                concise statement.

                                ### statement_1: """ +  prev_history  + """

                                ### statement_2: 
                            """   
            final_prompt = system_prompt + query + "\n\n ###Response: "
            new_query = self.__get_completion(final_prompt)

            if "new_plot" not in new_query:
                query = new_query
            #print("Refined Query:\n",query)
        else:
            self.cache.set("prev_resp", curr_resp)
        self.cache.set("prev_history", query)
        return query