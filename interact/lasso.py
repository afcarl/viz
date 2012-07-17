"""
Use a lasso to select a set of points and get the indices of the selected
points.  A callback is used to change the color of the selected points

TODO:

 * LassoBrowser and PointBrowser should be composable. Currently, they don't
   communicate.

    - Common code for dealing with pandas (e.g. the parallel idxs and point
      array); plot/axes updating; callback

    - PointBrowser only supports selecting one point. Why not generalize to
      shift-click many points this makes it much more like lasso.

"""
from matplotlib.widgets import Lasso
from matplotlib.nxutils import points_inside_poly
from matplotlib.collections import RegularPolyCollection
from matplotlib.colors import colorConverter
from numpy import nonzero, array

to_rgba = colorConverter.to_rgba

try:
    from debug import ip
except ImportError:
    pass


class LassoBrowser(object):

    def __init__(self, ax, df, xcol='x', ycol='y'):
        self.df = df
        self.ax = ax
        self.canvas = ax.figure.canvas
        self.lasso_lock = False             # indicates if another widget event has priority
        self.idxs = array(list(self.df.T))  # look up parallel with point indices
        self.xys = df[[xcol, ycol]].values
        self.collection = RegularPolyCollection(numsides=ax.figure.dpi,
                                                rotation=6,
                                                sizes=(100,),
                                                facecolors = [to_rgba('green', alpha=0.0)]*len(self.xys),
                                                linewidths = 0,
                                                offsets = self.xys,
                                                transOffset = ax.transData)
        ax.add_collection(self.collection)

        self.canvas.mpl_connect('button_press_event', self.onpress)
        self.canvas.mpl_connect('button_release_event', self.onrelease)
        self.selected = []
        self.lasso = None

    def lasso_callback(self, verts):
        [selected] = nonzero(points_inside_poly(self.xys, verts))
        # change face colors inplace
        facecolors = self.collection.get_facecolors()
        facecolors[:] = to_rgba('green', alpha=0.0)
        facecolors[selected] = to_rgba('yellow', alpha=0.6)

        # convert from point indices to dataframe indices
        idx = self.idxs[selected]
        print self.df.ix[idx]      # show selected rows of dataframe

        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)
        self.selected = selected

    def onpress(self, event):
        if self.canvas.widgetlock.locked():
            return
        if event.inaxes is None:
            return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.lasso_callback)
        self.canvas.widgetlock(self.lasso)  # acquire lock on lasso widget
        self.lasso_lock = True              # used when we release

    def onrelease(self, event):
        'on release we reset the press data'
        # test whether the widgetlock was initiated by the lasso
        if self.lasso_lock:
            self.canvas.widgetlock.release(self.lasso)
            self.lasso_lock = False


def example():
    import matplotlib.pyplot as pl
#    pl.ioff()
    pl.ion()

    import pandas
    from numpy.random import uniform

    n = 25
    m = pandas.DataFrame({
            'x': uniform(-1, 1, size=n),
            'y': uniform(-1, 1, size=n),
            'size': uniform(3, 10, size=n) ** 2,
            'color': uniform(0, 1, size=n),
    })

    # test using a custom index
    m['silly_index'] = ['%sth' % x for x in range(n)]
    m.set_index('silly_index', drop=True, inplace=True, verify_integrity=True)

    print m

    ax = pl.subplot(111)
    b = LassoBrowser(ax, m)
    print b.idxs

    plt = pl.scatter(m['x'], m['y'])

    #from viz.interact.pointbrowser import PointBrowser
    #pb = PointBrowser(m, plot=plt)

    pl.show()

    ip()

if __name__ == '__main__':
    example()
