Module 1:- Data Pipeline.
This module implements an end-to-end ETL pipeline that scrapes the data, cleans it,
computed from the required fixed-rate baseline (1 GBP = 105.50 INR), Load the Data a normalized SQLite schema with at least two table in database and Using SQL and Pandas wort queries.

** Setup and Execution process
* First we need install python software in our pc.
* Then Install project depended packeages : pip install -r requirements.txt
* Finally run the code file pipeline : pipline.py

Executed ths script we will get data.
* First scrape the data in this url ("[https://books.toscrape.com/]") it's free of cost.
* Then scrape Any 3 or More catregories in that site. At least more than 70 records.
* Next Create SQLite Database Load The data in this DB.
* Show the results of 5 or more SQL queries
* Finally validate the SQL join against an equivalent pandas using 'merge()' operation.
* Data cleaning : Currency conversion constrain, price Extraction via regex to strip currency symbols, Rating conversion and handling messy rows.
