

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

foreign_key = """
    
    Foreign Key Relationships:
    -- ACCT in POSITIONS_AND_BENCHMARK references ACCT in FACTORS.
    -- BENCHMARK in POSITIONS_AND_BENCHMARK references BENCHMARK in FACTORS.
    -- INSTRUMENT_ID in POSITIONS_AND_BENCHMARK references INSTRUMENT_ID in INSTRUMENTS.

    """ 

table_lst = [table1,table2,table3]
table_names = ["INSTRUMENTS", "FACTORS", "POSITIONS_AND_BENCHMARK"]

examples = """
    
    Examples:
    

    """
context = """ The following is the detail information of tables in a schema. The examples followed 
    by the 'Examples' tag contains questions asked in natural language and their 
    corresponding snowflake sql statement:
    """ + table1 + table2 + table3 + foreign_key #+ examples


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
    -- when querying the tables match the column which is the closest match in the query.
    -- If generating data across table needs a union operation then perform a union of tables only if the number of columns retrieved from all the tables is equal or else use foreign key relationship to get data from all tables.
    -- If using a where clause to compare data, use ILIKE to make the comparison.
    -- When constructing SQL queries with a WHERE clause, please ensure that you use a case-insensitive similarity comparison using ILIKE, for example: WHERE column_name ILIKE '%word%'
    """

create_table1 = """CREATE TABLE INSTRUMENTS ( INSTRUMENT_ID VARCHAR(16777216), ASSET_NAME VARCHAR(255), ISSUER VARCHAR(255), INSTRUMENT_TYPE VARCHAR(255) );""" 

create_table2 = """CREATE TABLE FACTORS (AS_OF_DATE TIMESTAMP_NTZ(9),ACCT VARCHAR(16777216),BENCHMARK VARCHAR(16777216),FACTOR_PARENT VARCHAR(255),ISTOTALROW BOOLEAN,RISK_SOURCE VARCHAR(255),PORTFOLIO_RISK NUMBER(38,6),PCT_PORTFOLIO_RISK NUMBER(38,6),BENCHMARK_RISK NUMBER(38,6),PCT_BENCHMARK_RISK NUMBER(38,6),ACTIVE_RISK NUMBER(38,6),PCT_ACTIVE_RISK NUMBER(38,6),PORTFOLIO_RISK_CONTRIBUTION NUMBER(38,6),ACTIVE_PORTFOLIO_RISK_CONTRIBUTION NUMBER(38,6),PORTFOLIO_CORRELATION NUMBER(38,6),ACTIVE_PORTFOLIO_CORRELATION NUMBER(38,6),PORTFOLIO_VARIANCE NUMBER(38,6),BENCHMARK_VARIANCE NUMBER(38,6), ACTIVE_VARIANCE NUMBER(38,6));""" 

create_table3 = """CREATE TABLE POSITIONS_AND_BENCHMARK (AS_OF_DATE TIMESTAMP_NTZ(9), ACCT VARCHAR(16777216),BENCHMARK VARCHAR(16777216),INSTRUMENT_ID VARCHAR(16777216),ACTIVE_CORRELATION NUMBER(38,6),ACTIVE_COMMODITY_CONTRIBUTION NUMBER(38,6),ACTIVE_COUNTRY_CONTRIBUTION NUMBER(38,6),ACTIVE_CURRENCY_RISK_CONTRIBUTION NUMBER(38,6),ACTIVE_EMERGING_MARKET_CONTRIBUTION NUMBER(38,6),ACTIVE_HEDGE_FUND_CONTRIBUTION NUMBER(38,6),ACTIVE_INDUSTRY_CONTRIBUTION NUMBER(38,6),ACTIVE_MKT_TIMING_RISK_CONTRIBUTION NUMBER(38,6),ACTIVE_SPECIFIC_CONTRIBUTION NUMBER(38,6),ACTIVE_SPREAD_CONTRIBUTION NUMBER(38,6),ACTIVE_STYLE_CONTRIBUTION NUMBER(38,6),ACTIVE_TERM_STRUCTURE_CONTRIBUTION NUMBER(38,6),ACTIVE_WORLD_CONTRIBUTION NUMBER(38,6),ACTIVE_RISK_CONTRIBUTION NUMBER(38,6), PORT_RISK_CONTRIBUTION NUMBER(38,6),ACTIVE_RESI_EFF_WGT_PCT NUMBER(38,6),ACTIVE_TOTAL_RISK NUMBER(38,6),MC_TO_ACTIVE_TOTAL_RISK NUMBER(38,6),MC_TO_TOTAL_TRACKING_ERROR NUMBER(38,6),PCT_CR_TO_ACTIVE_LOCAL_MKT_RISK NUMBER(38,6),PCT_CR_TO_ACTIVE_TOTAL_RISK NUMBER(38,6),PCT_CR_TO_TOTAL_TRACKING_ERROR NUMBER(38,6), BETA_BMK NUMBER(38,6),CORRELATION NUMBER(38,6),MC_TO_TOTAL_RISK NUMBER(38,6),PCT_CR_TO_TOTAL_RISK NUMBER(38,6),TOTAL_RISK NUMBER(38,6),ACTIVE_WEIGHT_PCT NUMBER(38,6),BMK_WEIGHT_PCT NUMBER(38,6),EFF_ACTIVE_WGT_PCT NUMBER(38,6),EFF_BMK_WGT_PCT NUMBER(38,6),EFF_GLOBAL_WEIGHT_PCT NUMBER(38,6),EFF_WGT_PCT NUMBER(38,6),WEIGHT_PCT NUMBER(38,6),BMK_ASSET_NOT_HELD VARCHAR(255),GICS_IND VARCHAR(255),GICS_IND_GRP VARCHAR(255),GICS_SECTOR VARCHAR(255),GICS_SUBIND VARCHAR(255),CNTRY_OF_RISK VARCHAR(255),COMPANY_RATING VARCHAR(255));"""

predibase_cntxt = create_table1 + create_table2 + create_table3