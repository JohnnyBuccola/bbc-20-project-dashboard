# Final Project - Project Dashboard and Cost Calculator
## Introduction
Project Frog is a company that designs, delivers, and installs prefabricated, panelized buildings in a variety of industries.  One of their biggest customers is a quick-service fried chicken restaurant based in the Southeast.  In the last three years, Project Frog has been responsible for building over 80 locations around the country, and continues to deliver more each year to meet the company's growth needs.
## Problem Statement
Although Project Frog has successfully delivered a relatively large number of the same building typology, the cost of the wooden wall panels is difficult to predict with any amount of accuracy, and underbudgeting could lead to significant margin losses on a project.  The extreme differences in price per square foot are due to things like regional labor costs, current lumber market price, supplier, building typology, and potentially some lesser-known variables.
## Hypothesis
By identifying the most important features in each project that contribute to cost, a regression model can be trained to predict the cost from a supplier of a building's wooden wall panels with an error margin 20% or better (current methods have a 35% error margin).
## Approach
This full-stack application was set up to extract project data (living in Smartsheet) as well as Lumber market data (using python `yfinance`).  The data was loaded into two postgres tables, where it can be used for Tableau visualizations and machine learning analysis.  The features in the data set were ranked using Random Forest Classification, and multiple algorithms were trained using the top features.  An analysis was conducted to determine the best algorithm, which was then selected for use in the application.  Input fields in the web page allow a user to get a rapid estimate by inputting values via UI.

# Running the application
## Install and run Locally

`git clone` this repo anywhere on your hard drive.

Navigate to the cloned directory, and run `pip install -r requirements.txt` to install the necessary dependencies

