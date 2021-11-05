# Project Dashboard and Cost Estimation
## Launching the App

## Activate virtual environment
This repo comes with its own virtual environment, through the `virtualenv` python package. When running the app for the first time, the dependencies must be installed. 

1. From the command line, navigate to the project root
2. From a windows system, run `.\scripts\activate.bat`
3. From Unix or MacOS, run `source ./bin/activate`

## Database Changes
To push a change to the database, do the following:

1. From the command line, navigate to the project root
2. If running from a windows system, run `env.bat` to set the environment variables
3. Ensure the postgres db is running with the credentials specified in `env.bat`
4. Run `flask db migrate` to create a new migration job
5. Run `flask db upgrade` to complete the migration

