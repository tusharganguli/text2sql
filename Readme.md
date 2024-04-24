* Install Anaconda
* Create a virtual environment
* Activate/Open the virtual environment.
* Run the following commands to install the necessary packages: 
	pip install flask
	pip install openai
	pip install snowflake
	pip install chat2plot
	pip install llama-index
	pip install llama-index-readers-json
	pip install Flask-Caching
	pip install watchdog
	pip install -U langchain-community
	
	For installing nltk: https://www.nltk.org/install.html
	NLTK installation for MAC Users:
		pip install --user -U nltk
		Open the python interpeter by typing "python"
		type the following commands in the python terminal:
			import nltk
			nltk.download() - This command wil open a UI, select and download everything

* Set the Open API key from the terminal:
	a. Run <sudo nano ~/.zshrc> 
	b. Copy the line: export <OPENAI_API_KEY="your key"> (please keep the key within quotes)
	c. ctrl+O to save the file and ctrl+X to exit
* Close this terminal and reopen another terminal.
* Activate the virtual environment created in step 2.
* From the terminal go to the folder FT and run python main.py

# Additional instructions for predibase:
* Install the following packages:
	pip install -U predibase
	pip install datasets

* Set the predibase key from the terminal:
	a. Run <sudo nano ~/.zshrc> 
	b. Copy the line: export PREDIBASE_TOKEN = <your key>
	c. ctrl+O to save the file and ctrl+X to exit
