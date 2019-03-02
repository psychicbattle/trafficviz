from bokeh.palettes import Category20_16
from bokeh.io import curdoc
from bokeh.io import show, output_notebook, push_notebook
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs, TableColumn, DataTable

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application

from scripts.traffic_plot import modify_doc 

import pandas as pd

import os
dataset_f = os.environ["citationscsv"]

dataset = pd.read_csv(dataset_f)
#drop datasets without coordinates
#print(dataset["X"].isna())
dataset_coords = dataset.dropna(subset=['X','chgdesc'])
#print(dataset_coords["X"])

maintab = modify_doc(dataset_coords)
tabs = Tabs(tabs=[maintab])

#handler=FunctionHandler(modify_doc)
#app = Application(handler)
curdoc().add_root(tabs)
