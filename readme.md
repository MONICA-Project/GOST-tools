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
  -h, --help            show this help message and exit
  -f FILE, --file FILE  choose a FILE from which execute a list of commands
  -t OGC, --ogc OGC, --type OGC
                        select the OGC Model name of the items to process
  -m MODE, --mode MODE  Select an alternative mode of operation.Actually
                        available modes: 
                         - test
  -d, --delete          delete the items chosen with get: 
                        example
                         --get 15 -t Sensors --delete
  -i, --info            shows the current GOST address and operation mode
  -p [PATCH [PATCH ...]], --patch [PATCH [PATCH ...]]
                        patch the choosen item FIELD with selected VALUE,usable
                        with multiple values at once 
                        examples: 
                        --p id <newId> name <newName>
                        --p description <newDescription> 
  -s [SELECT [SELECT ...]], --select [SELECT [SELECT ...]]
                        selection of the items from those found with
                        --get,before any further operation like delete or
                        patch. Choosen items are those in which FIELD has the
                        selected VALUE. It is usable with multiple values at once,
                        starting with "and/or" depending if the user wants ALL fields
                        matching or AT LEAST one
                        example: 
                         --select id <definedId> name <definedName>)
                         --select and id <definedId> name <definedName>)
                         --select or id <definedId> name <definedName>)
  --show [SHOW [SHOW ...]]
                        select which fields of the results of the elaborations 
                        to show as output.
                        Usable with multiple values at once, use 'all'
                        to show all fields
  -G GOSTADDRESS, --GOSTaddress GOSTADDRESS, --address GOSTADDRESS
                        sets a new address (IP and port) for GOST
  --pingconnection, --connectiontest, --conntest
                        sends a ping to test the connection
  -g, --get             get the items of the currently selected ogc type,if
                        one or more item identifiers or name are definited,
                        or all the items of selected type if no id or name 
                        is provided. The query results are
                        saved for successive operations like delete or patch
  --interactive         starts an interactive session, --exit to return
                        to shell
  --exit                exit from the program when you are in an interactive session
  --post [POST [POST ...]]
                        posts records from user defined file/s to currently
                        selected OGC types('--post <file_name> -t <type>'
  --create [CREATE [CREATE ...]]
                        Creates n items of type t in created_files/<type>,
                        or in the file defined with 'file <filename>
                        you can define field values for created records
                        otherwise default value will be used
                        (ex: --create num 2 description new_description --type Sensors)
```

More details about GOST-CLI implementation

### Examples
Different ways of getting the Sensor with @iot.id = 1 
and name = "test_name":
```
1 --get -t Sensors
--get 1 -t Sensors
test_name --get -t Sensors
-t Sensors --get test_name
--get -t Sensors --select name test_name
--get -t Sensors --select name test_name @iot.id = 1

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

Two ways of getting all the Sensors with 
name = "test_name" AND description = "test_description"
```
--get -t Sensors --select name test_name description test_description
--get -t Sensors --select and name test_name description test_description

```


Getting the Sensor with 
name = "Separated name" and the Sensor with @iot.id = 15
description = "test_description"
```
"Separated name" 15 --get -t Sensors

```

Different ways of deleting the Sensor with @iot.id = 1 
and name = "test_name":
```
1 --get -t Sensors --delete
--get 1 -t Sensors -d
```

Deleting all the Sensors (a warning message will be displayed before proceeding):
```
--get -t Sensors --d
```

Creating and storing 5 Sensors with default values to a file with path = "file_path":
```
--post num 5 type Sensors file file_path
```

Creating and storing 5 Sensors with default values except the description, which will be
 equal to "new_description", to a file with path = "file_path":
```
--post num 5 description new_description file file_path --type Sensors
```

Posting to GOST all the Sensors stored in a txt file with path = "file_path":
```
--post file_path -t Sensors
```

Setting the GOST address to which send requests to 192.168.99.100:8080
```
-G 192.168.99.100:8080
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
