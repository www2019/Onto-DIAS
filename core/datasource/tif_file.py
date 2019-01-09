import gdal, ogr, os, osr
import sys

def array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()


def raster2array(rasterfn, band_num):
    try:
        src_ds = gdal.Open(rasterfn)
    except RuntimeError as e:
        print('Unable to open')
        print(e)
        sys.exit(1)

    try:
        srcband = src_ds.GetRasterBand(band_num)
    except RuntimeError as e:
        # for example, try GetRasterBand(10)
        print('Band ( %i ) not found' % band_num)
        print(e)
        sys.exit(1)

    if srcband == None:
        return None

    array = srcband.ReadAsArray()
    return array


def loop_all_raster_bands(fn):
    src_ds = gdal.Open(fn)
    if src_ds is None:
        print('Unable to open %s' % fn)
        sys.exit(1)

    print("[ RASTER BAND COUNT ]: %s" % str(src_ds.RasterCount))

    res = []

    for band in range(src_ds.RasterCount):
        band += 1
        print("[ GETTING BAND ]: %s" % str(band))
        array = raster2array(fn, band)
        if array is None:
            continue

        res.append(array)

    return res


def create_raster_from_array(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):
    reversed_arr = array[::-1]  # reverse array so the tif looks like the array
    array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, reversed_arr)  # convert array to raster


def transform_raster_to_array(fn):
    all_arr = loop_all_raster_bands(fn)
    if len(all_arr) == 1:
        return all_arr[0]

    if len(all_arr) == 0:
        return None

    res = []
    for arr in all_arr:
        res += arr

    return res
