import json
import datetime
import pandas as pd
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash 
from dash.dependencies import Input, Output
from textwrap import dedent as d
import numpy as np
import operator

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

df = pd.read_csv("C:\\Users\\User\\Documents\\fyp\\clinical.csv")

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

def calPercent(df1,columnDF,nullExist=False, *replaceWith):
    dict_list = {}
    values = columnDF.unique()
    if nullExist:
        values = np.insert(values,0,replaceWith)
        values = np.delete(values,np.argwhere(pd.isna(values))[0][0])
    for v in values:
        if nullExist:
            dict_list[v] = round((len(columnDF) - columnDF.count())/len(columnDF)*100,2)
            nullExist = False
            continue
        dict_list[v] = round(len(df1[columnDF==v])/len(columnDF)*100,2)
    
    #sort values descendingly
    dict_list = dict(sorted(dict_list.items(),key=operator.itemgetter(1),reverse = True))

    return dict_list

# this has null
death_cause = df['cause_of_death']
death_cause_dict = calPercent(df,death_cause,True,"Alive")

#assuming no nan data
TNM = df['TNM_Stage']
TNM_dict = {}
TNM_Stage = TNM.unique()

for stage in TNM_Stage:
    status_dict = {}
    for life_status in death_cause_dict.keys():
        
        tmp = df[['TNM_Stage','cause_of_death']]
        if life_status == "Alive":
            NumRecord = len(tmp[(tmp['cause_of_death'].isnull()) & (tmp['TNM_Stage'] == stage)])/len(df[TNM == stage])*100
        else:
            NumRecord = len(tmp[(tmp['cause_of_death']==life_status) & (tmp['TNM_Stage']==stage)])/len(df[TNM == stage])*100
        status_dict[life_status] = round(NumRecord,2)
    TNM_dict[stage] = status_dict
TNM_dict = dict(sorted(TNM_dict.items(), key=lambda x:operator.getitem(x[1],'breast cancer related')))

# reorganize the previous dict into status for every stage
finalized_dict = {}
for status in death_cause_dict.keys():
    for stage in TNM_Stage:
        finalized_dict[status] = [v[status] for k,v in TNM_dict.items()] 

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    dcc.Graph(
        id='diagnosed-age-histogram',
        figure={
            'data': [
                 go.Histogram(                
                    x = df['Age_@_Dx'],
                    histnorm='probability',
                    nbinsx=22,
                    text = [11,47,285,864,1905,3306,4479,3995,3605,2891,1984,1282,832,376,163,39,11,1,2]
                ),
            ],
            'layout': go.Layout(
                title = "Patient's Diagnosed Age Distribution",
                xaxis = {'title': 'Diagnosed Age'},
                yaxis = {'title': 'Percentage of Patients'},
                autosize=False,
                width=600,
                height=400
            )
        }
    ),
    dcc.Graph(
        id='Proportion of Patients Alive Vs Dead',
        figure={
            'data': [
                go.Bar(
                x=list(death_cause_dict.keys()), 
                y=list(death_cause_dict.values()),
                text= list(death_cause_dict.values()),
                textposition='auto',
        )
            ],
            'layout': go.Layout(
                title = "Proportion of Patients Alive Vs Dead",
                xaxis = {'title': 'Cause of Death'},
                yaxis = {'title': 'Percentage of Patients'},
                hovermode='closest',
                autosize=False,
                width=600,
                height=400
            )
        }
    ), 
dcc.Graph(
        id='TNM Stage Alive Vs Dead',
        figure={
            'data': [
               go.Bar(
                    x= list(finalized_dict['Alive']),
                    y= list(TNM_dict.keys()),
                    name='Alive',
                    orientation='h',
                    marker=dict(
                    color='lightgreen',
                    line=dict(color='rgb(128, 173, 102)', width=3)
                    )
                ),
                go.Bar(
                    x= list(finalized_dict['breast cancer related']),
                    y= list(TNM_dict.keys()),
                    name='Dead- Breast cancer related',
                    orientation='h',
                    marker=dict(
                    color='rgba(246, 78, 139, 0.6)',
                    line=dict(color='rgba(246, 78, 139, 1.0)', width=3)
                    )
                ),
                go.Bar(
                    x= list(finalized_dict['n']),
                    y= list(TNM_dict.keys()),
                    name='Dead',
                    orientation='h',
                    marker=dict(
                    color='rgb(248, 97, 58)',
                    line=dict(color='red', width=3)
                    )
                ),
                go.Bar(
                    x= list(finalized_dict['unknown']),
                    y= list(TNM_dict.keys()),
                    name='unknown',
                    orientation='h',
                    marker=dict(
                    color='rgba(58, 71, 80, 0.6)',
                    line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
                    )
                )
            ],
            'layout': go.Layout(
                title = "TNM Stage Alive Vs Dead",
                xaxis = {'title': 'Percentage of Patients'},
                yaxis = {'title': 'Cancer Stages'},
                hovermode='closest',
                barmode='stack',
                autosize=False,
                width=1000,
                height=600
            )
        }
    )
    'style' = {'width': '100%', 'display': 'inline-block'}
])

if __name__ == '__main__':
    app.run_server(debug=True)