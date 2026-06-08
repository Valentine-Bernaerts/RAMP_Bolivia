from ramp.core.core import User
User_list = []


ICT = User("ICT", 1)
User_list.append(ICT)

ICT_TV = ICT.add_appliance(1,60,2,120,0.1,5, occasional_use = 0.5)
ICT_TV.windows([480,780],[840,1140],0.2)

ICT_radio = ICT.add_appliance(3,4,2,120,0.1,5, occasional_use = 0.5)
ICT_radio.windows([480,780],[840,1140],0.2)

ICT_DVD = ICT.add_appliance(1,8,2,120,0.1,5, occasional_use = 0.5)
ICT_DVD.windows([480,780],[840,1140],0.2)