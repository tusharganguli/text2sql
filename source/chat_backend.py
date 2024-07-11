

from source.t2sql import TextToSQL
from source.sql_connect import SQLConnect
from source.plot import GenPlot
from source.prompt import Prompt
from source.rag import Rag

class ChatBackend:
    def __init__(self, app_cache):
        self.gplot = GenPlot() 
        self.cache = app_cache
        self.t2sql = TextToSQL()
        self.sql_conn = SQLConnect()
        self.prompt = Prompt()
        self.rag = Rag()
        
    def __del__(self):
        del self.gplot
        del self.t2sql
        del self.sql_conn
        del self.prompt
        del self.rag
    
    def __generate_sql_and_get_result(self,user_query, view="normal"):
        try:
            word_dict = self.t2sql.validate_query(user_query)
            print("Word Dictionary:\n",word_dict)
            if len(word_dict) != 0:
                self.cache.set("response","generate_sql_continue")
                self.cache.set("user_query", user_query)
                return [{"word_mapping": word_dict}]
            sql_stmt_lst = self.t2sql.get_sql_statement(user_query, view)
            #print("SQL Query:", sql_query)
            sql_results = self.sql_conn.get_sql_data(sql_stmt_lst)
        except Exception as err:
            print("Exception Raised:",err)
            if sql_stmt_lst:
                #print("SQL Query:", sql_stmt_lst)
                return [{"error_msg": sql_stmt_lst}]
            else:
                return [{"error_msg": err}]
        else:
            self.cache.set("sql_results",sql_results)
            #print("SQL Results:",sql_results)
            column_names = sql_results[0]['columns']
            sql_data = [column_names]
            for result in sql_results:   
                sql_data += result['rows']
            self.cache.set("sql_data",sql_data)
        return sql_stmt_lst,sql_data
                       
    def get_data(self, user_query):
        stored_response = self.cache.get("response")
        self.cache.set("response","")
        if stored_response == "generate_sql_continue":
            try:
                stored_user_query = self.cache.get("user_query")
                #print("Stored query: {} \n new query:{}".format(stored_user_query, user_query))
                final_query = self.__rewrite_query(stored_user_query, user_query)
                print("Final Query:",final_query)
                sql_stmt_lst = self.t2sql.get_sql_statement(final_query)
                #print("SQL Query:{}".format(sql_query))
                sql_results = self.sql_conn.get_sql_data(sql_stmt_lst)
            except Exception as err:
                print("Exception Raised in chat_backend.get_data:{}".format(err))
                print("SQL statement:{}".format(sql_stmt_lst))
                return [{"error_msg": sql_stmt_lst}]
            else:
                table_data = []
                for result in sql_results:   
                    table_data += [result['columns']] + result['rows']
                return [{"sql_query": sql_stmt_lst},{"table_data": table_data}]

        chart_lst = self.gplot.get_chart_lst()
        system_prompt = """
                        if the user is asking about the list of available plots or charts, 
                        show the following list:""" + chart_lst + """ 
                
                        If the user is instructing to plot a specific chart or graph 
                        then return "plot_chart"
                        
                        If the user is asking to retrieve details or information then return the 
                        word "generate_sql".

                        If the user is asking the list of available dashboard views, show
                        the following list: "dashboard_lst" 

                        if the user is asking for generating a dashboard view then return the
                        word "dashboard_view"

                        ### User Query:
                    """
        final_prompt = system_prompt + user_query + "\n\n### Response: "
        response = self.prompt.get_completion(final_prompt)
        print("Response:",response)
        if "generate_sql" in response:
            sql_stmt_lst, sql_data = self.__generate_sql_and_get_result(user_query)
            return [{"sql_query": sql_stmt_lst},{"table_data": sql_data}]
        elif "plot_chart" in response:
            sql_data = self.cache.get("sql_data")
            if sql_data == None:
                return [{"error_msg": "Graph cannot be generated for empty data."}]
            
            column_names = sql_data[0]
            data = sql_data[1:]
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
                explanation = self.prompt.get_completion(system_prompt)
                return [{"chart": chart_html},{"explanation": explanation}]
        elif "pie" in response:
            return [{"chart_lst": response}]
        elif "dashboard_lst" in response:
            dashboard_lst = self.rag.get_dashboard_lst()
            dashboard_str = "Dashboard Names:" + ", ".join(dashboard_lst)
            return [{"dashboard_lst":dashboard_str}]
        elif "dashboard_view" in response:
            sql_stmt_lst, sql_data = self.__generate_sql_and_get_result(user_query, "dashboard")
            return [{"sql_query": sql_stmt_lst},{"table_data": sql_data}]
        else:
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
        final_query = self.prompt.get_completion(prompt)

        return final_query