from ramp.core.core import User
User_list = []

RP = User("Rice Processing", 1)
User_list.append(RP)

# Rice dryer (small ventilated dryer, 0.5-2 t/day)
# Source: Kapur et al. (2012), PMC4571202; manufacturer specs
RP_dryer = RP.add_appliance(1, 2500, 1, 480, 0.2, 30, wd_we_type=0)
RP_dryer.windows([420, 1080], [0, 0], 0.2)

# Rice huller (mini-huller 150-200 kg/h, 2.2 kW)
# Source: Kapur et al. (2012), PMC4571202; Yifeng Agro specs
RP_huller = RP.add_appliance(1, 2000, 1, 300, 0.2, 30, wd_we_type=0)
RP_huller.windows([420, 1080], [0, 0], 0.2)

# Rice polisher (mini-polisher 150-200 kg/h)
# Source: RERIC Journal Thailand; manufacturer specs
RP_polisher = RP.add_appliance(1, 1500, 1, 300, 0.2, 30, wd_we_type=0)
RP_polisher.windows([420, 1080], [0, 0], 0.2)

# Sorter/grader (vibrating screen, 200-300 kg/h)
# Source: Kapur et al. (2012), PMC4571202
RP_sorter = RP.add_appliance(1, 1000, 1, 300, 0.2, 15, wd_we_type=0)
RP_sorter.windows([420, 1080], [0, 0], 0.2)

# Packaging machine (small semi-automatic)
# Source: manufacturer specs (Victor Rice Mill)
RP_packaging = RP.add_appliance(1, 400, 1, 180, 0.2, 10, wd_we_type=0)
RP_packaging.windows([420, 1080], [0, 0], 0.2)
