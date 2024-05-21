
from flask import session
import json

class Prompt:
    
	def __init__(self):
		self.session_name = session.get('session')
		self.json_file = "./data/table_schemas.json"
        
	def create_query(self, question, rag_content):
		table_schemas = self.get_table_schemas()
		table_schema_str = '\n\n'.join(table_schemas)

		print("Session Name:", self.session_name)

		if "franklin" in self.session_name.lower():
			table_schema_str += "\n\n" + ft_foreign_key
		elif "zip" in self.session_name.lower():
			table_schema_str += "\n\n" + us_zip_code_table_descriptions
			table_schema_str += "\n\n" + us_zip_code_foreign_key
		elif "covid" in self.session_name.lower():
			if "cdc"  in self.session_name.lower():
				table_schema_str += "\n\n" + covid_cdc_foreign_keys
			else:	
				table_schema_str += "\n\n" + covid_foreign_keys
		else:
			print("Warning: No foreign key relationship specified")
		
		query = instruction + """ 
				
				### Question: """ + question + """
				
				The following is the context.

				### Context: The following is the detail information of tables in a schema.
				""" + table_schema_str + """

				The following is additional information to be taken into 
				account:
				
				### Information: """ + rag_content + """

				### Response:

				""" 
		#print("Table Schemas:\n",table_schemas)
		#query = query.format(table_schemas)
		return query	
		
	def get_table_schemas(self):
		
		# Load JSON data from schema.json file
		with open(self.json_file, 'r') as f:
			data = json.load(f)

		# Get the tables data for the specified session
		tables_data = data.get(self.session_name, {})

		create_table_schema = []
		# Iterate over tables data
		for table_name, create_statement in tables_data.items():
			create_table_schema.append(create_statement)
		return create_table_schema
	
	def get_table_names(self):
		with open(self.json_file, 'r') as f:
			data = json.load(f)
		
		# Get the tables data for the specified session
		tables_data = data.get(self.session_name, {})

		table_names = []
		# Iterate over tables data
		for table_name, create_statement in tables_data.items():
			table_names.append(table_name)
		return table_names
	
table1 = """    
    Table Name: INSTRUMENTS
    Schema: DW_DEV.FT
    create or replace TABLE INSTRUMENTS (
	INSTRUMENT_ID VARCHAR(16777216),
	ASSET_NAME VARCHAR(255),
	ISSUER VARCHAR(255),
	INSTRUMENT_TYPE VARCHAR(255)
    );

    """ 

table2 = """
    
    Table Name: FACTORS
    Schema: DW_DEV.FT
    
    create or replace TABLE FACTORS (
	AS_OF_DATE TIMESTAMP_NTZ(9),
	ACCT VARCHAR(16777216),
	BENCHMARK VARCHAR(16777216),
	FACTOR_PARENT VARCHAR(255),
	ISTOTALROW BOOLEAN,
	RISK_SOURCE VARCHAR(255),
	PORTFOLIO_RISK NUMBER(38,6),
	PCT_PORTFOLIO_RISK NUMBER(38,6),
	BENCHMARK_RISK NUMBER(38,6),
	PCT_BENCHMARK_RISK NUMBER(38,6),
	ACTIVE_RISK NUMBER(38,6),
	PCT_ACTIVE_RISK NUMBER(38,6),
	PORTFOLIO_RISK_CONTRIBUTION NUMBER(38,6),
	ACTIVE_PORTFOLIO_RISK_CONTRIBUTION NUMBER(38,6),
	PORTFOLIO_CORRELATION NUMBER(38,6),
	ACTIVE_PORTFOLIO_CORRELATION NUMBER(38,6),
	PORTFOLIO_VARIANCE NUMBER(38,6),
	BENCHMARK_VARIANCE NUMBER(38,6),
	ACTIVE_VARIANCE NUMBER(38,6)
    );
    
    """ 

table3 = """
    
    Table Name: POSITIONS_AND_BENCHMARK
    Schema: DW_DEV.FT
    
    create or replace TABLE POSITIONS_AND_BENCHMARK (
	AS_OF_DATE TIMESTAMP_NTZ(9), 
	ACCT VARCHAR(16777216),
	BENCHMARK VARCHAR(16777216),
	INSTRUMENT_ID VARCHAR(16777216),
	ACTIVE_CORRELATION NUMBER(38,6),
	ACTIVE_COMMODITY_CONTRIBUTION NUMBER(38,6),
	ACTIVE_COUNTRY_CONTRIBUTION NUMBER(38,6),
	ACTIVE_CURRENCY_RISK_CONTRIBUTION NUMBER(38,6),
	ACTIVE_EMERGING_MARKET_CONTRIBUTION NUMBER(38,6),
	ACTIVE_HEDGE_FUND_CONTRIBUTION NUMBER(38,6),
	ACTIVE_INDUSTRY_CONTRIBUTION NUMBER(38,6),
	ACTIVE_MKT_TIMING_RISK_CONTRIBUTION NUMBER(38,6),
	ACTIVE_SPECIFIC_CONTRIBUTION NUMBER(38,6),
	ACTIVE_SPREAD_CONTRIBUTION NUMBER(38,6),
	ACTIVE_STYLE_CONTRIBUTION NUMBER(38,6),
	ACTIVE_TERM_STRUCTURE_CONTRIBUTION NUMBER(38,6),
	ACTIVE_WORLD_CONTRIBUTION NUMBER(38,6),
	ACTIVE_RISK_CONTRIBUTION NUMBER(38,6), 
	PORT_RISK_CONTRIBUTION NUMBER(38,6),
	ACTIVE_RESI_EFF_WGT_PCT NUMBER(38,6),
	ACTIVE_TOTAL_RISK NUMBER(38,6),
	MC_TO_ACTIVE_TOTAL_RISK NUMBER(38,6),
	MC_TO_TOTAL_TRACKING_ERROR NUMBER(38,6),
	PCT_CR_TO_ACTIVE_LOCAL_MKT_RISK NUMBER(38,6),
	PCT_CR_TO_ACTIVE_TOTAL_RISK NUMBER(38,6),
	PCT_CR_TO_TOTAL_TRACKING_ERROR NUMBER(38,6), 
	BETA_BMK NUMBER(38,6),
	CORRELATION NUMBER(38,6),
	MC_TO_TOTAL_RISK NUMBER(38,6),
	PCT_CR_TO_TOTAL_RISK NUMBER(38,6),
	TOTAL_RISK NUMBER(38,6),
	ACTIVE_WEIGHT_PCT NUMBER(38,6),
	BMK_WEIGHT_PCT NUMBER(38,6),
	EFF_ACTIVE_WGT_PCT NUMBER(38,6),
	EFF_BMK_WGT_PCT NUMBER(38,6),
	EFF_GLOBAL_WEIGHT_PCT NUMBER(38,6),
	EFF_WGT_PCT NUMBER(38,6),
	WEIGHT_PCT NUMBER(38,6),
	BMK_ASSET_NOT_HELD VARCHAR(255),
	GICS_IND VARCHAR(255),
	GICS_IND_GRP VARCHAR(255),
	GICS_SECTOR VARCHAR(255),
	GICS_SUBIND VARCHAR(255),
	CNTRY_OF_RISK VARCHAR(255),
	COMPANY_RATING VARCHAR(255)
    );
"""

ft_foreign_key = """
    
    Foreign Key Relationships:
    -- ACCT in POSITIONS_AND_BENCHMARK references ACCT in FACTORS.
    -- BENCHMARK in POSITIONS_AND_BENCHMARK references BENCHMARK in FACTORS.
    -- INSTRUMENT_ID in POSITIONS_AND_BENCHMARK references INSTRUMENT_ID in INSTRUMENTS.

    """ 

us_zip_code_table_descriptions = """
	The following is the long form description of table names:

	-- ZIP_TRACT: Zip Code to Census Tract Crosswalk from US Department of Housing and Urban Development, 2021 Q4
	-- ZIP_COUNTY: Zip Code to County Crosswalk from US Department of Housing and Urban Development, 2021 Q4
	-- ZIP_CBSA: Zip Code to Core-Based Statistical Area Crosswalk from US Department of Housing and Urban Development, 2021 Q4
	-- TRACT_ZIP: Census Tract to Zip Code Crosswalk from US Department of Housing and Urban Development, 2021 Q4
	-- COUNTY_ZIP: County to Zip Code Crosswalk from US Department of Housing and Urban Development, 2021 Q4
	-- CBSA_ZIP: Core-Based Statistical Area to Zip Code Crosswalk from US Department of Housing and Urban Development, 2021 Q4
	-- COUNTY: County List from US Census Bureau, 2010 Census
	-- CBSA: Core-Based Statistical Areas List from US Census Bureau, February 2013
"""
us_zip_code_foreign_key = """
	Foreign Key Relationships:
	-- CBSA_ZIP table:
		Foreign Key: CBSA
		Referencing Table: CBSA
		Referenced Column: CBSA_CODE
		
	-- COUNTY_ZIP table:
		Foreign Key: COUNTY
		Referencing Table: COUNTY
		Referenced Column: GEOID

	-- ZIP_CBSA table:
		Foreign Key: CBSA
		Referencing Table: CBSA
		Referenced Column: CBSA_CODE
		
	--	ZIP_COUNTY table:
		Foreign Key: COUNTY
		Referencing Table: COUNTY
		Referenced Column: GEOID
	
	--	ZIP_TRACT table:
		Foreign Key: TRACT
		Referencing Table: TRACT_ZIP
		Referenced Column: TRACT

	"""

covid_foreign_keys = """
Foreign Key Relationships:

	APPLE_MOBILITY
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	CDC_INPATIENT_BEDS_ALL
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	WHO_DAILY_REPORT
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	
	ECDC_GLOBAL_WEEKLY
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	
	JHU_VACCINES
	Foreign Key: FIPS
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: FIPS
	
	CDC_INPATIENT_BEDS_ICU_ALL
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	CDC_REPORTED_PATIENT_IMPACT
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	CDC_TESTING
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	GOOG_GLOBAL_MOBILITY_REPORT
	Foreign Key: ISO_3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO_3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	IHME_COVID_19
	Foreign Key: ISO_3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO_3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	JHU_COVID_19_TIMESERIES
	Foreign Key: FIPS
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: FIPS
	
	KFF_HCP_CAPACITY
	Foreign Key: COUNTRY_REGION
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: COUNTRY_REGION
	
	KFF_US_ICU_BEDS
	Foreign Key: FIPS
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: FIPS
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	NYC_HEALTH_TESTS
	Foreign Key: FIPS
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: FIPS
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	PCM_DPS_COVID19
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	SCS_BE_DETAILED_PROVINCE_CASE_COUNTS
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	CDC_INPATIENT_BEDS_COVID_19
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	CT_US_COVID_TESTS
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	HDX_ACAPS
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	
	JHU_COVID_19
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	Foreign Key: FIPS
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: FIPS
	
	KFF_US_REOPENING_TIMELINE_INCREMENT
	Foreign Key: COUNTRY_REGION
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: COUNTRY_REGION
	
	KFF_US_STATE_MITIGATIONS
	Foreign Key: COUNTRY_REGION
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: COUNTRY_REGION
	
	NYT_US_REOPEN_STATUS
	Foreign Key: STATE
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: STATE
	
	SCS_BE_DETAILED_HOSPITALISATIONS
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	SCS_BE_DETAILED_MORTALITY
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	WHO_TIMESERIES
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	KFF_US_POLICY_ACTIONS
	Foreign Key: COUNTRY_REGION
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: COUNTRY_REGION

"""

covid_cdc_foreign_keys = """
Foreign Key Relationships:
	
	CDC_INPATIENT_BEDS_ALL
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	ECDC_GLOBAL_WEEKLY
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	
	CDC_INPATIENT_BEDS_ICU_ALL
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	CDC_REPORTED_PATIENT_IMPACT
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	CDC_TESTING
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	
	CDC_INPATIENT_BEDS_COVID_19
	Foreign Key: ISO3166_1
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_1
	Foreign Key: ISO3166_2
	Referenced Table: DATABANK_DEMOGRAPHICS
	Referenced Column: ISO3166_2
	
	
	
"""

#table_lst = [table1,table2,table3]
#table_names = ["INSTRUMENTS", "FACTORS", "POSITIONS_AND_BENCHMARK"]

examples = """
    
    Examples:
    

    """
context = """ The following is the detail information of tables in a schema. The examples followed 
    by the 'Examples' tag contains questions asked in natural language and their 
    corresponding snowflake sql statement:
    """# + table1 + table2 + table3 + foreign_key #+ examples


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
    -- include dates in the sql query only if the question is related to date or time. Use the format yyyy-MM-dd HH:mm:ss for any date related query.
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

create_table1 = """CREATE TABLE INSTRUMENTS ( INSTRUMENT_ID VARCHAR(16777216), ASSET_NAME VARCHAR(255), ISSUER VARCHAR(255), INSTRUMENT_TYPE VARCHAR(255) );""" 

create_table2 = """CREATE TABLE FACTORS (AS_OF_DATE TIMESTAMP_NTZ(9),ACCT VARCHAR(16777216),BENCHMARK VARCHAR(16777216),FACTOR_PARENT VARCHAR(255),ISTOTALROW BOOLEAN,RISK_SOURCE VARCHAR(255),PORTFOLIO_RISK NUMBER(38,6),PCT_PORTFOLIO_RISK NUMBER(38,6),BENCHMARK_RISK NUMBER(38,6),PCT_BENCHMARK_RISK NUMBER(38,6),ACTIVE_RISK NUMBER(38,6),PCT_ACTIVE_RISK NUMBER(38,6),PORTFOLIO_RISK_CONTRIBUTION NUMBER(38,6),ACTIVE_PORTFOLIO_RISK_CONTRIBUTION NUMBER(38,6),PORTFOLIO_CORRELATION NUMBER(38,6),ACTIVE_PORTFOLIO_CORRELATION NUMBER(38,6),PORTFOLIO_VARIANCE NUMBER(38,6),BENCHMARK_VARIANCE NUMBER(38,6), ACTIVE_VARIANCE NUMBER(38,6));""" 

create_table3 = """CREATE TABLE POSITIONS_AND_BENCHMARK (AS_OF_DATE TIMESTAMP_NTZ(9), ACCT VARCHAR(16777216),BENCHMARK VARCHAR(16777216),INSTRUMENT_ID VARCHAR(16777216),ACTIVE_CORRELATION NUMBER(38,6),ACTIVE_COMMODITY_CONTRIBUTION NUMBER(38,6),ACTIVE_COUNTRY_CONTRIBUTION NUMBER(38,6),ACTIVE_CURRENCY_RISK_CONTRIBUTION NUMBER(38,6),ACTIVE_EMERGING_MARKET_CONTRIBUTION NUMBER(38,6),ACTIVE_HEDGE_FUND_CONTRIBUTION NUMBER(38,6),ACTIVE_INDUSTRY_CONTRIBUTION NUMBER(38,6),ACTIVE_MKT_TIMING_RISK_CONTRIBUTION NUMBER(38,6),ACTIVE_SPECIFIC_CONTRIBUTION NUMBER(38,6),ACTIVE_SPREAD_CONTRIBUTION NUMBER(38,6),ACTIVE_STYLE_CONTRIBUTION NUMBER(38,6),ACTIVE_TERM_STRUCTURE_CONTRIBUTION NUMBER(38,6),ACTIVE_WORLD_CONTRIBUTION NUMBER(38,6),ACTIVE_RISK_CONTRIBUTION NUMBER(38,6), PORT_RISK_CONTRIBUTION NUMBER(38,6),ACTIVE_RESI_EFF_WGT_PCT NUMBER(38,6),ACTIVE_TOTAL_RISK NUMBER(38,6),MC_TO_ACTIVE_TOTAL_RISK NUMBER(38,6),MC_TO_TOTAL_TRACKING_ERROR NUMBER(38,6),PCT_CR_TO_ACTIVE_LOCAL_MKT_RISK NUMBER(38,6),PCT_CR_TO_ACTIVE_TOTAL_RISK NUMBER(38,6),PCT_CR_TO_TOTAL_TRACKING_ERROR NUMBER(38,6), BETA_BMK NUMBER(38,6),CORRELATION NUMBER(38,6),MC_TO_TOTAL_RISK NUMBER(38,6),PCT_CR_TO_TOTAL_RISK NUMBER(38,6),TOTAL_RISK NUMBER(38,6),ACTIVE_WEIGHT_PCT NUMBER(38,6),BMK_WEIGHT_PCT NUMBER(38,6),EFF_ACTIVE_WGT_PCT NUMBER(38,6),EFF_BMK_WGT_PCT NUMBER(38,6),EFF_GLOBAL_WEIGHT_PCT NUMBER(38,6),EFF_WGT_PCT NUMBER(38,6),WEIGHT_PCT NUMBER(38,6),BMK_ASSET_NOT_HELD VARCHAR(255),GICS_IND VARCHAR(255),GICS_IND_GRP VARCHAR(255),GICS_SECTOR VARCHAR(255),GICS_SUBIND VARCHAR(255),CNTRY_OF_RISK VARCHAR(255),COMPANY_RATING VARCHAR(255));"""

predibase_cntxt = create_table1 + create_table2 + create_table3