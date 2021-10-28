from api_config import GOOGLE_API_KEY,SMARTSHEET_API_KEY
from googlemaps import Client as GoogleMaps
import smartsheet
import logging
import pandas as pd
import traceback
from sqlalchemy import select
from .models import Project

## Wall Panel Cost; Sales Order Date; Panels Onsite Date
SUPPLY_CHAIN_SHEET_ID = '8581360311920516'

# ?
PROJECT_SHEET_ID = '4456738465310596'
CFA_TRACKER_SHEET_ID = '5063848718821252'

# Project Address, City, State
CFA_MASTER = '5769032839260036'

# Clean sample
SAMPLE_SHEET_ID = '7416230777776004'

# Google Maps Client (for get_coords)
gmaps = GoogleMaps(GOOGLE_API_KEY)

# Log all calls
logging.basicConfig(filename='rwsheet.log', level=logging.INFO)


def get_smartsheet_data(SHEET_ID):
    column_map = {}

    print("Starting ...")

    # Initialize client. Uses the API token in the environment variable "SMARTSHEET_ACCESS_TOKEN"
    smart = smartsheet.Smartsheet(SMARTSHEET_API_KEY)
    # Make sure we don't miss any error
    smart.errors_as_exceptions(True)


    # Load entire sheet
    sheet = smart.Sheets.get_sheet(SHEET_ID)

    print("Loaded " + str(len(sheet.rows)) + " rows from sheet: " + sheet.name)

    # Build column map for later reference - translates column names to column id
    for column in sheet.columns:
        column_map[column.title] = column.id
    
    print("Done")
    return column_map, sheet

def clean_cfa_tracker_df(cfa_tracker_df_raw):
    # select only address columns
    cols = ["Location_Number","Address", "City", "State"]
    cfa_tracker_df = cfa_tracker_df_raw[cols]
    # remove any non-numeric entries
    cfa_tracker_df["Location_Number"] = pd.to_numeric(cfa_tracker_df["Location_Number"],downcast='integer',errors='coerce').fillna(0)
    # Cast location number to integer type
    cfa_tracker_df = cfa_tracker_df.astype({'Location_Number':'int32'})
    # Remove any rows with missing data in any of the above columns (it's OK if address is missing for some reason, will be approximated)
    cfa_tracker_df[['Location_Number','City','State']].dropna(axis=0,how="any",inplace=True)
    return cfa_tracker_df

## clean dataframe from SC_CFA Master Budget v Buyout smartsheet
def clean_sc_df(sc_df_raw):
    # get columns
    cols = ['Location_Number','Prototype', 'Region','Awarded_Wall_Panel_Supplier','SO_Executed_Date','BUYOUT_Total','Panels_On_Site','sqft','Component_Model_Status','Wall_Panels','n_of_Ext_Wall_panel','n_of_Int_Wall_panel','sqft_of_Int_Wall_panel','sqft_of_Ext_Wall_panel']
    # filter out any project that does not have a wall panels cost
    sc_df=sc_df_raw[sc_df_raw['Wall_Panels'].notnull()][cols]
    # drop extra NA values (usually at the end)
    sc_df.dropna(how="all",inplace=True, axis=1)
    # force location number to type (removes leading zeroes)
    sc_df = sc_df.astype({'Location_Number':'int32'})
    # fill empty numerical cells with zeroes
    sc_df = sc_df.fillna({'n_of_Int_Wall_panel':0,'n_of_Ext_Wall_panel':0,'sqft_of_Int_Wall_panel':0, 'sqft_of_Ext_Wall_panel':0})
    return sc_df

def sheet_to_dataframe(sheet):
    # Clean column headers for itertuples() in sync_projects()
    def remove_invalid_char(str):
        return str.replace(" ", "_").replace("-","_").replace(".","").replace("#","n")
    headers = [remove_invalid_char(col.title) for col in sheet.columns]
    rows = []
    for row in sheet.rows:
        cells = []
        for cell in row.cells:
            cells.append(cell.value)
        rows.append(cells)
    # Create dataframe, use provided project ID Column as index 
    df = pd.DataFrame(rows,columns=headers)
    return df

def get_coords(city, state, address):
    location = "{0} {1} {2}".format(address, city, state)
    try:
        geodata = gmaps.geocode(location)
    except Exception as ex:
        print(ex)
        return None,None
    lat = geodata[0]['geometry']['location']['lat']
    lng = geodata[0]['geometry']['location']['lng']
    return lat, lng

def project_exists(db,project_tuple):
    statement = select(Project).where(Project.id == project_tuple.Location_Number)
    if len(db.session.execute(statement).all()) > 0:
        return True
    return False

def add_project(db,project_tuple):
    if not project_tuple.Location_Number:
        return
    lat, long = get_coords(project_tuple.City,project_tuple.State, project_tuple.Address)
    print(project_tuple.City,project_tuple.State, project_tuple.Address)
    project = Project (
        id = int(project_tuple.Location_Number),
        lat= lat,
        long= long,
        city=project_tuple.City,
        state=project_tuple.State,
        address=project_tuple.Address,
        region=project_tuple.Region,
        sqft=int(project_tuple.sqft),
        prototype_prefix=project_tuple.Prototype.split(' ')[0],
        prototype_suffix= project_tuple.Prototype.split(' ')[1] if len(project_tuple.Prototype.split(' ')) > 1 else '',
        wall_panels_cost=project_tuple.Wall_Panels,
        buyout_total=project_tuple.BUYOUT_Total,
        panels_onsite_date=project_tuple.Panels_On_Site,
        sales_order_date=project_tuple.SO_Executed_Date,
        panel_vendor=project_tuple.Awarded_Wall_Panel_Supplier,
        n_wall_panels_ext=project_tuple.n_of_Ext_Wall_panel,
        n_wall_panels_int=project_tuple.n_of_Int_Wall_panel,
        sqft_wall_panels_ext=project_tuple.sqft_of_Ext_Wall_panel,
        sqft_wall_panels_int=project_tuple.sqft_of_Int_Wall_panel,
        project_status=project_tuple.Component_Model_Status
    )
    try:
        db.session.add(project)
        db.session.commit()
        print(f"{project} added")
    except Exception as ex:
        print(f"error adding {project}: {ex} - not added")

##TODO: Implement Project Update
def update_project(db, project_tuple):
    print(f"(not) updating project {int(project_tuple.Location_Number)}")
    pass

def sync_projects(db):
    added = 0
    updated = 0
    ##TODO: join all dataframes
    sc_df_raw = sheet_to_dataframe(get_smartsheet_data(SUPPLY_CHAIN_SHEET_ID)[1])
    cfa_tracker_df_raw = sheet_to_dataframe(get_smartsheet_data(CFA_TRACKER_SHEET_ID)[1])
    sc_df = clean_sc_df(sc_df_raw)
    cfa_tracker_df = clean_cfa_tracker_df(cfa_tracker_df_raw)
    combined_df = sc_df.merge(cfa_tracker_df,how='left',left_on='Location_Number',right_on='Location_Number')
    # Iterate through dataframe and add to db
    for row in combined_df.itertuples():
        try:
            if project_exists(db,row):
                update_project(db,row)
            else:
                add_project(db,row) 
                added +=1
        except Exception:
            traceback.print_exc()
    print(f"{added} projects added successfully")
    return added, updated

def delete_all_projects(db):
    deleted = db.session.query(Project).delete()
    db.session.commit()
    return deleted