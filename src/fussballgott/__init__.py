__author__ = "Silvan Fischbacher"
__email__ = "silvan.fischbacher@greenmail.ch"
__credits__ = ["Silvan Fischbacher"]

__version__ = "0.1.0"


from . import fussball, league, load, plot, team, tournament  # noqa

print("WELCOME TO THE FUSSBALLGOTT PACKAGE")

asci_art = """
                       _,aaadP\"\"\"\"\"\"Ybaaaa,,_
                   ,adP,__,,,aaaadP\"\"\"\"\"Y888888a,_
                ,a8888888P\"''             \"Y8888888b,
             _a888888888\"                   `Y88888888b,
           ,d888888888P'                       \"888888888b,
         ,88888888P\"Y8,                       ,P'   `\"\"Y888b,
       ,d8888P\"'     \"Ya,                    ,P'         `Ya`b,
      ,P88\"'           `Ya,                 ,P'            `b`Yi
     d\",P                `\"Y,              ,P'              `Y \"i
   ,P' P'                   \"888888888888888b                `b \"i
  ,P' d'                    d8888888888888888b                `b `b
  d' d'                    ,888888888888888888b                I, Y,
 ,f ,f                    ,88888888888888888888b               `b, b
 d' d'                    d888888888888888888888b              ,88,I
,P  8                    ,88888888888888888888888b,_          ,d8888
d'  8,                   d8888888888888888888888P'`\"Ya,_     ,d88888
8  d88b,             ,adP\"\"Y888888888888888888P'      `\"\"Ya, d88888P
8 ,88888b,       ,adP\"'     `\"Y8888888888888\"'             `\"888888I
Y,88888888b, ,adP\"'             \"\"Y888888P\"                  888888'
`888888888888P'                     \"\"YP\"                    888888
 I88888888888                          8                     88888I
 `Y8888888888                          8                     88888'
  `Y888888888                          8                     8888I
   `Y88888888                          8                     8P\"8'
    `Y8888888,                         8                   ,d',d'
     `b\"\"\"\"Y8b                         8                 ,d\" ,d'
       \"b,   \"Y,                       8               ,P\" ,d\"
         \"b,   \"Ya,_                 ,d88ba,,___   _,aP\" ,P\"
           \"Ya_   \"\"Ya,_       _,,ad88888888888888P\"' _,d\"
             `\"Ya_    \"\"Yaaad88888888888888888888P _,d\"'
                 `\"Ya,_     \"Y888888888888888888P\",d\"'
                    `\"\"Ya,__`Y888888888888888P\"\"\"
                         ``\"\"\"\"\"\"\"\"\"\"\"\"\"''

"""
# Thanks to Normand Veilleux for the asci art
print(asci_art)
