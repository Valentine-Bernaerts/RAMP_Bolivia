from ramp.core.core import User
User_list = []


IL = User("Illumination", 1)
User_list.append(IL)


IL_indoor_bulb = IL.add_appliance(6,7,2,120,0.25,30)
IL_indoor_bulb.windows([480,780],[840,1140],0.35)

IL_outdoor_bulb = IL.add_appliance(1,13,1,60,0.2,10)
IL_outdoor_bulb.windows([960,1080],[0,0],0.35)
