from core.libs.GDAL_Libs.Layers import Raster, Feature

class PointBiserialCalc(QObject):
    """
    Point Biserial Calculation in extra Thread.
    """
    finishSignal = pyqtSignal(float, float, float, float, int, int, np.ndarray, np.ndarray, str, str)

    def __init__(self, discrete, continuous, inventory, projectLocation):
        super().__init__()
        self.discrete = discrete
        self.continuous = continuous
        self.inventory = inventory
        self.projectLocation = projectLocation

    def run(self):
        inventoryArray, rasterArray = self.getArrays(self.inventory, self.raster)
        rasterValuesWithLs, rasterValuesWithoutLs = self.getRasterValuesWithAndWithoutLs(
            inventoryArray, rasterArray
        )
        pointBiserial = self.calculatePointBiserial(
            rasterValuesWithLs, rasterValuesWithoutLs, rasterArray
        )
        self.finishSignal.emit(pointBiserial)

    def getArrays(self, inventory: str, raster: str) -> tuple:
        """
        Converts the feature file inventory into a raster file with raster as a mask to get
        its array and gets rasters array.
        Returns a tuple of numpy arrays: [0] = inventoryArray [1] = rasterArray
        """
        inventoryHandle = Feature(inventory)
        rasterHandle = Raster(raster)
        tmpRaster = os.path.join(self.projectLocation, "workspace", "tmp_raster.tif")
        inventoryHandle.rasterizeLayer(raster, tmpRaster)
        tmpInventoryRaster = Raster(tmpRaster)
        return (tmpInventoryRaster.getArrayFromBand(), rasterHandle.getArrayFromBand())

    def getRasterValuesWithAndWithoutLs(self, inventoryArray, rasterArray) -> tuple:
        """
        Returns a tuple of two arrays: [0] = values in rasterArray with a Landslide
                                       [1] = values in rasterArrray without a Landslide
        """
        elementIndicesWithLs = np.where(inventoryArray == 1)
        elementIndicesWithoutLs = np.where(inventoryArray == 0)
        rasterValuesWithLs = rasterArray[elementIndicesWithLs]
        rasterValuesWithoutLs = rasterArray[elementIndicesWithoutLs]
        return (rasterValuesWithLs, rasterValuesWithoutLs)

    def calculatePointBiserial(
            self, rasterValuesWithLs, rasterValuesWithoutLs, rasterArray
    ) -> tuple:
        """
        Returns the point biserial correlation coefficient r_pb and all values used to calculate it.
               M_1 - M_0     n_1 * n_0
        r_pb = --------- * √(---------)
                  s_n           n^2
        M_1: Mean of rasterArray values with landslide
        M_0: Mean of rasterArray values without landslide
        s_n: Standard Deviation of rasterArray values
        n_1: Count of rasterArray elements with landslide
        n_0: Count of rasterArray elements without landslide
        n:   Total count of elements in rasterArray
        """
        M_1 = np.mean(rasterValuesWithLs)
        M_0 = np.mean(rasterValuesWithoutLs)
        s_n = np.std(rasterArray)
        n_1 = rasterValuesWithLs.size
        n_0 = rasterValuesWithoutLs.size
        n = rasterArray.size
        return (((M_1 - M_0) / s_n) * (np.sqrt(((n_1 * n_0) / n ** 2))), M_1, M_0, s_n, n_1, n_0)
