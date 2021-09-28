# BlackBox
Web Service that secures the transactions made by of software engineering contracting work. When someone has a function they would like built by a contractor they post a ticket on the site with a description on the requested function and a test file. The test file will be used to verify that the a function submitted by a customer is correct.

## How to Run
To run the flask application run:
```
export FLASK_APP=flaskw && export FLASK_ENV=development
flask run
```
Note: you only need to run the export command once per session

To run in docker run:
```
docker build -t flask-container .
docker run -p 5000:5000 flask-container
```

To initialize or reset the database run
```
export FLASK_APP=flaskw && export FLASK_ENV=development
flask init-db
```
Note: you only need to run the export command once per session

## Endpoints
### /table
Shows a table of the active contracts

### /table/<int:id>
Shows the information on the contract of the id variable
User is able to upload a file with the function and attempt to complete the contract
Table also shows all of the attempts so far on the contract

### /create
Shows a form for creating a contract
Has a file upload section for uploading the test file

