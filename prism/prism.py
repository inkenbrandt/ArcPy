__author__ = 'jbellino'
import os
import csv
import gdal
import gdalconst
import zipfile as zf
import numpy as np
import pandas as pd
from unitconversion import *

prismGrid_shp = r'G:\archive\datasets\PRISM\shp\prismGrid_p.shp'
prismGrid_pts = r'G:\archive\datasets\PRISM\shp\prismGrid_p.txt'
prismProj = r'G:\archive\datasets\PRISM\shp\PRISM_ppt_bil.prj'
ncol = 1405
nrow = 621
max_grid_id = ncol * nrow

def getMonthlyPrecipData(year, month, mask=None, conversion=None):
    # print 'Getting data for', year, month
    bil = r'/vsizip/G:\archive\datasets\PRISM\monthly\ppt\{0}\PRISM_ppt_stable_4kmM2_{0}_all_bil.zip\PRISM_ppt_stable_4kmM2_{0}{1:0>2d}_bil.bil'.format(year, month)
    b = BilFile(bil, mask=mask)
    data = b.data
    if conversion is not None:
        data *= conversion
    # b.save_to_esri_grid('ppt_{}'.format(year), conversion_factor=mm_to_in)
    return data


def getAnnualPrecipData(year, mask=None, conversion=None):
    # print 'Getting data for year', year
    bil = r'/vsizip/G:\archive\datasets\PRISM\monthly\ppt\{0}\PRISM_ppt_stable_4kmM2_{0}_all_bil.zip\PRISM_ppt_stable_4kmM2_{0}_bil.bil'.format(year)
    b = BilFile(bil, mask=mask)
    data = b.data
    if conversion is not None:
        data *= conversion
    # b.save_to_esri_grid('ppt_{}'.format(year), conversion_factor=mm_to_in)
    return data


def getGridIdFromRowCol(row, col):
    """
    Determines the PRISM grid id based on a row, col input.
    """
    assert 1 <= row <= nrow, 'Valid row numbers are bewteen 1 and {}.'.format(nrow)
    assert 1 <= col <= ncol, 'Valid col numbers are bewteen 1 and {}.'.format(ncol)
    grid_id = ((row-1)*ncol)+col
    return grid_id


def getRowColFromGridId(grid_id):
    """
    Determines the row, col based on a PRISM grid id.
    """
    assert 1 <= grid_id <= max_grid_id, 'Valid Grid IDs are bewteen 1 and {}, inclusively.'.format(max_grid_id)
    q, r = divmod(grid_id, ncol)
    return q+1, r


def writeGridPointsToTxt(prismGrid_shp=prismGrid_shp, out_file=prismGrid_pts):
    """
    Writes the PRISM grid id, row, and col for each feature in the PRISM grid shapefile.
    """
    import arcpy
    data = []
    rowends = range(ncol, max_grid_id+1, ncol)
    with arcpy.da.SearchCursor(prismGrid_shp, ['grid_code', 'row', 'col']) as cur:
        rowdata = []
        for rec in cur:
            rowdata.append(rec[0])
            if rec[2] in rowends:
                data.append(rowdata)
                rowdata = []
    a = np.array(data, dtype=np.int)
    np.savetxt(out_file, a)


def getGridPointsFromTxt(prismGrid_pts=prismGrid_pts):
    """
    Returns an array of the PRISM grid id, row, and col for each feature in the PRISM grid shapefile.
    """
    a = np.genfromtxt(prismGrid_pts, dtype=np.int, usemask=True)
    return a


def makeGridMask(grid_pnts, grid_codes=None):
    """
    Makes a mask with the same shape as the PRISM grid.
    'grid_codes' is a list containing the grid id's of those cells to INCLUDE in your analysis.
    """
    mask = np.ones((nrow, ncol), dtype=bool)
    for row in range(mask.shape[0]):
        mask[row] = np.in1d(grid_pnts[row], grid_codes, invert=True)
    return mask


def downloadPrismFtpData(parm, output_dir=os.getcwd(), timestep='monthly', years=None, server='prism.oregonstate.edu'):
    """
    Downloads ESRI BIL (.hdr) files from the PRISM FTP site.
    'parm' is the parameter of interest: 'ppt', precipitation; 'tmax', temperature, max' 'tmin', temperature, min /
                                         'tmean', temperature, mean
    'timestep' is either 'monthly' or 'daily'. This string is used to direct the function to the right set of remote folders.
    'years' is a list of the years for which data is desired.
    """
    from ftplib import FTP

    def handleDownload(block):
        file.write(block)
        # print ".\n"

    # Play some defense
    assert parm in ['ppt', 'tmax', 'tmean', 'tmin'], "'parm' must be one of: ['ppt', 'tmax', 'tmean', 'tmin']"
    assert timestep in ['daily', 'monthly'], "'timestep' must be one of: ['daily', 'monthly']"
    assert years is not None, 'Please enter a year for which data will be fetched.'
    if isinstance(years, int):
        years = list(years)
    ftp = FTP(server)
    print 'Logging into', server
    ftp.login()

    # Wrap everything in a try clause so we close the FTP connection gracefully
    try:
        for year in years:
            dir = 'monthly'
            if timestep == 'daily':
                dir = timestep
            dir_string = '{}/{}/{}'.format(dir, parm, year)
            remote_files = []
            ftp.dir(dir_string, remote_files.append)
            for f_string in remote_files:
                f = f_string.rsplit(' ')[-1]
                if not '_all_bil' in f:
                    continue
                print 'Downloading', f
                if not os.path.isdir(os.path.join(output_dir, str(year))):
                    os.makedirs(os.path.join(output_dir, str(year)))
                local_f = os.path.join(output_dir, str(year), f)
                with open(local_f, 'wb') as file:
                    f_path = '{}/{}'.format(dir_string, f)
                    ftp.retrbinary('RETR ' + f_path, handleDownload)
    except Exception as e:
        print e
    finally:
        print('Closing the connection.')
        ftp.close()
    return


class BilFile(object):
    """
    This class returns a BilFile object using GDAL to read the array data. Data units are in millimeters.
    """

    def __init__(self, bil_file, mask=None):
        self.bil_file = bil_file
        self.hdr_file = bil_file[:-3]+'hdr'
        gdal.GetDriverByName('EHdr').Register()
        self.get_array(mask=mask)
        self.originX = self.geotransform[0]
        self.originY = self.geotransform[3]
        self.pixelWidth = self.geotransform[1]
        self.pixelHeight = self.geotransform[5]


    def get_array(self, mask=None):
        self.data = None
        img = gdal.Open(self.bil_file, gdalconst.GA_ReadOnly)
        band = img.GetRasterBand(1)
        self.nodatavalue = band.GetNoDataValue()
        self.data = band.ReadAsArray()
        self.data = np.ma.masked_where(self.data==self.nodatavalue, self.data)
        if mask is not None:
            self.data = np.ma.masked_where(mask==True, self.data)
        self.ncol = img.RasterXSize
        self.nrow = img.RasterYSize
        self.geotransform = img.GetGeoTransform()

    def save_to_esri_grid(self, out_grid, conversion_factor=None, proj=None):
        import arcpy
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = os.getcwd()
        arcpy.CheckOutExtension('Spatial')
        arcpy.env.outputCoordinateSystem = prismProj
        if proj is not None:
            arcpy.env.outputCoordinateSystem = proj
        df = np.ma.filled(self.data, self.nodatavalue)
        llx = self.originX
        lly = self.originY - (self.nrow * -1 * self.pixelHeight)
        point = arcpy.Point(llx, lly)
        r = arcpy.NumPyArrayToRaster(df, lower_left_corner=point, x_cell_size=self.pixelWidth,
                                     y_cell_size=-1*self.pixelHeight, value_to_nodata=self.nodatavalue)
        if conversion_factor is not None:
            r *= conversion_factor
        r.save(out_grid)

    def __extract_bil_from_zip(self, parent_zip):
        with zf.ZipFile(parent_zip, 'r') as myzip:
            if self.bil_file in myzip.namelist():
                myzip.extract(self.bil_file, self.pth)
                myzip.extract(self.hdr_file, self.pth)
        return

    def __clean_up(self):
        try:
            os.remove(os.path.join(self.pth, self.bil_file))
            os.remove(os.path.join(self.pth, self.hdr_file))
        except:
            pass


if __name__ == '__main__':
    grid_id = getGridIdFromRowCol(405, 972)
    print grid_id
    row, col = getRowColFromGridId(grid_id)
    print row, col


