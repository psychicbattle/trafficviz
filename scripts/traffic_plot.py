from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs, TableColumn, DataTable, RadioGroup

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application

import pandas as pd
import os

from bokeh.models import GMapOptions
from bokeh.plotting import gmap
from bokeh.models.tools import WheelZoomTool

colors_to_violations = {"INSPECTION":"blue","STOP/YIELD":"yellow","SPEEDING":"red","CROSSWALK":"orange"}


def modify_doc(dataset_coords):

    tooltips =[('Violation Type', '@ViolationType'),
                                    ('Speed Limit', '@SpeedLimit'),
                                    ('Vehicle Speed', '@VehicleSpeed')]

    def make_dataset(violations_list, warnings_value, speeding_over_limit = 0):
        applicable_violations = pd.DataFrame(columns=['ViolationType','X','Y','SpeedLimit','VehicleSpeed','color','border_color'])

        for i, violation in enumerate(violations_list):
            subset = dataset_coords[dataset_coords["chgdesc"].str.contains(violation)]
            if warnings_value == "CITATIONS":
                subset = subset[subset["warning"]!="Y"]
            if warnings_value == "WARNINGS":
                subset = subset[subset["warning"]=="Y"]
            #print(violation, len(subset))
            if "SPEED" in violation and speeding_over_limit > 0:
                subset_w_speeds = subset.dropna(subset=["vehiclemph","mphzone"])
                subset_over_limit = subset_w_speeds.vehiclemph - subset_w_speeds.mphzone > speeding_over_limit
                subset = subset_w_speeds[subset_over_limit]

            arr_df = pd.DataFrame({'X':subset.X,'Y':subset.Y,
                                   'SpeedLimit':subset.mphzone,'VehicleSpeed':subset.vehiclemph,
                                   'is_warning':subset.warning.map({'Y':True,'':False})})
                                   #color':Category20_16[i]})
            arr_df['color'] = colors_to_violations[violation]
            arr_df["ViolationType"] = violation
            applicable_violations = applicable_violations.append(arr_df)
        cds = ColumnDataSource(applicable_violations)
        #print(cds.column_names)
        return cds


    def style(p):
        # Title
        p.title.align = 'center'
        p.title.text_font_size = '20pt'
        p.title.text_font = 'serif'

        # Axis titles
        p.xaxis.axis_label_text_font_size = '14pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size = '14pt'
        p.yaxis.axis_label_text_font_style = 'bold'

        # Tick labels
        p.xaxis.major_label_text_font_size = '12pt'
        p.yaxis.major_label_text_font_size = '12pt'

        return p

    def make_plot(src):
        # Blank plot with correct labels
        #42.387035, -71.107639
        #print(src)
        map_options = GMapOptions(lat=42.387035, lng=-71.107639, map_type="roadmap", zoom=13)

        # Replace the value below with your personal API key:
        api_key = os.environ["GOOGLE_API_KEY"]

        p = gmap(api_key, map_options, title="Somerville Traffic Enforcement")
        geomap_wheel_zoom = WheelZoomTool()
        p.add_tools(geomap_wheel_zoom)
        p.toolbar.active_scroll = geomap_wheel_zoom

        data = dict(lat=src.data["Y"],lon=src.data["X"],color=src.data["color"],
                   ViolationType=src.data["ViolationType"])
                   #border_color=src.data["border_color"])
        # Quad glyphs to create a histogram
        global current_circles
        #do a dummy call with one of each and no alpha to populate legend
        for key in colors_to_violations:
            p.circle(x=-1,y=-1,size=0,fill_color=colors_to_violations[key], fill_alpha=1,legend=key)

        current_circles = p.circle(x="lon", y="lat", size=8, fill_color='color',
                                   fill_alpha=0.05, source=data, line_alpha=0)#legend='ViolationType')

        # Hover tool with vline mode
        #hover = HoverTool(tooltips=[('Violation Type', '@ViolationType'),
        #                            ('Speed Limit', '@SpeedLimit'),
        #                            ('Vehicle Speed', '@VehicleSpeed')],
        #                  mode='mouse')
        #
        #p.add_tools(hover)

        # Styling
        p = style(p)

        return p



    def update(attr, old, new):
        violations_to_plot = [violation_selection.labels[i] for i in violation_selection.active]
        warnings = warn_selection.labels[warn_selection.active]

        new_src = make_dataset(violations_to_plot, warnings)
        global p, current_circles
        #p.reset.emit()
        #p['plot_obj'].legend[0].legends.pop(0)
        data = dict(lat=new_src.data["Y"],lon=new_src.data["X"],color=new_src.data["color"],
                   ViolationType=new_src.data["ViolationType"])
        current_circles.visible = False
        current_circles = p.circle(x="lon", y="lat", size=8, fill_color='color',
                                   fill_alpha=0.05, source=data, line_alpha=0)

        src.data.update(new_src.data)

    all_violations = ["INSPECTION","STOP/YIELD","SPEEDING","CROSSWALK"]
    violation_selection = CheckboxGroup(labels=all_violations, active = [1,2,3])
    violation_selection.on_change('active', update)

    warn_selection = RadioGroup(labels=["WARNINGS","CITATIONS","BOTH"], active=2)
    warn_selection.on_change('active', update)


    initial_violations = [violation_selection.labels[i] for i in violation_selection.active]
    initial_warning = warn_selection.labels[warn_selection.active]
    src = make_dataset(initial_violations, initial_warning)
    global p
    p = make_plot(src)
    controls = WidgetBox(violation_selection, warn_selection)
    layout = row(controls, p)
    tab = Panel(child=layout, title="Traffic Violations Mapping")
    return tab
