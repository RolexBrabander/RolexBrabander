import xml.etree.ElementTree as ET
import json


input_file  = "conversion_input/covid.xml"
tree = ET.parse(input_file)
root = tree.getroot() 

output_directory = "conversion_output/"

def get_output_file(input, file_extension) :
    no_ext = input.rsplit(".", 1)           # remove old file extension
    filename = no_ext[0].rsplit("/", 1)     # isolate filename from directory
    output = output_directory + filename[1] + "_converted" + file_extension
    return output

def check_child_in_list_of_children(new_child, list) :
    for old_child in list :
        if new_child == old_child :
            return False
    return True
    

def get_node_struct(parent) :
    list_of_children_tags = [] # list identifying unique children tags
    parent_dict = {}
    attributes = parent.attrib

    if len(attributes) > 0 :
        parent_dict.update({"attributes" : attributes})

    for child in parent :
        if len(child) <= 1 :
            child_data = {child.tag : child.text}
            parent_dict.update(child_data)
            if len(child.attrib) > 0 :
                child_attr_tag = child.tag + "_attr"
                child_attr_data = {child_attr_tag : child.attrib}
                parent_dict.update(child_attr_data)
            
        else:
            isNewChild = check_child_in_list_of_children(child.tag, list_of_children_tags)
            if isNewChild :
                list_of_children_tags.append(child.tag)
                print(f"New unique child: {list_of_children_tags}")
                empty_list = []
                parent_dict.update({child.tag : empty_list})
            
            child_list = parent_dict[child.tag]
            child_dict = get_node_struct(child)     # recursion for children
            child_data = child_dict[child.tag]      # removes the tag, as that is already recorded for the list
            child_list.append(child_data)
            parent_dict.update({child.tag : child_list})



    return {parent.tag : parent_dict}

output_file = get_output_file(input_file, ".json")
print(output_file)
dict = get_node_struct(root)

new_dict = json.dumps(dict, indent=4)

with open(output_file, "w") as out :
    json.dump(dict, out, indent=4)





''' Old: 
for child in root :
    nr_items = len(child)
    local_dict = {}
    child_type_list = 

    for id in range(nr_items) :
        new_data = {child[id].tag : child[id].text}
        local_dict.update(new_data)

    other_list.append(local_dict)

    dict.update({child.tag : other_list})

print(dict)
'''
