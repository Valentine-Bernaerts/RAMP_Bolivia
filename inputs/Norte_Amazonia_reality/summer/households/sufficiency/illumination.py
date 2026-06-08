from ramp.core.core import User

User_list = []

HI = User("household illumination", 1)
User_list.append(HI)

# occasional_use=1.0: illumination is universal for electrified households
HI_indoor_bulb = HI.add_appliance(4, 7, 2, 270, 0.2, 10, occasional_use=1.0)
HI_indoor_bulb.windows([300, 480], [950, 1440], 0.35)

HI_outdoor_bulb = HI.add_appliance(2, 14, 1, 180, 0.2, 10, occasional_use=1.0)
HI_outdoor_bulb.windows([1140, 1380], [0, 0], 0.35)
