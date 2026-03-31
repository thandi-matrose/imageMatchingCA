def readOil():
    
    oilspill = xr.load_dataset("OilSpill.nc")
    print(oilspill._variables)
def getImg():
    connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
    aoi = {
    "type": "Polygon",
    "coordinates": [
        [
            [48.325487506118264, 28.742803969343313],
            [48.325487506118264, 28.414218984218607],
            [48.75387693420447, 28.414218984218607],
            [48.75387693420447, 28.742803969343313],
            [48.325487506118264, 28.742803969343313],
        ]
    ],
}
    s1_image = connection.load_collection(
    "SENTINEL1_GRD",
    temporal_extent=["2025-08-09", "2025-08-11"],
    spatial_extent=aoi,
    bands=["VV"],
)

    s1_image = s1_image.sar_backscatter(coefficient="sigma0-ellipsoid")
    
    #s1_image = s1_image.apply(process=lambda data: 10 * openeo.processes.log(data, base=10))

    s1_image = s1_image.rename_labels(dimension="bands", target=["amplitude"])
    oil_spill = s1_image.band("amplitude")
    oil_spill.execute_batch(title="Oil Spill Data", outputfile="OilSpill.nc")
   