import os
import pandas as pd
from pandas.core.frame import DataFrame
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression

# ML Parameters (tweak to improve model as necessary)
KNNS = 10
RFS={
    'scale_data': True,
    'n_estimators': 400,
    'min_samples_split': 10,
    'min_samples_leaf': 4,
    'max_features': 'auto',
    'max_depth': 70,
    'bootstrap': True
}

ENC = OneHotEncoder(sparse=False, handle_unknown="ignore")

def get_data():
    engine = create_engine(os.environ['DATABASE_URL'])
    projects_df = pd.read_sql_query('select * from projects',con=engine)
    lumber_df = pd.read_sql_query('select * from lumber_prices', con=engine)
    return projects_df,lumber_df



def prep_data():
    projects_df, lumber_df = get_data()
    # Outer-join dataframes on the date column, and drop any rows with missing data in any cell
    merged = projects_df.merge(lumber_df,left_on="sales_order_date", right_on="date",how='outer').dropna(axis=0,how='any')

    # List of features for analysis
    features = ['wall_panels_cost_per_elev_sqft','sales_order_date','prototype_prefix','region','panel_vendor','sqft','sqft_wall_panels_ext', 'sqft_wall_panels_int','close']

    # Create new df containing only columns relevant to analyitics, sort by date
    analytical_df = merged[features].sort_values(by=['sales_order_date'],ascending=True)

    # Only consider P12 and P13
    analytical_df = analytical_df[analytical_df['prototype_prefix'].str.startswith('P12') | analytical_df['prototype_prefix'].str.startswith('P13')]

    # Sales order date only needed for merge - drop it in favor of
    analytical_df = analytical_df.drop(columns=['sales_order_date']).reset_index().drop(axis=1,columns='index')

    # Create encoded dataframes, any NaN values will be encoded as None, value 0 (via handle_unknown)
    prototype_enc_df = encode_df(ENC,analytical_df,'prototype_prefix')
    vendor_enc_df = encode_df(ENC,analytical_df,'panel_vendor')
    region_enc_df = encode_df(ENC,analytical_df,'region')

    # merge back into original 
    analytical_df = analytical_df.merge(vendor_enc_df,left_index=True,right_index=True,how="outer").drop(columns="panel_vendor",axis=1)
    analytical_df = analytical_df.merge(region_enc_df,left_index=True,right_index=True).drop(columns="region",axis=1)
    analytical_df = analytical_df.merge(prototype_enc_df,left_index=True,right_index=True).drop(columns="prototype_prefix",axis=1)

    # Features
    X = analytical_df.drop(columns=["wall_panels_cost_per_elev_sqft"],axis=1)

    # Target
    y = analytical_df["wall_panels_cost_per_elev_sqft"]

    return X, y

def encode_df(enc, source_df, feature_to_encode):
    # if type(source_df) is DataFrame:
    encoded = pd.DataFrame(enc.fit_transform(source_df[feature_to_encode].values.reshape(-1,1))).sort_index()
    encoded.columns = enc.get_feature_names_out([feature_to_encode])
    # else:
    #     print(source_df['prototype_prefix']) 
    #     encoded = pd.DataFrame(enc.fit_transform(source_df[feature_to_encode])).sort_index()
    #     encoded.columns = enc.get_feature_names_out([feature_to_encode])
    return encoded

def evaluate_models(X,y,scale_features=True):
    scores = {}

    # Split into separate data sets for evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=43,test_size=0.20)

    # Use MinMaxScaler since are is no negative fields

    # Fit the MinMaxScaler on all columns 
    # NOTE: I don't know whether the encoded columns should be scaled as well - in this case, we are scaling everything.
    if scale_features:
        scaler = MinMaxScaler()
        X_scaler = scaler.fit(X_train)

        # Scale the data
        X_train = X_scaler.transform(X_train)
        X_test = X_scaler.transform(X_test)

    # Create random forest model
    rf_model = RandomForestRegressor(n_estimators=RFS['n_estimators'], min_samples_split=RFS['min_samples_split'], min_samples_leaf=RFS['min_samples_leaf'],max_features=RFS['max_features'],max_depth=RFS['max_depth'],bootstrap=RFS['bootstrap'], random_state=69)  
    rf_model = rf_model.fit(X_train,y_train)
    scores['RandomForestRegressor'] = rf_model.score(X_test,y_test)

    # Create KNN model
    knn_model = KNeighborsRegressor(n_neighbors=KNNS,weights='uniform')
    knn_model = knn_model.fit(X_train,y_train)
    scores['KNeighborsRegressor'] = knn_model.score(X_test,y_test)

    # Create Linear Model
    linear_model = LinearRegression()
    linear_model = linear_model.fit(X_train,y_train)
    scores['LinearRegression'] = linear_model.score(X_test,y_test)

    return scores

def get_feature_importances(X,y):
    rf_model = RandomForestRegressor(n_estimators=400, random_state=69) 
    rf_model = rf_model.fit(X,y)
    importances = sorted(zip(rf_model.feature_importances_,X.columns),reverse=True)
    return importances

def train(X,y,scale_features=True,model='RandomForestRegressor'):
    trained_model = None
    if scale_features:
        scaler = MinMaxScaler()
        X_scaler = scaler.fit(X)
        X = X_scaler.transform(X)
    if model == 'RandomForestRegressor':
        trained_model = RandomForestRegressor(n_estimators=RFS['n_estimators'], min_samples_split=RFS['min_samples_split'], min_samples_leaf=RFS['min_samples_leaf'],max_features=RFS['max_features'],max_depth=RFS['max_depth'],bootstrap=RFS['bootstrap'], random_state=69)  
        trained_model = trained_model.fit(X,y)
    if model == 'KNeighborsRegressor':
        trained_model = KNeighborsRegressor(n_neighbors=KNNS,weights='uniform')
        trained_model = trained_model.fit(X,y)
    if model == 'LinearRegression':
        linear_model = LinearRegression()
        linear_model = linear_model.fit(X,y)
    return trained_model

 # Encode the prediction values using the same encoder
def prep_prediction(prediction_df):
    prototype_enc_df = encode_df(ENC,prediction_df,'prototype_prefix')
    vendor_enc_df = encode_df(ENC,prediction_df,'panel_vendor')
    region_enc_df = encode_df(ENC,prediction_df,'region')

    # merge back into original 
    prediction_df = prediction_df.merge(vendor_enc_df,left_index=True,right_index=True,how="outer").drop(columns="panel_vendor",axis=1)
    prediction_df = prediction_df.merge(region_enc_df,left_index=True,right_index=True).drop(columns="region",axis=1)
    prediction_df = prediction_df.merge(prototype_enc_df,left_index=True,right_index=True).drop(columns="prototype_prefix",axis=1)
    
    return prediction_df

def predict(trained_model,X):
    return trained_model.predict([X])