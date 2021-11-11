import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import dcc
from dash import html
import pandas as pd
from dash.exceptions import PreventUpdate
import json
import base64
import io

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

PLOTLY_LOGO = "https://zupimages.net/up/21/44/ee8m.jpg"

app.layout = html.Div([
    dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                            dbc.Col(dbc.NavbarBrand("TraderPlus Config Editor", className="ms-2")),
                            dbc.Col(dbc.NavItem(dbc.NavLink("TraderPlus documentation",
                                                            href="https://myreader.toile-libre.org/uploads/My_6182ab33ac107.pdf",
                                                            id='documentation-link', external_link=True)),
                                    ),
                            dbc.Col(
                                dbc.Button("Donate", color="warning", id='donate-link', external_link=True,
                                           href='https://ko-fi.com/thedmitri'),
                            )
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="https://steamcommunity.com/sharedfiles/filedetails/?id=2458896948",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ]
        ),
        color="dark",
        dark=True,
    ),
    dcc.Store(id='session', storage_type='session'),
    dbc.Row([
        dbc.Col(
            dbc.Input(id="code_input", type="any", debounce=True, value="",
                      placeholder="paste your config here", size="md"),
            width="auto"
        ),
        dbc.Col(
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=False
            ),
        ),
        html.Div(id='output-data-upload'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='category_dropdown',
                options=[],
                placeholder="Select a category",
                persistence=True,
                persistence_type='session',
            ),
            width={"size": 6, "offset": 3},
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Button("Remove category", color="secondary", id='remove_category', n_clicks=0),
            width={"size": "auto", "offset": 4}
        ),

        dbc.Col(
            dbc.Button("Add category", color="secondary", id='add_category', n_clicks=0),
            width="auto"
        ),
        dbc.Col(
            dbc.Input(id="category_name_input", type="text", debounce=True, value="",
                      placeholder="Change category name", size="md"),
            width="auto"
        ),
        dbc.Col(
            dbc.Button("Save", color="success", id='save-button', n_clicks=0),
            width="auto"
        ),
        dcc.Download(id="download_json"),
    ], align="center", ),
    dbc.Row([
        dbc.Col(
            dash_table.DataTable(
                id='products_table',
                columns=[{"name": "classname", "id": "classname", "type": 'text'},
                         {"name": "coefficient", "id": "coefficient", "type": 'numeric'},
                         {"name": "max stock", "id": "max stock", "type": 'numeric'},
                         {"name": "trade quantity", "id": "trade quantity", "type": 'numeric'},
                         {"name": "buy price", "id": "buy price", "type": 'numeric'},
                         {"name": "sell price", "id": "sell price", "type": 'numeric'},
                         {"name": "destock coefficient", "id": "destock coefficient", "type": 'numeric'},
                         {"name": "comments", "id": "comments", "type": 'any'},
                         ],
                style_cell={'textAlign': 'left'},
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'Region'},
                        'textAlign': 'left'
                    }
                ],
                data=[],
                tooltip_header={
                    "classname": "classname of the item",
                    "coefficient": "this coefficient is used to calculate the dynamic price based on the current stock in the trader",
                    "max stock": "this value represent the max quantity of item the trader can accept",
                    "trade quantity": "it represent the quantity of the product you want to trade, if the quantity you have is below, the trader won't sell it, carefull about meat product !!! they need to use a coefficient ex: 0.75",
                    "buy price": "the buy price represent the highest price the trader is gonna ask you to buy the product",
                    "sell price": "the sell price represent the highest price the trader is gonna give you to sell your product",
                    "destock coefficient": "the destock coefficient will remove a % of the stock when the max stock is reached. ti will be apply after a restart if the destock feature is enabled",
                    "comments": "this cell is reserved for comments, I recommend to keep them short"
                },
                style_data_conditional=[
                    {
                        'backgroundColor': 'tomato',
                        'if': {
                            'filter_query': '{coefficient} != -1 && {coefficient} < 0.01 && {coefficient} > 1.0',
                            'column_id': 'coefficient'
                        },
                        'color': 'white'
                    },
                ],
                tooltip_duration=None,
                editable=True,
                persistence=True,
                persistence_type='session',
                is_focused=True,
                filter_action="native",
                sort_mode="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=20,
            ),
            width={'size': 10, "offset": 1, 'order': 1}
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Button("Add Product", color="primary", id='editing-rows-button', n_clicks=0),
            width={'size': "auto", "offset": 3, 'order': 1}
        ),
        dbc.Col(
            dbc.Input(id="cell_target_value", type="any", debounce=True, value="",
                      placeholder="set value to apply", size="md"),
            width={'size': "auto", "offset": 0, 'order': 2}
        ),
        dbc.Col(
            dbc.Button("Apply", color="success", id='btn_cell_target_value', n_clicks=0),
            width={'size': "auto", "offset": 0, 'order': 3}
        ),
        dbc.Tooltip(
            "right-click - open in new tab or you'll loose everything !",
            target="documentation-link",
        ),
        dbc.Tooltip(
            "right-click - open in new tab or you'll loose everything !",
            target="donate-link",
        ),
        dbc.Col(
            html.Div(id='message-output', children=[]),
            width={'size': "auto", "offset": 0, 'order': 7}
        ),
        dbc.Col(
            dbc.Input(id="buy_price_min", type="numeric", debounce=True, value="",
                      placeholder="minimal buy price", size="md"),
            width={'size': "auto", "offset": 0, 'order': 4}
        ),
        dbc.Tooltip(
            "set the lowest buy price you want to have when the stock is reached",
            target="buy_price_min",
        ),
        dbc.Col(
            dbc.Input(id="sell_price_min", type="numeric", debounce=True, value="",
                      placeholder="minimal sell price", size="md"),
            width={'size': "auto", "offset": 0, 'order': 5}
        ),
        dbc.Tooltip(
            "set the lowest sell price you want to have when the stock is reached",
            target="sell_price_min",
        ),
        dbc.Col(
            dbc.Button("Calculate coefficient", color="success", id='btn_calculate_coefficient', n_clicks=0),
            width={'size': "auto", "offset": 0, 'order': 5}
        ),
        dbc.Tooltip(
            "Make sure to select the coefficient cell of the product you want to calculate. You also need to make sure buy price and sell price are given so the calcul can be done correctly",
            target="bttn_calculate_coefficient",
        ),
    ]),
])


def fillDropDownMenu(categories):
    return [{'label': i["CategoryName"], 'value': index} for index, i in enumerate(categories)];


def check_for_duplicate_category(categories):
    categories_name = []
    for category in categories:
        categories_name.append(category["CategoryName"])
    for cat_name in categories_name:
        if categories_name.count(cat_name) > 1:
            return "duplicate category found ! Each category name must be specific! :" + cat_name


@app.callback(
    Output('session', 'data'),
    Output('category_dropdown', 'options'),
    Output('category_name_input', 'value'),
    Output('add_category', 'n_clicks'),
    Input('category_name_input', 'value'),
    Input('add_category', 'n_clicks'),
    Input('remove_category', 'n_clicks'),
    Input('upload-data', 'contents'),
    Input('upload-data', 'filename'),
    Input('products_table', 'selected_cells'),
    Input('products_table', 'derived_virtual_data'),
    Input('code_input','value'),
    State('category_dropdown', 'value'),
    State('session', 'data'),
    prevent_initial_call=True
)
def change_category_name(newCategoryName, n_clicks, remove_n_clicks, contents, filename, selected_cells,
                         post_filter_rows,code_input, value, data):
    ctx = dash.callback_context

    if ctx.triggered[0]['prop_id'] == 'upload-data.contents' and contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        file = io.StringIO(decoded.decode('utf-8'))
        if filename.__contains__('.xml'):
            if data is not None:
                df = pd.read_xml(file)
                products = []
                for index, product in enumerate(df['name']):
                    products.append('' + str(df['name'][index]) + ',1,' + str(df['nominal'][index]) + ',-1,-1,-1')
                data['dataframe']['0'][3].append({"CategoryName": filename.replace('.xml', ''), "Products": products})
                return data, fillDropDownMenu(data['dataframe']['0'][3]), '', 0
        elif filename.__contains__('.json'):
            df = pd.read_json(file, orient='index')
            check_for_duplicate_category(df.values[3][0])
            dff = {'dataframe': df.to_dict('series')}
            return dff, fillDropDownMenu(df.values[3][0]), '', 0
        else:
            raise PreventUpdate

    if ctx.triggered[0]['prop_id'] == 'products_table.derived_virtual_data' or ctx.triggered[0][
        'prop_id'] == 'products_table.selected_cells':
        if data is not None and post_filter_rows is not None:
            data['dataframe']['0'][3][value]['Products'].clear()
            products=[]
            for row in post_filter_rows:
                product = row['classname'] + "," + str(row['coefficient']) + "," + str(row['max stock'])+ "," + str(row['trade quantity'])+ "," + str(row['buy price'])+ "," + str(row['sell price'])+ "," + str(row['destock coefficient']) + "," + str(row['comments'])
                product = product.replace(',,','')
                products.append(product)
            data['dataframe']['0'][3][value]['Products'] = products
            return data, fillDropDownMenu(data['dataframe']['0'][3]), '', 0
        else:
            raise PreventUpdate

    if ctx.triggered[0]['prop_id'] == 'code_input.value':
        file = io.StringIO(code_input)
        df = pd.read_json(file, orient='index')
        check_for_duplicate_category(df.values[3][0])
        dff = {'dataframe': df.to_dict('series')}
        return dff, fillDropDownMenu(df.values[3][0]), '', 0

    if ctx.triggered[0]['prop_id'] == 'remove_category.n_clicks':
        if remove_n_clicks > 0:
            data['dataframe']['0'][3].remove(data['dataframe']['0'][3][value])
            return data, fillDropDownMenu(data['dataframe']['0'][3]), '', 0

    if ctx.triggered[0]['prop_id'] == 'add_category.n_clicks':
        if n_clicks > 0:
            if selected_cells is not None:
                products = []
                for row in post_filter_rows:
                    products.append(row['classname'] + ',' + row['coefficient'] + ',' + row['max stock'] + ',' + row[
                        'trade quantity'] + ',' + row['buy price'] + ',' + row['sell price'] + ',' + row[
                                        'destock coefficient'] + ',' + row['comments'])
                data['dataframe']['0'][3].append({"CategoryName": "New Category", "Products": products})
                return data, fillDropDownMenu(data['dataframe']['0'][3]), '', 0
            else:
                data['dataframe']['0'][3].append(
                    {"CategoryName": "New Category", "Products": ['classname,1,-1,-1,-1,-1']})
                return data, fillDropDownMenu(data['dataframe']['0'][3]), '', 0

    if ctx.triggered[0]['prop_id'] == 'category_name_input.value':
        if newCategoryName == None or newCategoryName == '':
            raise PreventUpdate
        else:
            data['dataframe']['0'][3][value]["CategoryName"] = newCategoryName
            return data, fillDropDownMenu(data['dataframe']['0'][3]), '', 0


@app.callback(
    Output('message-output', 'children'),
    Output('download_json', 'data'),
    Input('save-button', 'n_clicks'),
    State('session', 'data'),
    prevent_initial_call=True
)
def save_button(n_clicks, data):
    if n_clicks > 0:
        print(data['dataframe']['0'][3])
        for j, category in enumerate(data['dataframe']['0'][3]):
            for i, product in enumerate(category['Products']):
                data['dataframe']['0'][3][j]['Products'][i] = product.replace(',,', '')
        print(data['dataframe']['0'][3])
        out_json = {'EnableAutoCalculation': data['dataframe']['0'][0],
                    'EnableAutoDestockAtRestart': data['dataframe']['0'][1],
                    'EnableDefaultTraderStock': data['dataframe']['0'][2],
                    'TraderCategories': data['dataframe']['0'][3]}
        return "Category successfully saved!", dict(content=json.dumps(out_json, indent=4),
                                                    filename="TraderPlusPriceConfig.json")


@app.callback(
    Output('products_table', 'data'),
    Output('editing-rows-button', 'n_clicks'),
    Input('editing-rows-button', 'n_clicks'),
    Input('category_dropdown', 'value'),
    Input('products_table', 'selected_cells'),
    Input('products_table', 'active_cell'),
    Input('products_table', 'derived_virtual_data'),
    Input('cell_target_value', 'value'),
    Input('btn_cell_target_value', 'n_clicks'),
    Input('btn_calculate_coefficient', 'n_clicks'),
    State('sell_price_min', 'value'),
    State('buy_price_min', 'value'),
    State('products_table', 'data'),
    State('products_table', 'columns'),
    State('session', 'data'),
    prevent_initial_call=True
)
def add_row(n_clicks, value, selected_cells, active_cell, post_filter_rows, target_value, apply_n_clicks,
            calculate_n_clicks, sell_price_min, buy_price_min, rows, columns, data):
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'products_table.derived_virtual_data' or ctx.triggered[0][
        'prop_id'] == 'products_table.selected_cells' or ctx.triggered[0]['prop_id'] == 'products_table.active_cell':
        raise PreventUpdate

    if ctx.triggered[0]['prop_id'] == 'btn_calculate_coefficient.n_clicks':
        if sell_price_min is not None or buy_price_min is not None:
            for row in rows:
                if row['classname'] == post_filter_rows[active_cell['row']]['classname']:
                    row['coefficient'] = '1'
                    minBuyPrice = int(buy_price_min)
                    maxBuyPrice = int(row['buy price'])
                    minSellPrice = int(sell_price_min)
                    maxSellPrice = int(row['sell price'])
                    maxstock = int(row['max stock'])
                    if maxBuyPrice > 8:
                        row['coefficient'] = str(pow((minBuyPrice / maxBuyPrice), (1 / (maxstock - 1))))
                        print(str(pow((minBuyPrice / maxBuyPrice), (1 / (maxstock - 1)))))
                        print(row['coefficient'])
                        print(row['classname'])
                        print(row)
                        return rows, 0
                    elif maxSellPrice > 8:
                        row['coefficient'] = str(pow((minSellPrice / maxSellPrice), (1 / (maxstock - 1))))
                        return rows, 0
                    else:
                        break

    if ctx.triggered[0]['prop_id'] == 'btn_cell_target_value.n_clicks':
        if target_value is not None and selected_cells is not None:
            print(selected_cells)
            for cell in selected_cells:
                for row in rows:
                    if row['classname'] == post_filter_rows[cell['row']]['classname']:
                        value = float(target_value)
                        if cell['column_id'] == 'sell price' and (value > 0.0 and value < 1.0):
                            row[cell['column_id']] = str(int(float(row['buy price']) * value))
                        else:
                            row[cell['column_id']] = target_value
            return rows, 0

    if value is None:
        return [], 0

    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
        return rows, 0

    if data['dataframe'] is None:
        raise PreventUpdate
    else:
        products = data['dataframe']['0'][3][value]["Products"]
        if rows is not None:
            rows.clear()
        else:
            rows = []
        for product in products:
            new_key = ['classname', 'coefficient', 'max stock', 'trade quantity', 'buy price', 'sell price',
                       'destock coefficient', 'comments']
            new_value = product.split(',')
            my_dict = dict(zip(new_key, new_value))
            my_dict.setdefault('destock coefficient', '')
            my_dict.setdefault('comments', '')
            if my_dict['comments'] != '' and my_dict['destock coefficient'] == '':
                my_dict['destock coefficient'] = 0.0
            rows.append(my_dict)
        return rows, 0


if __name__ == '__main__':
    app.run_server(debug=True)
