import mahotas as mh
import numpy as np
import math
from scipy.ndimage.interpolation import rotate as scipy_rotate
from collections import OrderedDict
from colicoords.config import cfg


# https://stackoverflow.com/questions/26598109/preserve-custom-attributes-when-pickling-subclass-of-numpy-array

class BinaryImage(np.ndarray):
    """ Binary image data class

    This class is a subclass of np.ndarray and has therefore all its normal functionality.

     Attributes:
         name (:obj:`str`): Name string to identify the data element
         metadata (:obj:`dict`): Optional dict for metadata, load/save not implemented
     """

    def __new__(cls, input_array, name=None, metadata=None):
        if input_array is None:
            return None

        obj = np.asarray(input_array).view(cls)
        obj.name = name
        obj.metadata = metadata
        obj.dclass = 'binary'
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.name = getattr(obj, 'name', None)
        self.metadata = getattr(obj, 'metadata', None)
        self.dclass = getattr(obj, 'dclass', 'binary')

    def __reduce__(self):
        # Get the parent's __reduce__ tuple
        pickled_state = super(BinaryImage, self).__reduce__()
        # Create our own tuple to pass to __setstate__
        new_state = pickled_state[2] + (self.name, self.metadata, self.dclass)
        # Return a tuple that replaces the parent's __setstate__ tuple with our own
        return pickled_state[0], pickled_state[1], new_state

    def __setstate__(self, state):
        self.name, self.metadata, self.dclass = state[-3:]
        super(BinaryImage, self).__setstate__(state[0:-3])


    @property
    def orientation(self):
        """float: The main image axis orientation in degrees"""
        return _calc_orientation(self)


class BrightFieldImage(np.ndarray):
    """ Brightfield image data class

    This class is a subclass of np.ndarray and has therefore all its normal functionality.

     Attributes:
         name (:obj:`str`): Name string to identify the data element
         metadata (:obj:`dict`): Optional dict for metadata, load/save not implemented
     """

    def __new__(cls, input_array, name=None, metadata=None):
        if input_array is None:
            return None
        obj = np.asarray(input_array).view(cls)
        obj.name = name
        obj.metadata = metadata
        obj.dclass = 'brightfield'
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.name = getattr(obj, 'name', None)
        self.metadata = getattr(obj, 'metadata', None)
        self.dclass = getattr(obj, 'dclass', 'brightfield')

    def __reduce__(self):
        # Get the parent's __reduce__ tuple
        pickled_state = super(BrightFieldImage, self).__reduce__()
        # Create our own tuple to pass to __setstate__
        new_state = pickled_state[2] + (self.name, self.metadata, self.dclass)
        # Return a tuple that replaces the parent's __setstate__ tuple with our own
        return (pickled_state[0], pickled_state[1], new_state)

    def __setstate__(self, state):
        self.name, self.metadata, self.dclass = state[-3:]
        super(BrightFieldImage, self).__setstate__(state[0:-3])

    @property
    def orientation(self):
        """float: The main image axis orientation in degrees"""
        return _calc_orientation(self)


class FluorescenceImage(np.ndarray):
    """ Fluorescence image data class

    This class is a subclass of np.ndarray and has therefore all its normal functionality. The array can be 2D or 3D.

     Attributes:
         name (:obj:`str`): Name string to identify the data element
         metadata (:obj:`dict`): Optional dict for metadata, load/save not implemented
     """

    def __new__(cls, input_array, name=None, metadata=None):
        if input_array is None:
            return None
        obj = np.asarray(input_array).view(cls)
        obj.name = name
        obj.metadata = metadata
        obj.dclass = 'fluorescence'
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.name = getattr(obj, 'name', None)
        self.metadata = getattr(obj, 'metadata', None)
        self.dclass = getattr(obj, 'dclass', 'fluorescence')

    def __reduce__(self):
        # Get the parent's __reduce__ tuple
        pickled_state = super(FluorescenceImage, self).__reduce__()
        # Create our own tuple to pass to __setstate__
        new_state = pickled_state[2] + (self.name, self.metadata, self.dclass)
        # Return a tuple that replaces the parent's __setstate__ tuple with our own
        return (pickled_state[0], pickled_state[1], new_state)

    def __setstate__(self, state):
        self.name, self.metadata, self.dclass = state[-3:]
        super(FluorescenceImage, self).__setstate__(state[0:-3])

    @property
    def orientation(self):
        """float: The main image axis orientation in degrees"""
        return _calc_orientation(self)


class STORMTable(np.ndarray):
    """ STORM table data class

    This class is a subclass of np.ndarray and has therefore all its normal functionality.

     Attributes:
         name (:obj:`str`): Name string to identify the data element
         metadata (:obj:`dict`): Optional dict for metadata, load/save not implemented
     """

    def __new__(cls, input_array, name=None, metadata=None):

        if input_array is None:
            return None
        obj = np.asarray(input_array).view(cls)
        obj.name = name
        obj.metadata = metadata
        obj.dclass = 'storm'
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.name = getattr(obj, 'name', None)
        self.metadata = getattr(obj, 'metadata', None)
        self.dclass = getattr(obj, 'dclass', 'storm')

    def __reduce__(self):
        # Get the parent's __reduce__ tuple
        pickled_state = super(STORMTable, self).__reduce__()
        # Create our own tuple to pass to __setstate__
        new_state = pickled_state[2] + (self.name, self.metadata, self.dclass)
        # Return a tuple that replaces the parent's __setstate__ tuple with our own
        return (pickled_state[0], pickled_state[1], new_state)

    def __setstate__(self, state):
        self.name, self.metadata, self.dclass = state[-3:]
        super(STORMTable, self).__setstate__(state[0:-3])

    @property
    def image(self):
        raise NotImplementedError()
        #
        # assert 'storm_img' not in self.data_dict
        # img = self._get_storm_img(data)
        # name = 'storm_img' if name is 'storm' else name + '_img'
        # self.storm_img = STORMImage(img, name=name, metadata=metadata)
        # self.data_dict['storm_img'] = self.storm_img
        # self.name_dict[name] = self.storm_img


#todo is this even used?
class STORMImage(np.ndarray):
    def __new__(cls, input_array, name=None, metadata=None):
        """STORM recontructed image
        
        Args:
            input_array: STORM data array 
        """
        if input_array is None:
            return None

        obj = np.asarray(input_array).view(cls)
        obj.name = name
        obj.metadata = metadata
        obj.dclass = 'storm_img'
        return obj

    @property
    def orientation(self):
        return _calc_orientation(self)


#todo this shoud be a dict? (use open microscopy format?) (XML)
class MetaData(dict):
    pass


class Data(object):
    """ Main class to hold all data and perform transformations

    The data class is designed to combine and organize all different channels (brightfield, binary, fluorescence, storm)
    into one object. The class also provides basic functionality to manipulate the data, such as rotation and slicing.


    Attributes:
        data_dict (:obj:`dict`): Dictionary with all data elements by their name
        flu_dict (:obj:`dict`): Subset of `data_dict` with all Fluorescence data elements
        storm_dict (:obj:`dict`): Subset of `data_dict` with all STORM data elements

        binary_img (:class:`BinaryImage`): Convenience attribute which refers to the unique BinaryImage data element
        brightfield_img (:class:`BrightFieldImage`): Convenience attribute which refers tot he unique BrightFieldImage
            data element
    """

    def __init__(self):
        self.data_dict = OrderedDict() #todo ordereddict?
        self.flu_dict = OrderedDict()  #needed or new initialized class doesnt have empty dicts!!!oneone
        self.storm_dict = {}

        self.binary_img = None
        self.brightfield_img = None

        self.shape = None
        self.ndim = None

        self._idx = 0

    def add_data(self, data, dclass, name=None, metadata=None):
        """ Add data to the :class:`Data` to form a new data element

        Args:
            data: Input data, either np.ndarray with ndim 2 or 3 (images / movies) or numpy structured array for STORM data
            dclass: hmmm #todo change to enum or not?
            name (:obj:`str`): The data element's name
            metadata: (:obj:`dict`): Optional associated metadata (load/save metadata currently not supported)
        """

        if name in ['', u'', r'', None]:
            name = dclass
        else:
            name = str(name)

        if name in self.names:
            raise ValueError('Data element name {} is already used'.format(name))

        if dclass == 'binary':
            if self.binary_img is not None:
                raise ValueError('Binary image has to be unique and is already given')
            if not np.issubdtype(data.dtype, np.integer):
                raise TypeError('Invalid data type {} for data class binary'.format(data.dtype))

            self._check_shape(data.shape, data.ndim)
            self.binary_img = BinaryImage(data, name=name, metadata=metadata)
            self.data_dict[name] = self.binary_img
        elif dclass == 'brightfield':
            self._check_shape(data.shape, data.ndim)
            b = BrightFieldImage(data, name=name, metadata=metadata)
            setattr(self, 'bf_' + name, b)
            #todo brightfiels in a seperate dictionary?
            self.data_dict[name] = b
        elif dclass == 'fluorescence':
            assert name
            assert name not in self.flu_dict
            self._check_shape(data.shape, data.ndim)
            f = FluorescenceImage(data, name=name, metadata=metadata)
            setattr(self, 'flu_' + name, f)
            self.flu_dict[name] = f
        elif dclass == 'storm':
            assert name
            assert name not in self.storm_dict
            for field in ['x', 'y', 'frame']:
                assert field in data.dtype.names

            s = STORMTable(data, name=name, metadata=metadata)
            self.storm_dict[name] = s
            setattr(self, 'storm_' + name, s)

        else:
            raise ValueError('Invalid data class {}'.format(dclass))

        self.data_dict.update(self.flu_dict)
        self.data_dict.update(self.storm_dict)

    def prune(self, data_name):
        #todo test and docstring
        storm = self.data_dict.pop(data_name)
        self.storm_dict.pop(data_name)
        assert isinstance(storm, STORMTable)

        xmax, ymax = self.shape[1], self.shape[0]
        bools = (storm['x'] < 0) + (storm['x'] > xmax) + (storm['y'] < 0) + (storm['y'] > ymax)
        storm_out = storm[bools].copy()

        self.add_data(storm_out, storm.dclass, name=data_name)

    def copy(self):
        data = Data()
        for v in self.data_dict.values():
            data.add_data(np.copy(v), v.dclass, name=v.name, metadata=v.metadata)
        return data

    @property
    def dclasses(self):
        return np.unique([d.dclass for d in self.data_dict.values()])

    @property
    def names(self):
        return [d.name for d in self.data_dict.values()]

    def rotate(self, theta):
        data = Data()
        for v in self.data_dict.values():
            if v.dclass == 'storm':
                rotated = _rotate_storm(v, -theta, shape=self.shape)
            else:

                rotated = scipy_rotate(v, -theta, mode='nearest', axes=(-2, -1)) #todo check dis

            data.add_data(rotated, v.dclass, name=v.name, metadata=v.metadata)
        return data

    def transform(self, x, y, src='cart', tgt='mpl'):
        #todo docstring and unify with function on coords
        raise DeprecationWarning()
        if src == 'cart':
            xt1 = x
            yt1 = y
        elif src == 'mpl':
            xt1 = x
            yt1 = self.shape[0] - y - 0.5
        elif src == 'matrix':
            yt1 = self.shape[0] - x - 0.5
            xt1 = y + 0.5
        else:
            raise ValueError("Invalid source coordinates")

        if tgt == 'cart':
            xt2 = xt1
            yt2 = yt1
        elif tgt == 'mpl':
            xt2 = xt1
            yt2 = self.shape[0] - yt1 - 0.5
        elif tgt == 'matrix':
            xt2 = self.shape[0] - yt1 - 0.5
            yt2 = xt1 - 0.5
        else:
            raise ValueError("Invalid target coordinates")
        return xt2, yt2

    def _check_shape(self, shape, ndim):
        if self.shape:
            if not ((shape == self.shape) and (ndim == self.ndim)):
                if not ((ndim == self.ndim + 1) and (shape[1:] == self.shape)):
                    raise ValueError("Invalid shape")
            # try:
            #     assert shape == self.shape
            #     assert ndim == self.ndim
            # except AssertionError:
            #     assert ndim == self.ndim + 1
            #     assert shape[1:] == self.shape

        else:
            self.shape = shape
            self.ndim = ndim

    def __len__(self):
        if not hasattr(self, 'ndim'):
            return 0
        elif self.ndim == 3:
            return self.shape[0]
        elif self.ndim == 2:
            return 1
        else:
            raise ValueError

    def __iter__(self):
        self._idx = 0
        return self

    def __next__(self):
        if not hasattr(self, 'ndim'):
            raise StopIteration
        if self.ndim == 2:
            if self._idx == 0:
                self._idx += 1
                return self
            else:
                self._idx = 0
                raise StopIteration

#        data = Data()
        if self._idx >= len(self):
            self._idx = 0
            raise StopIteration
        else:
            data = self[self._idx]

            self._idx += 1
            return data

    def __getitem__(self, key):
        #todo len (key) means 2d slicing!
        data = Data()
        for v in self.data_dict.values():

            if v.dclass == 'storm':
                #todo needs testing

                if type(key) == int:
                    #Select the appropriate frames, STORM frame numbers start counting at 1
                    xmin = 0
                    ymin = 0

                    b_z = v['frame'] == key + 1
                    b_xy = True

                elif len(key) == 3:
                    #3d slicing, slices the frames? #todo 3d slicing by frame!
                    raise NotImplementedError()

                elif len(key) == 2:
                    ymin, ymax, ystep = key[0].start, key[0].stop, key[0].step
                    xmin, xmax, xstep = key[1].start, key[1].stop, key[1].step

                    xmin = xmin if xmin else 0
                    ymin = ymin if ymin else 0
                    xmax = xmax if xmax else self.shape[1]
                    ymax = ymax if ymax else self.shape[0]

                    if ystep is not None or xstep is not None:
                        raise ValueError('Cannot specify slice steps for slicing images in x and y dimenions')

                    #Create boolean array to mask entries withing the chosen range
                    b_xy = (v['x'] > xmin) * (v['x'] < xmax) * (v['y'] > ymin) * (v['y'] < ymax)
                    b_z = True

                # Choose selected data and copy, rezero x and y
                b_overall = b_z * b_xy

                table_out = v[b_overall].copy()
                table_out['x'] -= xmin
                table_out['y'] -= ymin

                data.add_data(table_out, v.dclass, name=v.name, metadata=v.metadata)

            else:
                key = (slice(None), *key) if v.ndim == 3 and type(key) == tuple else key #todo this needs maaaasive testing
                data.add_data(v[key], v.dclass, name=v.name, metadata=v.metadata)
        return data

    next = __next__


def _rotate_storm(storm_data, theta, shape=None):
    theta *= np.pi / 180  # to radians
    x = storm_data['x'].copy()
    y = storm_data['y'].copy()

    if shape:
        ymax = shape[0]
        xmax = shape[1]

        ynew = np.abs(xmax * np.sin(-theta)) + np.abs(ymax * np.cos(-theta))
        xnew = np.abs(xmax * np.cos(-theta)) + np.abs(ymax * np.sin(-theta))

    else:
        xmax = int(storm_data['x'].max()) + 2
        ymax = int(storm_data['y'].max()) + 2
        ynew = 0
        xnew = 0

    x -= xmax / 2
    y -= ymax / 2

    xr = x * np.cos(theta) + y * np.sin(theta)
    yr = y * np.cos(theta) - x * np.sin(theta)

    xr += xnew / 2
    yr += ynew / 2

    storm_out = np.copy(storm_data)
    storm_out['x'] = xr
    storm_out['y'] = yr

    return storm_out


def _calc_orientation(img):
    com = mh.center_of_mass(img)

    mu00 = mh.moments(img, 0, 0, com)
    mu11 = mh.moments(img, 1, 1, com)
    mu20 = mh.moments(img, 2, 0, com)
    mu02 = mh.moments(img, 0, 2, com)

    mup_20 = mu20 / mu00
    mup_02 = mu02 / mu00
    mup_11 = mu11 / mu00

    theta_rad = 0.5 * math.atan(2 * mup_11 / (mup_20 - mup_02))  # todo math -> numpy
    theta = theta_rad * (180 / math.pi)
    if (mup_20 - mup_02) > 0:
        theta += 90

    return theta
