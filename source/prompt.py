
from flask import session
import json
import yaml
import openai
import os

openai_api_key = os.environ.get('OPENAI_API_KEY')
class Prompt:
    #-- If some words do not make sense in the question, ask the user politely for clarification and do not generate any sql query.
	#-- Only if the question is a compound sentence break it into independent clauses which stand as complete sentences, otherwise consider the full question.
	#-- For each independent clause generate the sql queries in bullet point format. Start each query in a new line.
	# -- for previous month extract the current month from today's date. use it to get the previous month. then generate a range between the start date and end date of the previous month.

	instruction = """
		You are a powerful text-to-SQL model. You are participating in a 
		competition to convert text to snowflake sql. You have to get all 
		questions right otherwise we will loose.
		The margin for error is zero. Below are some guidelines for you to 
		generate accurate sql queries.

		#### Instructions:
		-- If the query does not make sense please ask the user politely to rephrase the question.
		-- Generate only snowflake SQL query if possible for the question following the 'Question:' tag  using the context following the 'Context:' tag.
		-- the sql statement generated should refer to the table schemas in this prompt.
		-- for dates use snowflake functions to generate actual dates in the sql queries. 
		-- for previous month extract the current month from today's date. use it to get the previous month. then generate a range between the start date and end date of the previous month.
		-- use relevant columns specified in the table schema in the context below.
		-- highest means to order by descending and lowest mean order by ascending.
		-- if any of the following keywords are used for matching data: 
			any, contains,matching, matches,similar to,includes,has,with - use snowflake sql statements for similarity matching with the data 
		-- resolve any ambiguity for displaying the columns based on foreign key relation of the tables specified in the context.
		-- use a foreign key only if it is required.
		-- when querying the tables match the column which is the closest match in the query.
		-- If generating data across table needs a union operation then perform a union of tables only if the number of columns retrieved from all the tables is equal or else use foreign key relationship to get data from all tables.
		-- If using a where clause to compare data, use ILIKE to make the comparison.
		-- When constructing SQL queries with a WHERE clause, please ensure that you use a case-insensitive similarity comparison using ILIKE, for example: WHERE column_name ILIKE '%word%'
		"""

	def __init__(self):
		self.session_name = session.get('session')
		self.yml_file = "./data/table_schemas.yml"
		self.prompt_file = "./data/prompt.yml"
	
	def __rewrite_query( self, initial_query, main_query):
		prompt = """
			append initial query as a preamble to the main query to generate a single statement
			in natural language. keep the main query intact and do not change it. 

			### initial query: {}

			### main query: {}

			### Response:
		"""
		prompt = prompt.format(initial_query, main_query)
		final_query = self.get_completion(prompt)

		return final_query

	def get_completion(self, prompt, model="gpt-3.5-turbo"):
        
		messages = [{"role": "user", "content": prompt}]
		response = openai.chat.completions.create(
			model=model,
			messages=messages,
			temperature=0,
		)
		return response.choices[0].message.content

	def get_response(self, system_prompt, user_prompt, model="gpt-3.5-turbo"):
        
		messages = [
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_prompt}
			]
		response = openai.chat.completions.create(
			model=model,
			messages=messages,
			temperature=0,
		)
		return response.choices[0].message.content

	def create_system_prompt(self, instruction):
		table_schemas = self.get_table_schemas()
		table_schema_str = '\n\n'.join(table_schemas)

		foreign_keys = self.__get_foreign_keys()
		table_schema_str += foreign_keys

		system_prompt = self.instruction + """ 

				The following is the context.

				### Context: The following is the detail information of tables in a schema.
				""" + table_schema_str + """
		
				The following is additional information to be taken into 
				account:
				
				### Information: """ + instruction + """

				"""
		return system_prompt
	
	def create_query(self, question, dashboard_list, view):
		
		#print("Session Name:", self.session_name)
		query_lst = []
		query = """ 		
				### Question: {}
		
				### Response:

				""" 
		print("View:",view)
		#print("dashboard_lst:\n",dashboard_list)
		if view == "dashboard" and dashboard_list:
			for dashboard in dashboard_list:
				#print("dashboard:",dashboard)
				rewritten_question = self.__rewrite_query(question,dashboard)
				formatted_query = query.format(rewritten_question)
				#print("Query:\n",query)
				query_lst.append(formatted_query)
		else:
			formatted_query = query.format(question)
			#print("Query:\n",query)
			query_lst.append(formatted_query)
		
		return query_lst
	    
	def get_table_schemas(self):
		# Load the YAML file
		with open(self.yml_file, 'r') as file:
			data = yaml.safe_load(file)

		#print("YAML file data:\n",data)
		# Extract the CREATE TABLE schemas
		tables_data = data.get(self.session_name, {}).get('Tables', {})
		table_schemas = []
		for table_name, schema in tables_data.items():
			table_schemas.append(schema)

		return table_schemas

	def __get_foreign_keys(self):
		# Load the YAML file
		with open(self.yml_file, 'r') as file:
			data = yaml.safe_load(file)

		# Extract the Foreign Key relationships
		foreign_keys = data.get(self.session_name, {}).get('Foreign Keys', '')

		return foreign_keys
	
	def get_table_names(self):
		with open(self.yml_file, 'r') as file:
			data = yaml.safe_load(file)

		# Get the tables data for the specified session
		tables_data = data.get(self.session_name, {}).get('Tables',{})

		table_names = []
		# Iterate over tables data
		for table_name, schema in tables_data.items():
			table_names.append(table_name)

		#print("Table Names:\n",table_names)
		return table_names
	

