# Forest fire simulator

As part of a group project about forest fires and reforestation after a forest fire I was tasked to do "simple forest fire simulator". Pretty soon after starting to do research about the factors that go into making such simulator I was sucked in heavily and ended up doing a lot more than was needed to pass the project work. When we got the feedback about the project it was mentioned that similar approach was used in real simulations at the time.

Still 9 years later I'm pretty proud of the end result. Even though I might have evolved as a programmer during this time the code still feels very simple and well documented to me after all this time.

## Documentation

[The original documentation](/documentation.txt) that was returned as part of the project work describes the research done, factors that affect spreading of a forest fire and factors that could not be taken into account due to data not being available or not being able to find sources to back up information. It also lists the sources used and has some general information about forest fires.

## Running the code

Sadly I cannot remember the how the code was run in 2014 and I have not ran it since. I think it was written against Python version 2.7 and had some dependencies for reading the data (numpy) and creating the animated map. I have no intention ever running the code again because I have the rendered examples available, but you are welcome to try.

## Rendered example simulations

[The rendered example simulations](/rendered_example_simulations) show the spread of fire with one frame in the animation being 500 seconds. The filenames indicate the wind direction and the starting point of the fire coordinates within the map. The wind direction is coded so that 0 indicates north, 1 north-east, 2 east and so on.

Some simulations are done on a homogenous test map with no elevation and some are done on the real map. The test map allowed me to inspect how the shape of the fire in the simulation looks and compare it to the real recorded shapes of forest fires.

The real map is from Virrat area. It was selected because it has varying land and forest types, varying elevation and some water areas.
