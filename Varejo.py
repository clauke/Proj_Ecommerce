# Importes

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly
import plotly.graph_objs as go
import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# app = Dash(__name__)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

# Carrega os dados
dados = pd.read_csv("superstore.csv", header = 0, encoding = 'UTF-8')

# Altera os dados
dados = dados.drop(columns = ['Row ID', 'Country', 'Postal Code'])
dados.rename(columns={'Order ID':'Order_ID','Order Date':'Order_Date','Ship Mode':'Ship_Mode','Customer ID':'Customer_ID',
                      'Ship Date':'Ship_Date', 'Product ID': 'Product_ID', 'Product Name':'Product_Name',
                      'Customer Name':'Customer_Name'}, inplace=True)

dados.Order_Date = pd.to_datetime(dados.Order_Date)
dados.Ship_Date = pd.to_datetime(dados.Ship_Date)
dados['Order_Year'] = dados['Order_Date'].dt.year
lucro_total = round(dados['Profit'].sum(), 2)


####### Gráfico de Linhas ########
# Prepara os dados
dados_lucro = dados.groupby(['Order_Year']).agg({'Profit': sum}).reset_index()

# Cria o gráfico
plot_dados = [go.Scatter(x = dados_lucro['Order_Year'],
                         y = dados_lucro['Profit'])]

plot_visual = go.Layout(xaxis = {'type': 'category'},
                    title = 'Lucro Anual')          

graf_linhas = go.Figure(data = plot_dados,
                    layout = plot_visual)

graf_linhas.update_layout(autosize=True,
                    margin=go.Margin(l=0, r=0, b=0))

graf_linhas.update_traces(marker_color='darkgreen')



###### Gráfico de Colunas ########
# Prepara os dados
dados_vendas = dados.groupby(['Order_Year']).agg({'Sales': sum}).reset_index()

# Gera o gráfico
graf_colunas = go.Figure()

graf_colunas.add_trace(go.Bar(x = dados_lucro['Order_Year'], 
                     y = dados_lucro['Profit'],
                     name = 'Lucro',
                     marker_color = 'blue'))

graf_colunas.add_trace(go.Bar(x = dados_vendas['Order_Year'],
                     y = dados_vendas['Sales'],
                     name = 'Vendas',
                     marker_color = 'lightblue'))

graf_colunas.update_layout(title_text = 'Vendas e Lucro por Ano',
                  xaxis = {'type': 'category'},
                  xaxis_title = "Ano",
                  yaxis_title = "Vendas/Lucro",
                  barmode = 'stack',
                  autosize=True,
                  margin=dict(l=10, r=10, b=10))

###### Gráfico de Pizza ########
# Prepara os dados
lucro_categ = dados[['Category','Profit']].groupby('Category').sum().reset_index()

# Gera o gráfico
cores = ['lightgray', 'lightblue', 'pink']
graf_pizza = go.Figure([go.Pie(labels = lucro_categ['Category'], values = lucro_categ['Profit'])])

graf_pizza.update_traces(hoverinfo = 'label+percent', 
                    textfont_size = 10,
                    insidetextorientation = 'radial',
                    marker = dict(colors = cores, line = dict(color = '#FFFFFF', width = 1)))
                    
graf_pizza.update_layout(title = "Lucro por Categoria",
                    title_x = 0.5,
                    autosize=True,
                    margin=dict(l=10, r=10, b=10),
                    showlegend=False)

###### Mapa ########
# Prepara os dados
ped_estado = dados['State'].value_counts().to_frame().reset_index().rename(columns = {'index':'State', 'State': 'Count'})

# Gera o gráfico
graf_mapa = go.Figure(go.Choropleth(locations = ped_estado['State'],
                            z = ped_estado['Count'].astype(float),
                            locationmode = 'USA-states',
                            colorscale = 'Reds',
                            autocolorscale = False,
                            text = ped_estado['State'], 
                            marker_line_color = 'white', 
                            showscale = True))

graf_mapa.update_layout(title_text = 'Pedidos por Estado (2014-2017)',
                    geo = dict(scope = 'usa',
                    projection = go.layout.geo.Projection(type = 'albers usa'),
                    showlakes = True, 
                    lakecolor = '#87cefa',
                    bgcolor="black"))


###### Gráfico de Barras ########
# Prepara os dados
ped_ano = dados['Order_Year'].value_counts().reset_index().rename(columns = {'index':'Order_Year', 'Order_Year': 'Count'})

# Gera o gráfico
graf_barras = go.Figure(go.Bar(y = ped_ano['Order_Year'], x = ped_ano['Count'], orientation = "h")) 

graf_barras.update_layout(title_text = 'Número de Pedidos por Ano',
                    xaxis_title = "Nº de Pedidos",
                    yaxis = {'type': 'category'},
                    yaxis_title = "Ano")

graf_barras.update_traces(marker_color="indianred")

graf_barras.update_yaxes(categoryorder = 'category ascending')


######## Layout ########

app.layout = dbc.Container(
    dbc.Row([
        html.H2(children='Dashboard - BI para Varejo'),
        dbc.Col([
            html.Div([
                dcc.Graph(figure=graf_linhas, style={"height": "40vh"}),
                dcc.Graph(figure=graf_mapa, style={"height": "40vh", "margin-top": "10px"})
            ])    
        ],md=5),
    
        dbc.Col([
            html.Div([
                dcc.Graph(figure=graf_colunas, style={"height": "40vh"}),
                dcc.Graph(figure=graf_barras, style={"height": "40vh", "margin-top": "10px"})
            ])
        ], md=5),
    
        dbc.Col([
            html.Div([
                dcc.Graph(figure=graf_pizza, style={"height": "40vh"}),
                dbc.Card([
                    dbc.CardBody([
                        html.Span("Lucro Total", style={"color": "white", "margin-left": "40px"}),
                        html.H3(lucro_total, style={"color": "white", "margin-left": "20px"})
                        ])
                    ], outline=True, style={"margin-top": "10px", "height":"15vh"})
            ])
        ], md=2),    
    ]),
fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)