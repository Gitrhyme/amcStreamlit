import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from st_aggrid import AgGrid

################ USER SPREADSHEET CONNECTION #####################################
def gspreadConnect():
    sa = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    sh = sa.open('amcClientSheet')
    wks = sh.worksheet('amcDf')
    return wks


def appendSpreadSheet(userInfo):
    wks = gspreadConnect()
    wks.append_row(userInfo, table_range="A1:F1")

################ FOOD SPREADSHEET CONNECTION #####################################
def gspreadConnect2():
    sa2 = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    sh2 = sa2.open('amcClientSheet')
    wks2 = sh2.worksheet('foodDf')
    return wks2

def appendSpreadSheet2(foodInfo):
    wks2 = gspreadConnect2()
    wks2.append_row(foodInfo, table_range="A1:G1")

################ NUMBER CONVERSIONS ##############################################
def heightConvert (ft, inches):
    h_ft = ft
    h_inch = inches

    h_inch += h_ft * 12
    h_cm = round(h_inch * 2.54, 2)

    return h_cm

def weightConvert (lbs):
    kilo_grams = round(lbs * 0.453592, 2)

    return kilo_grams

def activeRate (aLevel):
    activityRate = 0
    if aLevel == 'Sedentary':
        activityRate = 1.2
    elif aLevel == 'Lightly active':
        activityRate = 1.375
    elif aLevel == 'Moderately active':
        activityRate = 1.55
    elif aLevel == 'Very active':
        activityRate = 1.725
    elif aLevel == 'Extra active':
        activityRate = 1.9
    else:
        print('Input Invalid')
    return activityRate

def weightRate (wLevel):
    weightDiff = 0
    if wLevel == "Mild Weight Loss(half lb)":
        weightDiff = -250
    elif wLevel == "Weight Loss(1lb)":
        weightDiff = -500
    elif wLevel == "Extreme Weight Loss(2lbs)":
        weightDiff = -1000
    elif wLevel == "Mild Weight Gain(half lb)":
        weightDiff = 250
    elif wLevel == "Weight Gain(1lb)":
        weightDiff = 500
    elif wLevel == "Extreme Weight Gain(2lbs)":
        weightDiff = 1000
    elif wLevel == "Maintain":
        weightDiff = 0
    else:
        print('Input Invalid')
    return weightDiff

def macroCalc (gender, weight, height, age, activityRate, weightDiff):
    if gender == 'M' or gender == 'm':
        calories = 10 * weight + 6.25 * height - 5 * age + 5
    elif gender == 'F' or gender == 'f':
        calories = 10 * weight + 6.25 * height - 5 * age - 161
    return round((calories * activityRate) + weightDiff)

def macroSplit (splitChoice, macroCal):
    protein = 0
    carbs = 0
    fat = 0
    if splitChoice == 'Ectomorph':
        protein = (.25 * macroCal) / 4
        carbs = (.55 * macroCal) / 4
        fat = (.20 * macroCal) / 9
    if splitChoice == 'Mesomorph':
        protein = (.30 * macroCal) / 4
        carbs = (.40 * macroCal) / 4
        fat = (.30 * macroCal) / 9
    if splitChoice == 'Endomorph':
        protein = (.35 * macroCal) / 4
        carbs = (.25 * macroCal) / 4
        fat = (.40 * macroCal) / 9
    return round(protein), round(carbs), round(fat)

def loadData():
  wks = gspreadConnect()
  df = pd.DataFrame(wks.get_all_records())
  return df

##FOOD DF##
def loadData2(chosen_food_group, chosen_diet_type):
  wks2 = gspreadConnect2()
  df2 = pd.DataFrame(wks2.get_all_records())
  df3 = df2[df2['food_group'].isin(chosen_food_group)]
  if chosen_diet_type == "Normal":
    return df3
  else:
    df4 = df3[df3['diet_type'] == chosen_diet_type]
    return df4

###### MAIN PROGRAM START #############################################
st.title('AMC MACRO')
st.sidebar.header('Chart Filter')
df = loadData()
############### MACRO FORMULA #########################################
chosenClient = st.sidebar.selectbox('Choose Client', list(df['name']))
#gender = df['gender']
gender = df.loc[df['name'] == chosenClient, 'gender'].iloc[0]
#age = df['age']
age = df.loc[df['name'] == chosenClient, 'age'].iloc[0]
#ft = df['ft']
ft = df.loc[df['name'] == chosenClient, 'ft'].iloc[0]
#inches = df['in']
inches = df.loc[df['name'] == chosenClient, 'in'].iloc[0]
#lbs = df['lbs']
lbs = df.loc[df['name'] == chosenClient, 'lbs'].iloc[0]
#aLevel = int(input('Select Activity Level: '))
activityLvlList = ['Sedentary', 'Lightly active', 'Moderately active', 'Very active', 'Extra active']
aLevel = st.sidebar.selectbox('Activity Level', activityLvlList)
#wLevel = int(input('Select Weight Goal: '))
weightLvlList = ["Mild Weight Loss(half lb)", "Weight Loss(1lb)", "Extreme Weight Loss(2lbs)", "Mild Weight Gain(half lb)", "Weight Gain(1lb)", "Extreme Weight Gain(2lbs)", "Maintain"]
wLevel = st.sidebar.selectbox('Weight Goal', weightLvlList)
#splitChoice = int(input('Select Body Type: '))
bodyTypeList = ['Ectomorph', 'Mesomorph', 'Endomorph']
splitChoice = st.sidebar.selectbox('Body Type', bodyTypeList)
height = heightConvert (ft, inches)
weight = weightConvert (lbs)
activityRate = activeRate (aLevel)
weightDiff = weightRate (wLevel)
macroCal = macroCalc (gender, weight, height, age, activityRate, weightDiff)
############### MACRO FORMULA ############################################
st.text("")
st.header(f"{chosenClient}")
st.header(f"Current Weight: {lbs} lbs")
############ TOTAL CALORIES & GRAM BREAKDOWN #############################
#print(macroCal)
st.subheader(f'Daily Intake: {macroCal} calories')
#print(macroSplit (splitChoice, macroCal))
proteinMac, carbsMac, fatMac = macroSplit (splitChoice, macroCal)
st.subheader(f'Protein🍗: {proteinMac} grams')
st.subheader(f'Carbs🍞: {carbsMac} grams')
st.subheader(f'Fat🥑: {fatMac} grams')
############ TOTAL CALORIES & GRAM BREAKDOWN #############################

##FOOD DF SELECT BOXES##
chosen_food_group = st.sidebar.multiselect('Desired Food Groups', ["Fruits", "Veggies", "Grains", "Protein Rich", "Dairy"])
chosen_diet_type = st.sidebar.selectbox('Desired Diet Type', ["Normal", "Vegitarian", "Vegan"])
df2 = loadData2(chosen_food_group, chosen_diet_type)
##################### PIE CHART ##########################################
# Pie chart, where the slices will be ordered and plotted counter-clockwise:
labels = 'Protein', 'Carbs', 'Fat'
sizes = [proteinMac, carbsMac, fatMac]
explode = (0.1, 0.1, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

fig1, ax1 = plt.subplots(figsize=(10,5))
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

st.pyplot(fig1)
##################### PIE CHART ##########################################

##FOOD DF VISUAL##
df2 = loadData2(chosen_food_group, chosen_diet_type)
AgGrid(df2)

st.header("Add Client💪")
################ ADD USER FORM ###########################################
form = st.form(key="annotation")

with form:
    cols = st.columns((1, 1))
    userName = cols[0].text_input("Name:")
    userGender = cols[1].selectbox(
        "Gender:", ["M", "F"], index=0
    )
    cols = st.columns(4)
    userAge = cols[0].slider("Age:", 0, 100)
    userFt = cols[1].slider("Height(ft):", 0, 12)
    userInches = cols[2].slider("Height(in):", 0, 11) 
    userLbs = cols[3].number_input("Weight(lbs):", min_value=0, value=0)
    userInfo = [userName, userGender, userAge, userFt, userInches, userLbs]
    submitted = st.form_submit_button(label="Submit")


if submitted:
    appendSpreadSheet(userInfo)
    st.success("Thanks! Your info was recorded.")
    st.balloons()
################ ADD USER FORM ###########################################

st.header("Add Food🥣")
#################### ADD FOOD FORM #######################################
form2 = st.form(key="annotation2")

with form2:
    cols = st.columns(3)
    foodName = cols[0].text_input("Food Name:",)
    foodGroup = cols[1].selectbox("Food Group:", ["Fruits", "Veggies", "Grains", "Protein Rich", "Dairy"], index=0)
    dietType = cols[2].selectbox("Diet Type:", ["Normal", "Vegitarian", "Vegan"], index=0)
    cols = st.columns(4)
    foodProtein = cols[0].number_input("Protein:")
    foodCarbs = cols[1].number_input("Carbs:")
    foodFats = cols[2].number_input("Fat:") 
    foodServing = cols[3].text_input("Serving size:")
    foodInfo = [foodName, foodGroup, dietType, foodProtein, foodCarbs, foodFats, foodServing]
    submitted2 = st.form_submit_button(label="Submit")


if submitted2:
    appendSpreadSheet2(foodInfo)
    st.success("Food has been added!")
#################### ADD FOOD FORM #######################################
expander = st.expander("See all records")
with expander:
    st.write("View Google Sheet Here: https://docs.google.com/spreadsheets/d/1HHk3o5NeoFL3O6yyKO6a9gdypUrEZnLCJnCNHgmwmqk/edit?usp=sharing")
###### MAIN PROGRAM END #################################################
