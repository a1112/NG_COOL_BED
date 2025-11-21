name_list=["steel","t_car","d_car"]
color_list=[
    255
    ,
    0
    ,
    0
    ]


def name_to_id(name):
    return name_list.index(name)

def id_to_name(id_):
    return name_list[id_]

def name_to_color(name):
    # print(fr"name_to_color = {color_list[name_list.index(name)]}")
    return color_list[name_list.index(name)]

def name_is_steel(name):
    return name=="steel"