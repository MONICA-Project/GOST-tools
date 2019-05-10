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
                        selected VALUE,usable with multiple values at once
                        example: 
                         --select id <definedId> name <definedName>)
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
                        one or more identifiers are definited,or all the items
                        of seleted typeif nothing is defined. The results are
                        saved for successive operationslike delete and patch
  --exit                exit from the program
  --interactive         starts an interactive session, --exit to return
                        toshell
  --post [POST [POST ...]]
                        posts records from user defined file/s tocurrently
                        selected OGC typees('--post <file_name> -t <type>'
  --create [CREATE [CREATE ...]]
                        Creates n items of type t in created_files/<type>,or
                        in the file defined with 'file <filename> you can
                        define field values for created records otherwise
                        default value will be used(ex: --create num 2 type
                        Sensors description newDesc)
```

More details about GOST-CLI implementation

### Examples
ex 1
```
./scral.py -h
```

ex 2
```
./scral.py -h
```

ex 3
```
./scral.py -h
```


## Other information
Insert here more relevant information.


## Next steps
GOST-CLI is still under active development. Several extensions will be available soon.

* nuova cosa 1
* nuova cosa 2
* nuova cosa 3


## Contacts
Feel free to contact [Giacomo Robino](http://giacomo.robino.it), [Luca Mannella](http://ismb.it/luca.mannella) or [Jacopo Foglietti](http://ismb.it/jacopo.foglietti/)
for any ideas, improvements, and questions.


## Licensing
**Copyright © 2019 [Giacomo Robino](http://ismb.it/giacomo.robino/), [Luca Mannella](http://ismb.it/luca.mannella) 
 and [Jacopo Foglietti](http://ismb.it/jacopo.foglietti/)
 for [LINKS Foundation](http://linksfoundation.com/).**

*GOST-CLI* is licensed under the 2-Clause BSD License ([BSD-2-Clause](https://opensource.org/licenses/BSD-2-Clause)).
