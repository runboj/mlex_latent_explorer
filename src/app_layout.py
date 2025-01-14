from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from dash.long_callback import DiskcacheLongCallbackManager
import plotly.graph_objects as go
import dash_uploader as du
import diskcache
import pathlib
import os

import templates
from file_manager.main import FileManager

### GLOBAL VARIABLES
ALGORITHM_DATABASE = {"PCA": "PCA", "UMAP": "UMAP",}
CLUSTER_ALGORITHM_DATABASE = {"KMeans": "KMeans", "DBSCAN": "DBSCAN", "HDBSCAN": "HDBSCAN"}

DATA_OPTION = [
    {"label": "Synthetic Shapes", "value": "data/example_shapes/Demoshapes.npz"},
    {"label": "Latent representations from encoder-decoder model", "value": "data/example_latentrepresentation/f_vectors.parquet"}
]
DOCKER_DATA = pathlib.Path.home() / 'data'  #/app/work/data
UPLOAD_FOLDER_ROOT = DOCKER_DATA / 'upload' #/app/work/data/upload

# DATA_CLINIC_OPTION = 

#### SETUP DASH APP ####
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)
external_stylesheets = [dbc.themes.BOOTSTRAP, "../assets/segmentation-style.css"]
app = Dash(__name__, 
           external_stylesheets=external_stylesheets, 
           suppress_callback_exceptions=True,
           long_callback_manager=long_callback_manager)

server = app.server

dash_file_explorer = FileManager(DOCKER_DATA, 
                                 UPLOAD_FOLDER_ROOT,
                                 open_explorer=False)
dash_file_explorer.init_callbacks(app)
du.configure_upload(app, UPLOAD_FOLDER_ROOT, use_upload_id=False)

#### BEGIN DASH CODE ####
header = templates.header()
# right panel: uploader, scatter plot, individual image  plot
image_panel = [
    dbc.Card(
        id="image-card",
        children=[
            dbc.CardHeader(
                [   
                    dbc.Label('Upload your own zipped dataset', className='mr-2'),
                    dash_file_explorer.file_explorer,
                    dbc.Label('Or select Data Clinic modal', className='mr-2'),
                    dcc.Dropdown(
                        id='feature-vector-model-list',
                        clearable=False,
                        style={'margin-bottom': '1rem'}
                    ),
                    dbc.Label('Or try Example Dataset', className='mr-2'),
                    dcc.Dropdown(
                        id='example-dataset-selection',
                        options=DATA_OPTION,
                        #value = DATA_OPTION[0]['value'],
                        clearable=False,
                        style={'margin-bottom': '1rem'}
                    ),
                ]
            ),
            dbc.CardBody(
                dcc.Graph(
                    id="scatter",
                    figure=go.Figure(go.Scattergl(mode='markers')),
                )
            ),
            dbc.CardFooter(
                dcc.Graph(
                    id="heatmap",
                    figure=go.Figure(go.Heatmap())
                )
            )
        ]
    )
]

# left panel: choose algorithms, submit job, choose scatter plot attributes, and statistics...
algo_panel = html.Div(
    [dbc.Card(
        id="algo-card",
        style={"width": "100%"},
        children=[
            dbc.Collapse(children=[
                dbc.CardHeader("Select Dimension Reduction Algorithms"),
                dbc.CardBody(
                    [
                                dbc.Label("Algorithm", className='mr-2'),
                                dcc.Dropdown(id="algo-dropdown",
                                                options=[{"label": entry, "value": entry} for entry in ALGORITHM_DATABASE],
                                                style={'min-width': '250px'},
                                                value='PCA',
                                                ),
                                html.Div(id='additional-model-params'),
                                html.Hr(),
                                html.Div(
                                    [
                                        dbc.Button(
                                            "Submit",
                                            color="secondary",
                                            id="run-algo",
                                            outline=True,
                                            size="lg",
                                            className="m-1",
                                            style={'width':'50%'}
                                        ),
                                    ],
                                    className='row',
                                    style={'align-items': 'center', 'justify-content': 'center'}
                                ),
                                html.Div(id='invisible-apply-div')
                    ]
                )
            ],
            id="model-collapse",
            is_open=True,
            style = {'margin-bottom': '0rem'}
            )
        ]
    )
    ]
)

cluster_algo_panel = html.Div(
    [
        dbc.Card(
            id="cluster-algo-card",
            style={"width": "100%"},
            children=[
                dbc.Collapse(children=[
                        dbc.CardHeader("Select Clustering Algorithms"),
                        dbc.CardBody([
                            dbc.Label("Algorithm", className='mr-2'),
                            dcc.Dropdown(id="cluster-algo-dropdown",
                                            options=[{"label": entry, "value": entry} for entry in CLUSTER_ALGORITHM_DATABASE],
                                            style={'min-width': '250px'},
                                            value='DBSCAN',
                                            ),
                            html.Div(id='additional-cluster-params'),
                            html.Hr(),
                            html.Div(
                                [
                                    dbc.Button(
                                        "Apply",
                                        color="secondary",
                                        id="run-cluster-algo",
                                        outline=True,
                                        size="lg",
                                        className="m-1",
                                        style={'width':'50%'}
                                    ),
                                ],
                                className='row',
                                style={'align-items': 'center', 'justify-content': 'center'}
                            ),
                            html.Div(id='invisible-submit-div')
                        ]

                        )
                    ],
                id="cluster-model-collapse",
                is_open=True,
                style = {'margin-bottom': '0rem'}
                )
            ]
        )
    ]
)

scatter_control_panel =  html.Div(
    [dbc.Card(
        style={"width": "100%"},
        children=[
            dbc.CardHeader("Scatter Plot Control Panel"),
            dbc.CardBody([
                        dbc.Label('Scatter Colors', className='mr-3'),
                        dcc.RadioItems(id='scatter-color',
                                        options=[
                                            {'label': 'cluster', 'value': 'cluster'},
                                            {'label': 'label', 'value': 'label'}
                                            ],
                                        value = 'cluster',
                                        style={'min-width': '250px'},
                                        className='mb-2'),
                        dbc.Label("Select cluster", className='mr-3'),
                        dcc.Dropdown(id='cluster-dropdown',
                                        value=-1,
                                        style={'min-width': '250px'},
                                        className='mb-2'),
                        dbc.Label("Select label", className='mr-3'),
                        dcc.Dropdown(id='label-dropdown',
                                        value=-2,
                                        style={'min-width': '250px'},
                                        )
            ])
        ]
    ),
    dcc.Interval(
        id='interval-component',
        interval=3000, # in milliseconds
        max_intervals=-1,  # keep triggering indefinitely, None
        n_intervals=0,
    ),
    ]
)

heatmap_control_panel =  html.Div(
    [dbc.Card(
        style={"width": "100%"},
        children=[
            dbc.CardHeader("Heatmap Control Panel"),
            dbc.CardBody([ 
                            dbc.Label([
                                    'Select a Group of Points using ',
                                    html.Span(html.I(DashIconify(icon="lucide:lasso")), className='icon'),
                                    ' or ',
                                    html.Span(html.I(DashIconify(icon="lucide:box-select")), className='icon'),
                                    ' Tools :'
                                    ], 
                                    className='mb-3'),
                            dbc.Label(id='stats-div', children=[
                                   'Number of images selected: 0',
                                   html.Br(),
                                   'Clusters represented: N/A',
                                   html.Br(),
                                   'Labels represented: N/A',
                                ]),
                            dbc.Label('Display Image Options', className='mr-3'),
                            dcc.RadioItems(id='mean-std-toggle',
                                           options=[
                                               {'label': 'Mean', 'value': 'mean'},
                                                {'label': 'Standard Deviation', 'value': 'sigma'}
                                                ],
                                           value = 'mean',
                                           style={'min-width': '250px'},
                                           className='mb-2'),
            ])
        ]
    )]
)

# add alert pop up window
modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Header")),
                dbc.ModalBody("This is the content of the modal", id="modal-body"),
            ],
            id="modal",
            is_open=False,
        ),
    ]
)


control_panel = [algo_panel, cluster_algo_panel, scatter_control_panel, heatmap_control_panel, modal]


# metadata
meta = [
    html.Div(
        id="no-display",
        children=[
            # Store for user created contents
            dcc.Store(id='image-length', data=0),
            dcc.Store(id='user-upload-data-dir', data=None),
            dcc.Store(id='dataset-options', data=DATA_OPTION),
            dcc.Store(id='run-counter', data=0),
            dcc.Store(id='experiment-id', data=None),
            # data_label_schema, latent vectors, clusters
            dcc.Store(id='input_labels', data=None),
            dcc.Store(id='label_schema', data=None),
            dcc.Store(id='model_id', data=None),
            dcc.Store(id='latent_vectors', data=None),
            dcc.Store(id='clusters', data=None),
        ],
    )
]


##### DEFINE LAYOUT ####
app.layout = html.Div(
    [
        header, 
        dbc.Container(
            children = [
                dbc.Row([ dbc.Col(control_panel, width=4), 
                         dbc.Col(image_panel, width=7)
                        ]),
                dbc.Row(dbc.Col(meta)),
            ]
        ),
        modal
    ]
)