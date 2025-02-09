#!/bin/python3

import json
import sys

if len(sys.argv) != 2:
	out_file_path = "androiddir.bash"
else:
	out_file_path = sys.argv[1]

# 1. How to parse json file with c-style comments?
#   https://stackoverflow.com/questions/29959191/how-to-parse-json-file-with-c-style-comments
def GetJsonFromFile(filePath):
    contents = ""

    fh = open(filePath, encoding="utf-8")
    for line in fh:
        cleanedLine = line.split("//", 1)[0]
        if len(cleanedLine) > 0 and line.endswith("\n") and "\n" not in cleanedLine:
            cleanedLine += "\n"
        contents += cleanedLine
    fh.close

    while "/*" in contents:
        preComment, postComment = contents.split("/*", 1)
        contents = preComment + postComment.split("*/", 1)[1]

    return contents

# get config
config = json.loads(GetJsonFromFile('config.json'))
# print(json.dumps(config, indent=4))

# get project key-value keys and init key variable array
project_keys = []
for key in config["project_keys"]:
	project_keys.append(key)
	globals()["%ss" % (key)] = []

# get data
defaultPath = config["defaultPath"]
for project in config["projects"]:
	for key in project_keys:
		if key in project.keys():
			globals()["%ss" % (key)].append(project[key])
		else:
			globals()["%ss" % (key)].append(".")

# show data
print("defaultPath: " + defaultPath)
for key in project_keys:
	print(key + "s: " + str(globals()["%ss" % (key)]))

# get component key
component_keys = []
for component in config["components"]:
	component_keys.append(component["cmd"])

# generator file
anpp_config_start = "##### ANPP CONFIG START #####"
anpp_config_end = "##### ANPP CONFIG END #####"
anpp_custom_start = "##### ANPP CUSTOM START #####"
anpp_custom_end = "##### ANPP CUSTOM END #####"
anpp_component_start = "##### ANPP COMPONENT START #####"
anpp_component_end = "##### ANPP COMPONENT END #####"
anpp_command_start = "##### ANPP COMMAND START #####"
anpp_command_end = "##### ANPP COMMAND END #####"
anpp_alias_start = "##### ANPP ALIAS START #####"
anpp_alias_end = "##### ANPP ALIAS END #####"
anpp_template_skip_line = False
with open(out_file_path, 'w', encoding = 'utf-8') as f_out:
	with open("androiddir.bash.template", 'r', encoding = 'utf-8') as f_in:
		for line in f_in:
			if line.strip() == anpp_config_start:
				anpp_template_skip_line = True
				f_out.write(line)

				f_out.write("# default Workspace dir, all projects are here\n")
				f_out.write("export defaultPath=" + defaultPath + "\n")
				f_out.write("\n")

				for key in project_keys:
					f_out.write("# " + key + " dir info \n")
					f_out.write(key + "s=(\n")
					for value_data in globals()["%ss" % (key)]:
						f_out.write("    " + value_data + "\n")
					f_out.write(")\n")
					f_out.write("\n")

			elif line.strip() == anpp_config_end:
				anpp_template_skip_line = False
			elif line.strip() == anpp_custom_start:
				anpp_template_skip_line = True
				f_out.write(line)

				with open("custom.sh", 'r', encoding = 'utf-8') as f_custom:
					for line in f_custom:
						f_out.write(line)

			elif line.strip() == anpp_custom_end:
				anpp_template_skip_line = False
			elif line.strip() == anpp_component_start:
				anpp_template_skip_line = True
				f_out.write(line)

				f_out.write("# components for shell alias cmd\n")
				f_out.write("components=(\n")
				for key in component_keys:
					f_out.write("    " + key+ "\n")
				f_out.write(")\n")
				f_out.write("\n")

			elif line.strip() == anpp_component_end:
				anpp_template_skip_line = False
			elif line.strip() == anpp_command_start:
				anpp_template_skip_line = True
				f_out.write(line)

				# generate shell variable
				custom_args = "$1 ${defaultPath} "
				for key in project_keys:
					f_out.write("                " + key + "=${" + key + "s[i]}\n")
					custom_args += "${" + key + "} "

				# generate header for if
				f_out.write("\n")
				f_out.write("                if [ $1 == \"None\" ]; then\n")
				f_out.write("                    cd .\n")
				
				# generate if body for cmd
				for key in component_keys:
					f_out.write("                elif [ $1 == \"" + key + "\" ]; then\n")
					cmd_path = ""
					key_index = component_keys.index(key)
					for conbine in config["components"][key_index]["combine"]:
						cmd_path += "${" + conbine +"}/"
					if cmd_path.endswith("/"):
						cmd_path = cmd_path[:-1]
					f_out.write("                    cd " + cmd_path + "\n")

				f_out.write("                else\n")

				# generate else for if
				if custom_args.endswith(" "):
					custom_args = custom_args[:-1]
				f_out.write("                    project_product_custom " + custom_args + "\n")
				f_out.write("                    returnData=$?\n")
				f_out.write("                    if [ ${returnData} -ne 0 ]; then\n")
				f_out.write("                        echo \"error: $1 returned with value: ${returnData}\"\n")
				f_out.write("                        return\n")
				f_out.write("                    fi\n")
				f_out.write("                fi \n")

			elif line.strip() == anpp_command_end:
				anpp_template_skip_line = False
			elif line.strip() == anpp_alias_start:
				anpp_template_skip_line = True
				f_out.write(line)

				f_out.write("alias anpp=\"project_product\"           # just for project_product function alias\n")
				f_out.write("alias anppc=\"project_product_custom\"   # just for project_product_custom function alias")
				f_out.write("# custom shell alias cmds\n")
				for alias in config["alias"]:
					alias_cmd = "alias " + alias["cmd"] + "=\"" + alias["shell"] + "\"\n"
					f_out.write(alias_cmd)

			elif line.strip() == anpp_alias_end:
				anpp_template_skip_line = False

			if not anpp_template_skip_line:
				f_out.write(line)
