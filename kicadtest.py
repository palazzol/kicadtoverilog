# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 09:18:39 2021

@author: frank
"""

import pprint  # for testing
import sexpr   # for parsing

TESTHARNESS_SCHEMATIC = 'test.kicad_sch'

chip_file = ''

class VerilogSymbol:
    def __init__(self,syminst,symtype):
        self.syminst = syminst
        self.symtype = symtype
        
class VerilogModule:
    def __init__(self,name,filename):
        self.name = name
        self.filename = filename
        self.pin_name = []
        self.pin_type = []
        self.symbol = []
        self.wire = []
        self.chip = []
        
    def addPin(self,name,pintype):
        self.pin_name.append(name)
        self.pin_type.append(pintype)
        
    def addSymbol(self,symbol):
        self.symbol.append(symbol)
    
    def addSheet(self,chip):
        self.chip.append(chip)
        
    def addWire(self,wire):
        self.wire.append(wire)
        
    def print(self):
        print(self.name)
        print(self.filename)
        print(self.pin_name)
        print(self.pin_type)
        print()

def ParseFile(fname):
    with open(fname,'r') as f:
        sexp = f.read()
        return sexpr.parse_sexp(sexp)
    
def ParseSymbols(chip,parsed):
    for symbol in parsed:
        if symbol[0] == 'symbol':
            for item in symbol:
                if item[0] == 'property':
                    if item[1] == 'Reference':
                        syminst = item[2]
                    elif item[1] == 'Value':
                        symtype = item[2]
                        s = VerilogSymbol(syminst,symtype)
                    elif item[1] == 'pin':
                        s.addPin(item[2])
            chip.addSymbol(s)
    
def ParseSheets(chip1,parsed):
    for sheet in parsed:
        if sheet[0] == 'sheet':
            for property in sheet:
                if property[0] == 'property':
                    if property[1] == 'Sheet name':
                        chip_name = property[2]
                    elif property[1] == 'Sheet file':
                        chip_file = property[2]
                        chip = VerilogModule(chip_name, chip_file)
                elif property[0] == 'pin':
                    chip.addPin(property[1],property[2])
            if not chip1 is None:
                chip1.addSheet(chip)
            if not (chip_file in chip_list):
                chip_list[chip_file] = chip
                HandleSheet(chip)
                
def HandleSheet(chip1):
    parsed = ParseFile(chip1.filename);
        
    ParseSymbols(chip1,parsed)
    #ParseWires()
    
    ParseSheets(chip1,parsed)
    
######################################################

chip_list = {}
    
parsed = ParseFile(TESTHARNESS_SCHEMATIC)
ParseSheets(None,parsed)

for item in chip_list:
    chip = chip_list[item]
    module_name = chip.filename.replace('.','_')
    with open(module_name+'.v','w') as f:
        f.write('module '+ module_name + '(\n')
        for i in range(0,len(chip.pin_name)):
            if i != 0:
                f.write(',\n')
            f.write('    '+chip.pin_type[i]+' '+chip.pin_name[i])
        f.write(');\n')
        f.write('\n    // TBD wires\n\n')
        for s in chip.symbol:
            f.write('    '+s.symtype+' '+s.syminst+'(/* */);\n')
        for c in chip.chip:
            symbol_name = c.filename.replace('.','_')
            f.write('    '+symbol_name+' '+c.name+'(/* */);\n')
        f.write('endmodule\n')
    
    
    
