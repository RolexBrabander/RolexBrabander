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

# function to check if the child tag is new or the same as a previous child
def check_child_in_list_of_children(new_child, list) :
    for old_child in list :
        if new_child == old_child :
            return False
    return True

# true if the text contains more than only "banned characters"
def check_valid_text(text_string) :
    if text_string == None :
        return True
    banned_characters = {"\n", " ", "\t"} # general formatting or readability characters
    text_set          = set(text_string) # convert text_string to a set of characters

    # if there are more characters than just banned characters, return true
    if len(text_set - banned_characters) > 0 :
        return True
    else:
        return False

# function to convert the element tree to a dictionary
def single_node(node) :
    print(f"In node: {node.tag}")

    node_dict = {}
    node_list_of_children_tags = []

    if len(node.attrib) > 0 :
        node_attr_tag = node.tag + "_attributes"
        child_attr_data = {node_attr_tag : node.attrib}
        node_dict.update(child_attr_data)

    # rare, but sometimes parents have relevant text in addition to its own children
    isValidText = check_valid_text(node.text)
    if isValidText :
        node_dict.update({node.tag + "_text" : node.text})

    # scroll through sub_nodes
    for sub_node in node :
        isNewChild = check_child_in_list_of_children(sub_node.tag, node_list_of_children_tags)
        if isNewChild : # create list for the new child type
            node_list_of_children_tags.append(sub_node.tag)
            print(f"New unique child: {node_list_of_children_tags}")
            empty_list = []
            node_dict.update({sub_node.tag : empty_list})
        
        sub_node_dict = single_node(sub_node)
        node_dict[sub_node.tag].append(sub_node_dict)
        
    return node_dict

# function to clean up the converted dict
def clean_dict(node) :
    print (f"In {type(node)}: {node}")
    new_data = node

    # if data is null, simply return it
    if node == None :
        return new_data

    # if the node is a list of length 1, set the data to be the first index (no longer a list)
    if isinstance(node, list) and len(node) == 1 :
        new_data = node[0]
        print(f"New data: {new_data}, length: {len(new_data)}")

    # recursion, scroll through subnodes
    for sub_node in node :
        if isinstance(node, dict) :                        
            sub_node_tag = str(sub_node)
            new_sub_node = clean_dict(node[sub_node_tag])
            new_data.update({sub_node_tag : new_sub_node})

        elif isinstance(node, list) :
            sub_node_index = node.index(sub_node)
            node[sub_node_index] = clean_dict(sub_node)

    # if new data is a dict of length 1
    if isinstance(new_data, dict) and len(new_data) == 1 :
        sub_node_tag_text = str(list(new_data.keys())[0])
        tag_split_underscore = sub_node_tag_text.rsplit("_", 1)
        # sub_node_tag_text had an underscore, and right of the underscore was "text" remove a layer of dicts
        if len(tag_split_underscore) > 1 :
            if tag_split_underscore[1] == "text" :
                new_data = new_data[sub_node_tag_text]

    return new_data

output_file = get_output_file(input_file, ".json")
converted_dict = single_node(root)
clean_dict(converted_dict)
output_dict = {root.tag : converted_dict}

with open(output_file, "w") as out :
    json.dump(output_dict, out, indent=4)
