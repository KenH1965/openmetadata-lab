import json
import yaml

def add_widget_to_ui():
    # Load the existing UI configuration
    path = 'src/config/widget.yaml'
    with open(path, 'r') as widget_file:
        if path.endswith('.yaml'):
            widget_config = yaml.safe_load(widget_file)
        else:
            widget_config = json.load(widget_file)

    # Define the Data Products widget properties
    data_products_widget = {
        "name": "DataProductsWidget",
        "type": "widget",
        "properties": {
            "title": "Data Products",
            "description": "Displays key metrics and a list of data products.",
            "dataSource": "dataProductsAPI",
            "layout": {
                "position": "sidebar",
                "size": "medium"
            }
        }
    }

    # Add the Data Products widget to the configuration
    widget_config['widgets'].append(data_products_widget)

    # Save the updated widget configuration
    with open(path, 'w') as widget_file:
        yaml.safe_dump(widget_config, widget_file, sort_keys=False)

    print("Data Products widget added to UI configuration.")

if __name__ == "__main__":
    add_widget_to_ui()