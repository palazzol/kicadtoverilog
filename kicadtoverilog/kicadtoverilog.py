# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 09:18:39 2021

@author: frank
"""

import pprint  # for testing
import sexpr   # for parsing


TEST_SCHEMATIC      = 'kicadtoverilog_test.kicad_sch'
KICAD_PROJECT_DIR   = '..\\kicadtoverilog_test\\'
VERILOG_PROJECT_DIR = '..\\verilog\\'


# A Symbol definition, cached in a schematic page
class Symbol:
    def __init__(self,parsed):
        self.name = ''
        self.pin_type = []
        self.pin_loc = []
        self.pin_name = []
        self.pin_num = []
        #pprint.pp(parsed)
        for elem in parsed[2:]:
            if isinstance(elem, list):
                if elem[0] == 'property':
                    if elem[1] == 'Value':
                        self.name = elem[2]
                elif elem[0] == 'symbol':
                    for elem1 in elem:
                        if elem1[0]=='pin':
                            self.pin_type.append(elem1[1])
                            for elem2 in elem1[3:]:
                                if elem2[0] == 'at':
                                    self.pin_loc.append((elem2[1],elem2[2]))
                                elif elem2[0] == 'name':
                                    self.pin_name.append(elem2[1])
                                elif elem2[0] == 'number':
                                    self.pin_num.append(elem2[1])
        #print(self.name, self.pin_type, self.pin_loc, self.pin_name, self.pin_num)
        #print()

# A Symbol Instance on a schematic page
class SymbolInstance:
    def __init__(self,parsed):
        self.name = ''
        self.symtype = ''
        self.loc = (0,0)
        for item in parsed:
            if item[0] == 'at':
                self.loc = (item[1],item[2])
            elif item[0] == 'property':
                #pprint.pp(item)
                if item[1] == 'Reference':
                    self.name = item[2]
                elif item[1] == 'Value':
                    self.symtype = item[2]
                
# A Sheet (symbol) on a schematic page
class Sheet:
    def __init__(self,parsed):
        self.instancename = ''
        self.filename = ''
        self.pin_name = []
        self.pin_type = []
        self.pin_loc = []
        for property in parsed:
            if property[0] == 'property':
                if property[1] == 'Sheet name':
                    self.instancename = property[2]
                elif property[1] == 'Sheet file':
                    self.filename = property[2]
            elif property[0] == 'pin':
                pin_name = property[1]
                pin_type = property[2]
                for n in range(3,len(property)):
                    x = property[n]
                    if x[0] == 'at':
                        self.addPin(pin_name,pin_type,x[1],x[2])
                        
    def addPin(self,name,pintype,x,y):
        self.pin_name.append(name)
        self.pin_type.append(pintype)
        self.pin_loc.append((x,y))
        #print(self.filename,self.instancename,name,pintype,(x,y))
        
# A Schematic Page, created by parsing a *.kicad_sch file
class Page:
    def __init__(self, filename, recurse):
        self.sheets = []
        self.symbolinsts = []
        self.symbols = []
        self.filename = filename
        self.port_name = []
        self.port_loc = []
        self.port_type = []
        self.wires = []
        self.junctions = []
        self.wire1 = []
        self.wire2 = []
        parsed = ParseFile(self.filename)
        for elem in parsed:
            if elem[0] == 'sheet':
                sheet = Sheet(elem)
                self.sheets.append(sheet)
            elif elem[0] == 'symbol':
                symbolinst = SymbolInstance(elem)
                self.symbolinsts.append(symbolinst)
                #print(symbolinst.name,symbolinst.symtype,symbolinst.loc)
            elif elem[0] == 'lib_symbols':
                for elem1 in elem[1:]:
                    symbol = Symbol(elem1)
                    self.symbols.append(symbol)
            elif elem[0] == 'hierarchical_label':
                self.port_name.append(elem[1])
                for elem1 in elem[2:]:
                    if elem1[0] == 'at':
                        self.port_loc.append((elem1[1],elem1[2]))
                    elif elem1[0] == 'shape':
                        self.port_type.append(elem1[1])
            elif elem[0] == 'wire':
                wire_loc1 = (elem[1][1][1],elem[1][1][2])
                wire_loc2 = (elem[1][2][1],elem[1][2][2])
                self.wire1.append(wire_loc1)
                self.wire2.append(wire_loc2)
                #print('Wire:',wire_loc1,wire_loc2)    
            elif elem[0] == 'junction':
                junction_loc = (elem[1][1],elem[1][2])
                self.junctions.append(junction_loc)
                #print('Junction:',junction_loc)
        # Create a reference from each symbolinst to it's symbol
        self.CreateSymbolRefs()
                
    def Sheets(self):
        return self.sheets
    
    def CreateSymbolRefs(self):
        # Link Symbols with SymbolRefs
        # Add symbolinst[i].pin_loc
        for i in range(0,len(self.symbolinsts)):
            value = self.symbolinsts[i].symtype
            for j in range(0,len(self.symbols)):
                if self.symbols[j].name == value:
                    self.symbolinsts[i].symbol = self.symbols[j]
                    symbol_loc = self.symbolinsts[i].loc
                    self.symbolinsts[i].pin_loc = []
                    for k in range(0,len(self.symbolinsts[i].symbol.pin_loc)):
                        pin_loc = self.symbolinsts[i].symbol.pin_loc[k]
                        inst_loc = (round(symbol_loc[0] + pin_loc[0],2),round(symbol_loc[1]+pin_loc[1],2))
                        self.symbolinsts[i].pin_loc.append(inst_loc)

    def DumpNets(self):
        print(self.junction_nets)
        print(self.wire_nets)
        print(self.port_nets)
        print()
        for sheet in self.sheets:
            print(sheet.pin_nets)
        print()
        for symbolinst in self.symbolinsts:
            print(symbolinst.name)
            print(symbolinst.pin_nets)
        print()
            
    def CreateNets(self):
        # Mark all nets as unknown
        self.junction_nets = [0]*len(self.junctions)
        self.wire_nets = [0]*len(self.wire1)
        self.port_nets = [0]*len(self.port_name)
        for sheet in self.sheets:
            sheet.pin_nets = [0]*len(sheet.pin_name)
        for symbolinst in self.symbolinsts:
            symbolinst.pin_nets = [0]*len(symbolinst.symbol.pin_name)
            
        #self.DumpNets()
        
        current_net = 1
        for i in range(0,len(self.junction_nets)):
            if self.junction_nets[i] == 0:
                self.junction_nets[i] = current_net
                self.PropagateNet(current_net, self.junctions[i])
                current_net += 1
        for i in range(0,len(self.wire_nets)):
            if self.wire_nets[i] == 0:
                self.wire_nets[i] = current_net
                self.PropagateNet(current_net, self.wire1[i])
                self.PropagateNet(current_net, self.wire2[i])
                current_net += 1
        
        # rename nets to eliminate port pins
        self.num_nets = current_net-1
        self.net_names = ['wire_NC']*(self.num_nets+1)
        for i in range(1, self.num_nets+1):
            renamed = False
            for j in range(0,len(self.port_nets)):
                if self.port_nets[j] == i:
                    self.net_names[i] = self.port_name[j]
                    renamed = True
            if not renamed:
                self.net_names[i] = 'net_'+str(i)
        #self.DumpNets()
                
    def PropagateNet(self,net,loc):
        done = False
        while not done:
            done = True
            for i in range(0,len(self.junctions)):
                if self.junction_nets[i] == 0:
                    if self.junctions[i] == loc:
                        self.junction_nets[i] = net
                        done = False
            for i in range(0,len(self.wire1)):
                if self.wire_nets[i] == 0:
                    if self.wire1[i] == loc:
                        self.wire_nets[i] = net
                        self.PropagateNet(net,self.wire2[i])
                        done = False
                    if self.wire2[i] == loc:
                        self.wire_nets[i] = net
                        self.PropagateNet(net,self.wire1[i])
                        done = False
            for i in range(0,len(self.port_nets)):
                if self.port_nets[i] == 0:
                    if self.port_loc[i] == loc:
                        self.port_nets[i] = net
                        done = False
            for sheet in self.sheets:
                for i in range(0,len(sheet.pin_nets)):
                    if sheet.pin_nets[i] == 0:
                        if sheet.pin_loc[i] == loc:
                            sheet.pin_nets[i] = net
                            done = False
            for symbolinst in self.symbolinsts:
                for i in range(0,len(symbolinst.pin_nets)):
                    if symbolinst.pin_nets[i] == 0:
                        if symbolinst.pin_loc[i] == loc:
                            symbolinst.pin_nets[i] = net
                            done = False
                                
    def Dump(self):     
        print('Page: ',self.filename)
        print()
        
        print("Ports:")
        for i in range(0,len(self.port_name)):
            print(self.port_name[i],self.port_loc[i])
        print()
        
        print("Sheet Pins:")
        for i in range(0,len(self.sheets)):
            print(self.sheets[i].filename,self.sheets[i].instancename)
            for j in range(0,len(self.sheets[i].pin_name)):
                print(self.sheets[i].pin_name[j],self.sheets[i].pin_loc[j])
        print()
    
        print("Symbol Pins:")
        for i in range(0,len(self.symbolinsts)):
            name = self.symbolinsts[i].name
            #value = self.symbolinsts[i].symtype
            baseloc = self.symbolinsts[i].loc
            symbol = self.symbolinsts[i].symbol
            print(name, symbol.name)
            for j in range(0,len(symbol.pin_name)):
                loc = (round(symbol.pin_loc[j][0] + baseloc[0],2), round(symbol.pin_loc[j][1] + baseloc[1],2)) 
                print(symbol.pin_name[j], symbol.pin_num[j], loc)

        print()
        
def ParseFile(fname):
    print('Reading file:',fname);
    with open(KICAD_PROJECT_DIR+fname,'r') as f:
        sexp = f.read()
        return sexpr.parse_sexp(sexp)
    
# Parse schematic files recursively
def PageCreateRecursive(pageNames, pages, filename):
    page = Page(filename, False)
    pages.append(page)
    pageNames.append(page.filename)

    for sheet in page.Sheets():
        if sheet.filename in pageNames:
            pass
        else:
            PageCreateRecursive(pageNames, pages, sheet.filename)
            
# Parse Schematic Files starting with the top one in the heirarchy
def ParseFiles(pages, topfilename):
    pageNames = []
    PageCreateRecursive(pageNames, pages, topfilename)
    
######################################################

pages = []

# Parse all the pages
ParseFiles(pages, TEST_SCHEMATIC)

# Create netlists for each page
print("Creating netlists...")
for page in pages:
    page.CreateNets()
    
# Generate Verilog files

for page in pages:
    module_name = page.filename.replace('.','_')
    print("Writing file:",module_name+".v")
    with open(VERILOG_PROJECT_DIR+module_name+'.v','w') as f:
        f.write('module '+ module_name + '(\n')
        for i in range(0,len(page.port_name)):
            if i != 0:
                f.write(',\n')
            f.write('    '+page.port_type[i]+' '+page.port_name[i])
        f.write(');\n\n')
        wires_written = False
        for i in range(1,page.num_nets+1):
            if page.net_names[i][0:4] == 'net_':
                f.write('    wire '+page.net_names[i]+';\n')
                wires_written = True
        if wires_written:
            f.write('\n');
        for s in page.symbolinsts:
            f.write('    '+s.symtype+' '+s.name+'(')
            for i in range(0,len(s.pin_nets)):
                if i!=0:
                    f.write(', ');
                f.write(page.net_names[s.pin_nets[i]])
            f.write(');\n')
        for s in page.sheets:
            sheet_name = s.filename.replace('.','_')
            f.write('    '+sheet_name+' '+s.instancename+'(')
            for i in range(0,len(s.pin_nets)):
                if i!=0:
                    f.write(', ');
                f.write(page.net_names[s.pin_nets[i]])                  
            f.write(');\n')
        f.write('endmodule\n')

    
    
    
