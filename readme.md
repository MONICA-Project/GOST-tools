# GOST - Command Line Interface (CLI)

[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)
![Language: Python3](https://img.shields.io/badge/language-python3-blue.svg)

![Logo](images/example.png)


## Getting Started
*GOST-CLI* is a tool for interacting via command-line with a GOST
server

### Install
GOST-CLI requires Python 3 or greater (it was tested on Python 3.7 so it's suggest to use this version) 

#### Clone the repository
```
git clone https://git.pertforge.ismb.it/Students-Projects/gost-cli.git
```


## How to use GOST-CLI
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
                        
  --exit                exits from the program when you are in an interactive session
 
                        
  -d, --delete          delete the items chosen with get or selected
                        giving id or name: 
                        example:
                         --get 15 -t Sensors --delete
                          15 16 -t Sensors --delete  
  --file                execute a of commands, this command
                        requires the absolute file path inside ""
                        example:
                         --file "absolute_filepath"
                         --file "absolute_filepath_1" "absolute_filepath_2"
   
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
                        
  --related [ogc_entity_type]
                        gets the entities of ogc_entity_type which shares a datastream with the
                        currently selected items, and adds a field "related <ogc type of the previously
                        selected items>" to each result
                        Accepts select <boolean expression> as additional value to filter the results
                        
                        example:
                        1 --type Sensors --related Observations
                        1 --type Sensor --related Observations select @iot.id > 10
                        
                        If the currently selected item is a datastream, found the related items
                        
                        example: find all the Observations of the datastreams with @iot.id 10 and 11
                        10 11 -t Datastreams --related Observations
                        
                        If the currently selected item is a not datastream, and the related command type
                        is a datastream, will find all the datastreams related to the selcted item/s
                        
                        example: find all the datastreams related to the things with @iot.id 10 and 11
                        10 11 -t Things --related Datastreams
                        
                        A select condition may be added before the related type
                        example: find all the Observations of the datastreams with @iot.id 10 and 11,
                        which have a result > 10
                        10 11 -t Datastreams --related Observations select result > 10
                        
  -s [SELECT [SELECT ...]], --select [SELECT [SELECT ...]]
                        selection of the items (between " " or ' ') to process,
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
  
  --silent              shuts all the outputs
                        
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

### Use Cases

#### Create Elements (POST)

##### Posting to the GOST server *"n"* new items of entity type *"t"* with a specific field value

This is a two-step operation: first of all, you need to create a local file with 
the representation of the items that you want to create, then you have to upload the
represented items to the server

###### First step: creating a file with the records

There are two ways of getting this done: using a pre-defined template,
or without it.

Posting with a template:

The template is a .txt file JSON-like formatted as you can see in the following example:
```
{
    "field 1 name" : "value 1",
    "field 2 name" : "value 2",
    ...
}
```
In this case:
```
{
    "field_name" : "chosen field's value",
}
```
Then, when you use the --template command followed by this file path, that template 
will be used as a base for the new created items, in this case the Sensors

In addition to the --template command, one must use the --create command, to specify:


* how many items create

* in which file store them

* the type of the created item (the program will check for the mandatory fields and default fields values,
according to it)

* other custom field values, if needed (this will override the value definition given in template
or in default implementation)

Those specifications are preceded respectively by "num", "file", "type" and by < field_name > and < field_value >


So our final command will be:
```
--template <template file path> --create num n file <storing_file_path> type t
```

In the case you don't want to use a template, it is possible to use only the --create command.
You have to pass as --create arguments the custom values that you want to assign to a specified field, 
preceded by the field's value.

So the command of this use case will be
```
--create num n file <storing_file_path> metadata "chosen metadata value" type t
```
###### Second step: posting the created records to the server
To post a file of records to the GOST server, you have to use the --post command
followed by the file path, and the --type command to specify the ogc entity type
to which post the records. In this case:
```
--post <storing_file_path> --type Sensors
```
Then will be showed the outcome of the posting operation

#### Modify existing elements (PATCH)
##### Patching an item's "description" field to a desired value, knowing the item's @iot.id

You need only one step to achieve this result: first of all you have to specify the item to patch,
which can be done in several ways:
```
--get <@iot.id value> -t <item's ogc entity type>
--select @iot.id == '<@iot.id value>' -t <item's ogc entity type> 
```


### Examples of single commands
Different ways of getting the Sensor with @iot.id = 1 
and name = "test_name":
```
--get -t Sensors --select name == "test_name" and @iot.id == 1
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
--get -t Sensors --select metadata == "test_metadata" and description == "test_description"
```

Getting all the Sensors with 
metadata = "test_metadata" OR description = "test_description"
```
--get -t Sensors --select metadata == "test_metadata" or description == "test_description"
```

Getting all the Sensors with name = "test_name" OR 
with @iot.id between "lower_bound" and "upper_bound", extremes included

```
-g -t Sensors --select name == "test_name" or (@iot.id >= "lower_bound" and @iot.id <= "upper_bound")
```

Getting all the Sensors with the word "test" in name and "2018" not in name
(to search multiple words separated by a space, is necessary to use quotes).

```
-g -t Sensors --select test in name and 2018 not in name
--get -t Sensors --select "test name" in name
```

[NOT SUPPORTED] Getting all the Observations which both share a Datastream with Sensors with @iot.id < 10 
and have a result greater than 100
```
--select @iot.id < 10 -t Sensors --related Observations select result > 100

If you want to delete those Observations, you only need to add the --delete command:
--select @iot.id < 10 -t Sensors --related Observations select result > 100 --delete
```

Different ways of deleting the Sensor with @iot.id = 1 and name = "test_name":
```
1 --get -t Sensors --delete
--get 1 -t Sensors -d
-g "test_name" -t Sensors -d
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
Creating 20 Sensors from the template stored in < template_file_path >,
adding a < custom_description > and storing them in < storing_file_path >.
Below the command, an example of the template
```
--template <template file path> --create num 20 type Sensors file <storing file path> description <custom description>

Template file content:
{
    "encodingType": "application/pdf",
    "metadata": "default metadata"
}
```

Posting to GOST all the Sensors stored in a txt file with path = "file_path":
```
--post file_path -t Sensors
```
Storing all sensor in a file with absolute path = "file_path"
```
--get --type Sensors --store "file_path"
```

Setting the GOST address to which send requests to http://x.x.x.x:port_number/v1.0
```
-G http://x.x.x.x:port_number/v1.0
```

Executing a list  of commands stored in a file with absolute path = "file_path"
```
--file "file_path"
```

Make a sql-like query from a file with path "file_path"
```
--sql "file_path"

Format of the stored query:
<conditions on an entity type> as <name of the first table> join
<conditions on an entity type> as <name of the second table>
on <[name of the table]><comparisons between fields of the results> (join condition)
show <[name of the table]results to show(separated by "and")>

Query format example:
--get -t Sensors --select id > '990' as t1 join
--get -t Sensors --select id < '3' as t2
on [t1]description == [t2]description
show [t1]name and [t2]description
```

## More details about GOST-CLI implementation:

#####SPECIAL CHARACTERS

Some systems do not accept "<" and ">" characters, so those alternatives in conditional
statements are available:
```
"<" --> "lt"
">" --> "gt"
"<=" --> "lteq"
">=" --> "gteq"
```

## Next steps
GOST-CLI is still under active development. Several extensions will be available soon.

* SQL functionality on the GUI
* dynamic expansion of the GUI elements (especially the result widget) according to the program application window
* Pop-up that appears when the user presses the search button and disappear automatically when the query computation is ended
* display messages when hovering over something with mouse cursor in the GUI
* selective selection of records from file
* implementing a test mode
* storing custom commands and settings and tying them to a user account


## Contacts
Feel free to contact Giacomo Robino, Emanuel Frulla, [Luca Mannella](http://ismb.it/luca.mannella) or [Jacopo Foglietti](http://ismb.it/jacopo.foglietti/)
for any ideas, improvements, and questions.


## Licensing
**Copyright © 2019 Giacomo Robino, Emanuel Frulla, [Luca Mannella](http://ismb.it/luca.mannella) 
 and [Jacopo Foglietti](http://ismb.it/jacopo.foglietti/)
 for [LINKS Foundation](http://linksfoundation.com/).**

*GOST-CLI* is licensed under the 2-Clause BSD License ([BSD-2-Clause](https://opensource.org/licenses/BSD-2-Clause)).
