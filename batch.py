#!/usr/bin/env python

import pandas as pd
from jinja2 import Environment, FileSystemLoader
from Utils import beans_to_roast, beans_remove_inventory, df_labels, rename_labels, get_final_blend_grams
from PivotUtils import create_lb_pivot, create_gm_pivot, create_batch_df, create_green_inventory, create_green_pivot, create_bag_pivot, create_blend_df
import argparse
import time
import os
from tabulate import tabulate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate file in Coffee Batches folder for (batch #)')
    parser.add_argument('batch', type=int, help='batch #')
    args = parser.parse_args()

    # Prepares jinga2 templates
    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template('report.html')

    t = time.localtime()
    timestamp = time.strftime('%b-%d-%Y', t)

    # Read in the excel file
    xls = pd.ExcelFile('../BatchSpreadsheet.xlsx')
    dfBeans = pd.read_excel(xls, sheet_name="Beans", converters={'IS': str, 'Batch#': int, 'Roast': str})
    dfBeanTypeInfo = pd.read_excel(xls, sheet_name="BeanTypeInfo")
    dfGreenBeans = pd.read_excel(xls, sheet_name="GreenBeans")

    """
    Batch
    """
    dfBeans = dfBeans[dfBeans['Batch#'] == args.batch]
    dfLabels = df_labels(dfBeans)


    """
    Inventory
    """
    # removes empty beans, removes instock beans, adds green lb column
    dfGreen = beans_remove_inventory(dfBeans)
    dfGreenBatch = create_green_inventory(dfGreen, dfBeanTypeInfo)

    # get blends only, without the 1.16 shrinkage
    dfBlends = beans_remove_inventory(dfBeans, shrinkage=1)
    dfBlends = get_final_blend_grams(dfBlends, dfBeanTypeInfo)
    dfBlendBatch = create_blend_df(dfBlends, dfBeanTypeInfo)

    dfBlendInfo = dfBlendBatch.groupby(['Coffee Type', 'Green Bean']).sum()
    dfBlendTotal = dfBlendBatch.groupby(['Coffee Type']).sum()

    """
    Roast
    """
    # Clean up Beans table and add column for green weight(lb & oz)

    dfBeans = beans_to_roast(dfBeans)
    # creates data for pivot tables


    dfBatch = create_batch_df(dfBeans, dfBeanTypeInfo)

    """
    Pivots
    """
    # Create pivots
    # print(tabulate(dfBatch, floatfmt='.2f'))
    # print(dfBatch)
    gm_pivot = create_gm_pivot(dfBatch)
    lb_pivot = create_lb_pivot(dfBatch)
    green_pivot = create_green_pivot(dfGreenBatch)
    bag_pivot = create_bag_pivot(dfLabels)

    bag_pivot = rename_labels(bag_pivot)

    """
    Styling
    """
    # Add bootstrap style to tables
    html_lb_pivot = lb_pivot.style.set_table_attributes('class="table table-striped table-bordered"').render()
    html_gm_pivot = gm_pivot.style.set_table_attributes('class="table table-striped table-bordered"').render()

    html_bag_pivot = "<h3>No beans to bag. No beans in batch or all of them are marked as in stock.</h3>"
    if len(bag_pivot):
        html_bag_pivot = bag_pivot.style.set_table_attributes('class="table table-striped table-bordered"').render()

    html_green_pivot = "<h3>No Inventory used</h3>"
    if len(green_pivot) > 0:
        html_green_pivot = green_pivot.style.set_table_attributes('class="table table-striped table-bordered"').render()

    html_blend_info = dfBlendInfo.style.set_table_attributes('class="table table-striped table-bordered"').render()
    html_blend_total = dfBlendTotal.style.set_table_attributes('class="table table-striped table-bordered"').render()

    """
    Template
    """
    # Template variables
    template_vars = {
        # "title": "Batch " + str(args.batch) + " - " + timestamp,
        # "batch_pivot_lb": html_lb_pivot,
        "batch_pivot_gm": html_gm_pivot,
        "bag_pivot": html_bag_pivot,
        # "green_pivot": html_green_pivot,
        "blend_total": html_blend_total,
        "blend_info": html_blend_info
    }

    # Render template
    html_out = template.render(template_vars)

    """
    Create Batches Directory
    """
    batch_dir = os.path.join(os.pardir,"Batches")

    if not os.path.exists(batch_dir):
        os.makedirs(batch_dir)

    os.chdir(batch_dir)

    """
    Create filename with time stamp
    """
    BATCH_NAME = (str(args.batch) + "-batch" + ".html")

    # Create HTML version of the report
    with open(BATCH_NAME, 'w') as f:
        f.write(html_out)
        f.close()
        print('\n------------------ Batch Creator ----------')
        print("Batch "+ str(args.batch) +" saved as: " + BATCH_NAME)
        print('---------- Batch(gm) ----------')
        headers = ['Green Bean', 'gram']
        print(tabulate(gm_pivot, headers='keys', tablefmt='fancy_grid', floatfmt='.0f'))
        pass
