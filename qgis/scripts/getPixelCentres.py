import math
from qgis.core import (
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsFeature,
    QgsField
)
from PyQt5.QtCore import QVariant
import processing  # Added implicit processing import

# 1. SET YOUR PARAMETERS
GROUP_NAME = "HartRasters" # Replace with your actual QGIS group name

# Find the target layer group
root = QgsProject.instance().layerTreeRoot()
group = root.findGroup(GROUP_NAME)

if not group:
    print(f"Group '{GROUP_NAME}' not found.")
else:
    # 2. LOOP THROUGH ALL RASTER LAYERS IN THE GROUP
    for child in group.children():
        if child.layer() and isinstance(child.layer(), QgsRasterLayer):
            raster_layer = child.layer()
            raster_name = raster_layer.name()
            print(f"Processing: {raster_name}")

            # --- CALCULATE THE GRIDCELL VALUE USING PYTHON SLICING ---
            # Python is 0-indexed, so chars 1 to 7 in SQL translates to index 0:7.
            # .rstrip('_') mimics your regexp_replace(..., '_$', '') to clean trailing underscores.
            gridcell_value = raster_name[0:7].rstrip('_')

            # Step A: Run native pixel extraction to points (temporary layer)
            params = {
                'INPUT_RASTER': raster_layer,
                'RASTER_BAND': 1,
                'FIELD_NAME': 'VALUE',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }
            res = processing.run("native:pixelstopoints", params)
            temp_point_layer = res['OUTPUT']

            # Step B: Prepare a memory layer with added Row, Col, and Gridcell attributes
            crs_str = raster_layer.crs().authid()
            vector_layer = QgsVectorLayer(f"Point?crs={crs_str}", f"{raster_name}_points", "memory")
            provider = vector_layer.dataProvider()

            # Add fields matching native output + Row, Col, & Gridcell
            provider.addAttributes([
                QgsField("VALUE", QVariant.Double),
                QgsField("Row", QVariant.Int),
                QgsField("Col", QVariant.Int),
                QgsField("Gridcell", QVariant.String)  # Added Gridcell field
            ])
            vector_layer.updateFields()

            # Step C: Retrieve raster metadata for math calculation
            extent = raster_layer.extent()
            x_min = extent.xMinimum()
            y_max = extent.yMaximum()
            x_res = raster_layer.rasterUnitsPerPixelX()
            y_res = raster_layer.rasterUnitsPerPixelY()

            # Step D: Process features and calculate row/col indices
            new_features = []
            for feat in temp_point_layer.getFeatures():
                geom = feat.geometry()
                pt = geom.asPoint()

                # Math conversion from map coordinate back to grid matrix
                col = int(math.floor((pt.x() - x_min) / x_res))
                row = int(math.floor((y_max - pt.y()) / y_res))

                # Map values to the newly initialized feature layout
                new_feat = QgsFeature(vector_layer.fields())
                new_feat.setGeometry(geom)
                new_feat.setAttribute("VALUE", feat["VALUE"])
                new_feat.setAttribute("Row", row)
                new_feat.setAttribute("Col", col)
                new_feat.setAttribute("Gridcell", gridcell_value)  # Populated Gridcell text
                new_features.append(new_feat)

            # Add populated features to the memory provider
            provider.addFeatures(new_features)
            vector_layer.updateExtents()

            # Step E: Load output point layer into the project
            QgsProject.instance().addMapLayer(vector_layer)
            print(f"Successfully created point layer for {raster_name}")

    print("Batch processing complete.")
