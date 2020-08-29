import shapefile, json, pyproj, os, sys, shutil
from pyproj.enums import WktVersion

class GenrateShapefile:
    def ReadGeoJsonData(self, GeojsonData):
        FeatureGeometryMap = {}
        FeatureCount = 0 

        # Load GeoJson To a Dict Object
        GeojsonDict = json.loads(GeojsonData)

        # Extract GeoJson Schema and Doordinates
        featureCollection = GeojsonDict['features']
        for feature in featureCollection:
            featureProperties = feature['properties']
            geometry= feature['geometry']['coordinates']

            FeatureCount +=1
            FeatureGeometryMap[FeatureCount] = (featureProperties, list(geometry))
        
        return FeatureGeometryMap
        
    def CreateShapefile(self, ShapefileLocation, ShapefileName, GeojsonFileName, GeometryTypeCode):
        # Check if Path Exists
        if not os.path.exists(ShapefileLocation):
            os.mkdir(ShapefileLocation)

        if not os.path.exists(GeojsonFileName):
            print ("Error Geojson Not Found")
            return

        try:
            shpFile = None
            geojsonStringData  = open(GeojsonFileName, 'r').read()
            
            featureDataMap = self.ReadGeoJsonData(geojsonStringData)
            
            # Write featureDataMap to Shapefile
            addField = True
            with shapefile.Writer(os.path.join(ShapefileLocation, ShapefileName + '.shp')) as shpFile:

                shpFile.autoBalance = True
                shpFile.shapeType = GeometryTypeCode

                for featureId in featureDataMap.keys():
                    props, geom = featureDataMap[featureId]

                    rowData = []
                    
                    if not bool(props):
                        shpFile.field("Type", 'C')
                        shpFile.record(GeomType)

                    if addField:
                        for fieldName in props.keys():
                            shpFile.field(fieldName)

                        addField = False

                    shpFile.record(**props)
                    
                    #     ''' POINT = 1, POLYLINE = 3, POLYGON = 5 '''
                        
                    # Check for Geometry type and call API accordinly.
                    if (GeometryTypeCode == 5):
                        shpFile.poly(geom)
                    
                    elif (GeometryTypeCode == 3):
                        shpFile.line([geom])

                    elif (GeometryTypeCode == 1):
                        shpFile.point(geom[0], geom[1])



                shpFile.close()
            
            
            projData = pyproj.CRS.from_epsg(4326)
            projFile = open(os.path.join(ShapefileLocation, ShapefileName + '.prj'), 'w')
            projFile.write(projData.to_wkt(WktVersion.WKT1_ESRI, pretty = False))
            projFile.close()
            
            print("ShapeFile Genrated")
            print("ShapeFile Location is " + os.path.join(ShapefileLocation, ShapefileName + '.shp'))



        except Exception as e:
            # shpFile.close()
            print("Error Occred")
            print(e.args[0])
            shutil.rmtree(ShapefileLocation)

if __name__ == '__main__':
    FileLocation =  sys.argv[1]
    FileName = sys.argv[2]
    GeoJsonFile = sys.argv[3]
    GeomType = str.upper(sys.argv[4])
    
    GeometryTypeCode = 0

    if GeomType == 'POLYGON':
        GeometryTypeCode = 5
    
    elif GeomType == 'POINT':
        GeometryTypeCode = 1

    elif GeomType in ['LINE','POLYLINE']:
        GeometryTypeCode = 3

    else:
        print("Geometry Type " + GeomType + " is Not Yet Supported ")
    
    shpGen = GenrateShapefile()
    shpGen.CreateShapefile(FileLocation, FileName,GeoJsonFile, GeometryTypeCode)