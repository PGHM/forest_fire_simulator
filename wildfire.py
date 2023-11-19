import util
import subprocess

# 701 Wind directions, P = pixel
# 6P2
# 543
WIND_DIRECTION = 0
BURNING_RATES = util.BURNING_SPEED_RATE

INITIAL_POINT = (200, 300)
CELL_SIZE = 25
WIND_SPEED_EFFECT_COEFFICIENTS = util.calculate_wind_speed_coefficients()

#forest = util.load_test_map()
forest = util.load_forest_map()
slope = util.load_slope_map()
elevation = util.load_elevation_map()

# seconds since point zero
t = 0 

# has all the pixel that is about to be burning as key and 
# the the time from t=0 when it is about to burn
burn_dict = {}

# add the initial pixel and start the loop
burn_dict[INITIAL_POINT] = 1
filenames = []

# check if there are any pixels that are about to burn
while len(burn_dict) > 0:
    if t % 500 == 0:
        filename = "output_{0}_{1}_{2}_{3}.tif".format(t, WIND_DIRECTION, INITIAL_POINT[0], INITIAL_POINT[1])
        filenames.append(filename)
        util.draw_color_tiff(forest, util.load_forest_colormap(), filename) 
    next_pixels = util.get_next_pixels(burn_dict, t)
   
    # go through all the pixels that start burning at this second
    for pixel in next_pixels:
        del burn_dict[pixel]
        util.mark_pixel_burning(forest, pixel)
        neighbours = util.get_eligible_neighbours(forest, pixel)
        wind_speed = util.get_wind_speed(elevation, pixel)
       
        # for each eligible neighbour calculate the time it takes the fire to reach that cell
        for neighbour in neighbours:
            slope_coefficient = 1.00
            slope_value = util.get_slope(slope, neighbour[1])
            if slope_value > 0:
                slope_coefficient = util.calculate_slope_coefficient(slope_value, elevation, pixel, neighbour[1])
            
            distance_to_wind_direction = util.calculate_direction_difference(WIND_DIRECTION, neighbour[0])
            wind_speed_coefficient = WIND_SPEED_EFFECT_COEFFICIENTS[distance_to_wind_direction]
            speed = wind_speed * wind_speed_coefficient * BURNING_RATES[neighbour[2]] * slope_coefficient
            time_to_reach_cell = int(CELL_SIZE / speed)
            
            # check if this time is earlier or later then possible previous time for this cell
            if neighbour[1] in burn_dict and burn_dict[neighbour[1]] <= t + time_to_reach_cell:
                pass
            else:
                burn_dict[neighbour[1]] = t + time_to_reach_cell
            #print neighbour[0], wind_speed_coefficient, BURNING_RATES[neighbour[2]], speed,  time_to_reach_cell

    # increase the simulation time by one second
    t = t + 1

# make an animated gif from the pictures
filename = "animation_{0}_{1}_{2}.gif".format(WIND_DIRECTION, INITIAL_POINT[0], INITIAL_POINT[1])
args = ['convert', '-delay', '100', '-loop', '0']
args.extend(filenames)
args.append(filename)
subprocess.call(args)

# remove the individual pictures
args = ['rm']
args.extend(filenames)
subprocess.call(args)
