# GOST - Command Line Interface (CLI)

[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)
![Language: Python3](https://img.shields.io/badge/language-python3-blue.svg)

![Logo](images/example.png)


## Getting Started
*GOST-CLI* is a tool for interacting via command-line with a GOST
server

### Install
GOST-CLI requires Python 3 or greater (it was tested on Python 3.7 so it is suggested to install at least that version).

#### Clone the repository
```
git clone https://git.pertforge.ismb.it/Students-Projects/gost-cli.git
```


### How to use GOST-CLI
```

usage: interface.py [-h] [-f FILE] [-t OGC] [-m MODE] [-d] [-i]
                    [-p [PATCH [PATCH ...]]] [-s [SELECT [SELECT ...]]]
                    [--show [SHOW [SHOW ...]]] [-G GOSTADDRESS]
                    [--pingconnection] [-g] [--exit] [--interactive]
                    [--post [POST [POST ...]]]
                    [--create [CREATE [CREATE ...]]]
                    [identifier [identifier ...]]

Process user-defined GOST operations

positional arguments:
  identifier            ID or Name of one or more items to process, or '$'
                        followed by the name of a file with a list of them or
                        'all' for all the items of chosen type

optional arguments:
  --create [CREATE [CREATE ...]]
                        Creates n items of type t in created_files/<type>,
                        or in the file defined with 'file <filename>
                        you can define field values for created records
                        otherwise default value will be used
                        (ex: --create num 2 description new_description --type Sensors)
                        
  -d, --delete          delete the items chosen with get or selected
                        giving id or name: 
                        example:
                         --get 15 -t Sensors --delete
                          15 16 -t Sensors --delete  
  --execute             execute a of commands, this command
                        requires the absolute file path inside ""
                        example:
                         --exec "absolute_filepath"
                         --exec "absolute_filepath_1" "absolute_filepath_2"
  
  --exit                exits from the program when you are in an interactive session
  
  -g, --get             get the items of the currently selected ogc type.If
                        one or more item identifiers or names are definited those items
                        will be selected, otherwise all the items of the currently selected 
                        type if no id or name will be chosen. The query results are
                        stored for successive operations like delete or patch
  
  -G GOSTADDRESS, --GOSTaddress GOSTADDRESS, --address GOSTADDRESS
                        sets a new address (IP and port) for GOST
  
  -h, --help            show this help message and exit
  
  -i, --info            shows the current GOST address and operation mode
  
  --interactive         starts an interactive session, accepting new commands until the --exit 
                        command is given to return to the shell
                        
  -m MODE, --mode MODE  Select an alternative mode of operation. Currently
                        available modes: 
                         - default
  
  -p [PATCH [PATCH ...]], --patch [PATCH [PATCH ...]]
                        patch the choosen item FIELD with selected VALUE,usable
                        with multiple values at once 
                        examples: 
                        15 -t Sensors --p id <newId> name <newName>
                        --p description <newDescription> 
                          
  --post [POST [POST ...]]
                        posts records from user defined file/s to currently
                        selected OGC types(
                        examples:
                        --post <file_name> -t <type> 
                        --post <file_name_1> <file_name_2> -t <type>
                        
  --pingconnection, --connectiontest, --conntest
                        sends a ping to test the connection and shows the output
                        
  -s [SELECT [SELECT ...]], --select [SELECT [SELECT ...]]
                        selection of the items to process,
                        before any further operation like delete or
                        patch. Accepts python-like boolean expressions comparing
                        fields value, with ==, !=, <, >, <=, >=, <>, 
                        lt, gt, lteq, gteq, diff operators
                        example: 
                         --select @iot.id == <definedId> and name <definedName>)
                         --select @iot.id <definedId> and (name == <definedName1> 
                            or name == <definedName2>)
                         --select @iot.id <definedId> and not (name == <definedName1> 
                            or name == <definedName2>)
                            
  --show [SHOW [SHOW ...]]
                        selects which fields of the results to show as output.
                        Usable with multiple values at once, use 'all'
                        to show all fields
                        
  --sql [FILE]          select a file from which to execute a sql-like query

  --store STORE         store the results of command execution in the
                        specified file
                        
  -t OGC, --ogc OGC, --type OGC
                        select the OGC Model name of the items to process
                        
  --template [FILE]     must be used with --create num [number] type [entity type] file [storing file]:
                        creates [number] records with a valid random name for [entity type] in [storing file],
                        following the template stored in FILE. More fields can be added in the form of [field, 
                        value] as --create additional arguments
```

More details about GOST-CLI implementation:

### Special characters
Some systems do not accept "<" and ">" characters, so those alternatives in conditional
statements are available:
```
"<" --> "lt"
">" --> "gt"
"<=" --> "lteq"
">=" --> "gteq"
```
### Examples
Different ways of getting the Sensor with @iot.id = 1 
and name = "test_name":
```
--get -t Sensors --select name == test_name and @iot.id == 1
1 --get -t Sensors
--get 1 -t Sensors
test_name --get -t Sensors
-t Sensors --get test_name

```
Getting all the Sensors and showing their
@iot.id and description:
```
--get -t Sensors --show @iot.id description
```

Getting all the Sensors with name = "test_name" OR @iot.id = 5
```
--get -t Sensors --select or @iot.id 5 name test_name
```

Getting all the Sensors with 
metadata = "test_metadata" AND description = "test_description"
```
--get -t Sensors --select metadata == test_metadata and description == test_description

```


Getting all the Sensors with 
metadata = "test_metadata" OR description = "test_description"
```
--get -t Sensors --select metadata == test_metadata or description == test_description

```

Getting all the Sensors with name = "test_name" OR 
with @iot.id between "lower_bound" and "upper_bound", extremes included

```
-g -t Sensors --select name == test_name or (@iot.id >= lower_bound and @iot.id <= upper_bound)
```

Getting all the Sensors with the word "test" in name and "2018" not in name

```
-g -t Sensors --select test in name and 2018 not in name
```

Different ways of deleting the Sensor with @iot.id = 1 
and name = "test_name":
```
1 --get -t Sensors --delete
--get 1 -t Sensors -d
1 -t Sensors -d 
```

Deleting all the Sensors (a warning message will be displayed before proceeding):
```
-t Sensors --d
```

Creating and storing 5 Sensors with default values to a file with path = "file_path":
```
--create num 5 file "file_path" -t Sensors
```
Creating and storing 5 Sensors with default values except the description, which will be
equal to "new_description", to a file with path = "file_path":
```
--create num 5 file file_path description new_description --type Sensors
```
Creating two Sensors without specifying the ogc type: the system will ask
to the user to insert it
```
interface.py --create num 2   <-- User input
Missing Ogc Type, insert one: <-- System response
Sensors
Created a file in created_files/Sensors with 2 Sensors
```
Posting to GOST all the Sensors stored in a txt file with path = "file_path":
```
--post file_path -t Sensors
```

Setting the GOST address to which send requests to http://x.x.x.x:port_number/v1.0
```
-G http://x.x.x.x:port_number/v1.0
```

Executing a list  of commands stored in a file with absolute path = "file_path"
```
--execute "file_path"
```
Storing all sensor in a file with absolute path = "file_path"
```
--get --type Sensors --store "file_path"
```

Make a sql-like query from a file with path "file_path"
```
--sql "file_path"

Format of the stored query:
<conditions on an entity type> as <name of the first result> join
<conditions on an entity type> as <name of the second result>
on <comparisons between fields of the results>
show <results to show>
```
Sql-like query to find all the Datastreams linked to Things with "Temperature" in name and showing their id's
```
-t Things --select "Temperature" in name as Temp_Thing join
-g -t Datastreams as Streams 
on [Streams]Thing@iot.navigationLink == [Temp_Thing]@iot.selfLink
show [Streams]@iot.id [Temp_Thing]@iot.id
```
Creating 20 Sensors from the template stored in <template file path>,
adding a <custom description> and storing them in <storing file path>.
Below the command, an example of the template
```
--template <template file path> --create num 20 type Sensors file <storing file path> description <custom description>
Template file content:
{"encodingType": "application/pdf",
"metadata": "default metadata"}
```

## Next steps
GOST-CLI is still under active development. Several extensions will be available soon.

*selective selection of records from file
* implementing a test mode
* storing custom commands and settings and tying them to a user account


## Contacts
Feel free to contact [Giacomo Robino](http://giacomo.robino.it), [Luca Mannella](http://ismb.it/luca.mannella) or [Jacopo Foglietti](http://ismb.it/jacopo.foglietti/)
for any ideas, improvements, and questions.


## Licensing
**Copyright © 2019 [Giacomo Robino](http://ismb.it/giacomo.robino/), [Luca Mannella](http://ismb.it/luca.mannella) 
 and [Jacopo Foglietti](http://ismb.it/jacopo.foglietti/)
 for [LINKS Foundation](http://linksfoundation.com/).**

*GOST-CLI* is licensed under the 2-Clause BSD License ([BSD-2-Clause](https://opensource.org/licenses/BSD-2-Clause)).
