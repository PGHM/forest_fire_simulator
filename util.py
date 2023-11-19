from osgeo import gdalnumeric
import numpy

# Precalculate an array for elevations from 0 to 250 meters by interpolating 
# the rest of the values linearly
def calculate_wind_speeds():
    wind_speeds = []
    
    step = (WIND_50 - WIND_0) / 50.0
    for i in range(0, 50):
        wind_speeds.append(WIND_0 + (i+1) * step)
    
    step = (WIND_100 - WIND_50) / 50.0
    for i in range(50, 100):
        wind_speeds.append(WIND_50 + (i+1) * step)
    
    step = (WIND_200 - WIND_100) / 100.0
    for i in range(100, 250):
        wind_speeds.append(WIND_100 + (i+1) * step)
   
    for i in range(0, 250):
        wind_speeds[i] = round(wind_speeds[i], 2)
    
    return wind_speeds

# Mean temperature and presipication at 07/2006
MEAN_TEMP = 16.5 # celcius
MEAN_PREC = 16 # mm

# value of burning pixel
BURNING_PIXEL = 1

# Array which tells with tuple (x, y) how much you move in x, y coordinates in each direction
# 701 from pixel P, for example direction 0 you move (0, -1). Directions are positive in down-right
# 6P2 direction
# 543
MOVE_TO_DIRECTION = [
    (0, -1),
    (1, -1),
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1),
]

# pixel values that are not suitable for new burning
UNELIGIBLE_TYPES = [BURNING_PIXEL, 7, 42]

# Width and height of the area
WIDTH = 307
HEIGHT = 409

# Wind speeds at different altitudes in meters per second
WIND_0 = 3.0 # estimate
WIND_50 = 4.5 
WIND_100 = 5.5
WIND_200 = 6.5

WIND_SPEEDS = calculate_wind_speeds()

# The percentage of speed of the wind that baseline forest 
# burns in the direction of the wind (see documentation for reasoning)
WIND_TO_FIRE_SPEED_PERCENTAGE = 0.11

# Relative burning speed rates to the baseline (Pine in mineral soil).
# More details in documentation about the reasoning behind the rates
BURNING_SPEED_RATE = {
    13 : 1.50,
    20 : 0.50,
    46 : 1.00,
    47 : 1.10,
    49 : 1.20,
    51 : 0.50,
    52 : 0.60,
    56 : 1.00,
    57 : 1.10,
    59 : 1.20,
    67 : 0.75,
    69 : 0.85,
    71 : 0.95,
    78 : 1.00, # baseline
    79 : 1.10,
    81 : 1.20,
    89 : 1.25,
    90 : 1.35,
    92 : 1.45,
    100 : 0.75,
    101 : 0.80,
    103 : 0.85,
    116 : 1.25,
    117 : 1.35,
    119 : 1.45,
    132 : 0.75,
}

# Precalculate array that tells how quickly the baseline 
# forest burns n steps from the direction of the wind
def calculate_wind_speed_coefficients():
    wind_speed_coefficients = []

    # if the direction is 0 steps away, the fire burns at the optimal speed in this direction
    wind_speed_coefficients.append(WIND_TO_FIRE_SPEED_PERCENTAGE)
    
    # if the direction is 1 steps (45 degrees) away, the fire burns at 60% of the speed of the wind coefficient
    wind_speed_coefficients.append(WIND_TO_FIRE_SPEED_PERCENTAGE * 0.6)
    
    # rest of the steps with same kind of logic
    wind_speed_coefficients.append(WIND_TO_FIRE_SPEED_PERCENTAGE * 0.35)
    wind_speed_coefficients.append(WIND_TO_FIRE_SPEED_PERCENTAGE * 0.25)
    wind_speed_coefficients.append(WIND_TO_FIRE_SPEED_PERCENTAGE * 0.15)
    return wind_speed_coefficients

# Validate that these coordinates are in the area
def validate_coordinates(coordinate_tuple):
    x = coordinate_tuple[0]
    y = coordinate_tuple[1]
    if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT:
        return True
    else:
        return False

def get_next_pixels(burn_dict, t):
    next_pixels = []
    for pixel, burn_time in burn_dict.iteritems():
        if burn_time <= t:
            next_pixels.append(pixel)
    return next_pixels

# marks the pixel burning in the forest
def mark_pixel_burning(forest, pixel):
    #print "Burning pixel: ", pixel
    forest[pixel[1]][pixel[0]] = BURNING_PIXEL

# returns list of tuples for eligible neighbours, as (direction from pixel, coordinates, land_type)
def get_eligible_neighbours(forest, pixel):
    eligible_neighbours = []
    for i in range(0, 8):
        move = MOVE_TO_DIRECTION[i]
        neighbour_coordinates = (pixel[0] + move[0], pixel[1] + move[1])
        if validate_coordinates(neighbour_coordinates):
            neighbour = forest[neighbour_coordinates[1], neighbour_coordinates[0]]
            if neighbour not in UNELIGIBLE_TYPES:
                eligible_neighbours.append((i, neighbour_coordinates, neighbour))
    return eligible_neighbours

# get wind speed for this pixel
def get_wind_speed(elevation, pixel):
    return WIND_SPEEDS[get_elevation(elevation, pixel)]

# get slope for this pixel, transform the percent value to fraction form
def get_slope(slope, pixel):
    return float(slope[pixel[1]][pixel[0]]) / 100.0

# get elevation for this pixel
def get_elevation(elevation, pixel):
    return elevation[pixel[1]][pixel[0]]

# calculate the effect the slope has on the speed. Check if we are going uphill
# or downhill. Uphill accelerates and downhill decelerates the spread.
def calculate_slope_coefficient(slope_value, elevation, source_pixel, target_pixel):
    source_elevation = get_elevation(elevation, source_pixel)
    target_elevation = get_elevation(elevation, target_pixel)

    if source_elevation < target_elevation:
        # going uphill
        return 1.00 + slope_value
    else:
        # going downhill
        return 1.00 - slope_value

# calculate the difference between directions
def calculate_direction_difference(direction1, direction2):
    difference = abs(direction1 - direction2)
    if difference <= 4:
        return difference
    else:
        return 8 - difference

def load_forest_colormap():
    colormap = {}
    colorfile = open('forest.tif.clr', 'r')
    for line in colorfile:
        splitted = line.split(' ')
        colormap[splitted[0]] = (splitted[1], splitted[2], splitted[3].strip())

    return colormap

# Pixels are the type of the terrain
def load_forest_map():
    return gdalnumeric.LoadFile('forest.tif')

# Load test map that has only one type of forest to study the wind coefficients
def load_test_map():
    return gdalnumeric.LoadFile('test.tif')

# Pixels are the rates in which the slope affects the speed of the fire
def load_slope_map():
    return gdalnumeric.LoadFile('slope.tif')

# Pixels are elevation in meters
def load_elevation_map():
    array = gdalnumeric.LoadFile('elevation.tif')
    for i in range(0, len(array)):
        for j in range(0, len(array[i])):
            array[i][j] = array[i][j] * 0.1
    return array

# draw output raster, use colormap to make the pixels colorful again!
def draw_color_tiff(array, colormap, filename):
    original = gdalnumeric.LoadFile('originals/forest.tif')
    for i in range(0, len(array)):
        for j in range(0, len(array[i])):
            value = array[i][j]
            color = colormap[str(value)]
            original[0][i][j] = numpy.uint8(color[0])
            original[1][i][j] = numpy.uint8(color[1])
            original[2][i][j] = numpy.uint8(color[2])

    write_obj = gdalnumeric.SaveArray(original, filename)

    # Flush cache many many times to actually get the picture out!
    write_obj.FlushCache()
    write_obj.FlushCache()
    write_obj.FlushCache()
    write_obj.FlushCache()
    write_obj.FlushCache()
