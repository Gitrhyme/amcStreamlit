import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread

################ SPREADSHEET CONNECTION #####################################
def gspreadConnect():
    sa = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    sh = sa.open('amcClientSheet')
    wks = sh.worksheet('amcDf')
    return wks


def appendSpreadSheet(userInfo):
    wks = gspreadConnect()
    wks.append_row(userInfo, table_range="A1:F1")
################ SPREADSHEET CONNECTION ###############################

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

###### MAIN PROGRAM START ######
st.title('AMC MACRO')

st.header("Add Client💪")
################ SPREADSHEET FORM #####################################
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
################ SPREADSHEET FORM ################################

st.sidebar.header('Chart Filter')
df = loadData()

############### MACRO FORMULA #########################
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
############### MACRO FORMULA #########################


############ TOTAL CALORIES & GRAM BREAKDOWN ##########
#print(macroCal)
st.text('')
st.header(f'{chosenClient} Chart Details:')
st.subheader(f'Daily Intake: {macroCal} calories')
#print(macroSplit (splitChoice, macroCal))
proteinMac, carbsMac, fatMac = macroSplit (splitChoice, macroCal)
st.subheader(f'Protein🍗: {proteinMac} grams')
st.subheader(f'Carbs🍞: {carbsMac} grams')
st.subheader(f'Fat🥑: {fatMac} grams')
############ TOTAL CALORIES & GRAM BREAKDOWN ##########


##################### PIE CHART ##########################################
# Pie chart, where the slices will be ordered and plotted counter-clockwise:
labels = 'Protein', 'Carbs', 'Fat'
sizes = [proteinMac, carbsMac, fatMac]
explode = (0.1, 0.1, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

st.pyplot(fig1)
##################### PIE CHART ##########################################

expander = st.expander("See all records")
with expander:
    st.dataframe(df)

###### MAIN PROGRAM END ######
