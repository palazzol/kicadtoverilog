# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 09:18:39 2021

@author: palazzol
"""

#import pprint  # for testing
import sexpr   # for parsing
import argparse
import shutil

# Convert KiCad name "~{XXX}" to legal Verilog name "not_XXX"
def ConvertUnderbarName(name):
    return name.replace('~{','not_').replace('}','')
    
# A Symbol definition, cached in a schematic page
class Symbol:
    def __init__(self,parsed):
        self.name = ''      # Symbol Name
        # for each pin, we have lists of type, location (relative), name, and number
        self.pin_type = []
        self.pin_loc = []
        self.pin_name = []
        self.pin_num = []
        #pprint.pp(parsed)
        # initialize from the s-expressions
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
                                    self.pin_name.append(ConvertUnderbarName(elem2[1]))
                                elif elem2[0] == 'number':
                                    self.pin_num.append(elem2[1])
        #print(self.name, self.pin_type, self.pin_loc, self.pin_name, self.pin_num)
        #print()

# A Symbol Instance on a schematic page
class SymbolInstance:
    def __init__(self,parsed):
        self.name = ''      # instance RefDes
        self.symtype = ''   # instance Value (type name)
        self.loc = (0,0)    # instance location
        # initialize from the s-expressions
        for item in parsed:
            if item[0] == 'at':
                self.loc = (item[1],item[2],item[3])
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
        # for each pin, we have lists of type, location (absolute), name
        self.pin_name = []
        self.pin_type = []
        self.pin_loc = []
        # initialize from the s-expressions
        for property in parsed:
            if property[0] == 'property':
                if property[1] == 'Sheet name':
                    self.instancename = property[2]
                elif property[1] == 'Sheet file':
                    self.filename = property[2]
            elif property[0] == 'pin':
                pin_name = ConvertUnderbarName(property[1])
                pin_type = property[2]
                for n in range(3,len(property)):
                    x = property[n]
                    if x[0] == 'at':
                        self.pin_name.append(pin_name)
                        self.pin_type.append(pin_type)
                        self.pin_loc.append((x[1],x[2]))
                        #print(self.filename,self.instancename,pin_name,pin_type,(x[1],x[2]))
        
# A Schematic Page, created by parsing a *.kicad_sch file
class Page:
    def __init__(self, path, filename, recurse):
        self.filename = filename
        
        self.sheets = []
        
        self.symbolinsts = []
        self.symbols = []
        
        self.port_name = []
        self.port_loc = []
        self.port_type = []
        
        # Net stuff
        self.wires = []
        self.junctions = []
        self.wire1 = []
        self.wire2 = []
        
        # initialize from the s-expressions
        parsed = ParseFile(path, self.filename)
        for elem in parsed:
            if elem[0] == 'sheet':
                sheet = Sheet(elem)
                self.sheets.append(sheet)
            elif elem[0] == 'symbol':
                symbolinst = SymbolInstance(elem)
                self.symbolinsts.append(symbolinst)
            elif elem[0] == 'lib_symbols':
                for elem1 in elem[1:]:
                    symbol = Symbol(elem1)
                    self.symbols.append(symbol)
            elif elem[0] == 'hierarchical_label':
                self.port_name.append(ConvertUnderbarName(elem[1]))
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
                
        # Create a reference from each symbolinst to its symbol
        self.CreateSymbolRefs()
                
    def Sheets(self):
        return self.sheets
    
    def CreateSymbolRefs(self):
        # Link Symbols with SymbolRefs
        # Add symbolinst[i].pin_loc
        # This is O(N*M) in number of symbols and symbolrefs - could be optimized
        for i in range(0,len(self.symbolinsts)):
            value = self.symbolinsts[i].symtype
            for j in range(0,len(self.symbols)):
                if self.symbols[j].name == value:
                    # Calculate and save the absolute position of each symbol pin
                    self.symbolinsts[i].symbol = self.symbols[j]
                    symbol_loc = (self.symbolinsts[i].loc[0], self.symbolinsts[i].loc[1])
                    symbol_angle = self.symbolinsts[i].loc[2]
                    self.symbolinsts[i].pin_loc = []
                    # Note oddity of coordinates in KiCad...
                    # Symbol y-coordinates increase up
                    # Global y-coordinates increase down
                    # This code handles this properly
                    for k in range(0,len(self.symbolinsts[i].symbol.pin_loc)):
                        pin_loc_unrotated = self.symbolinsts[i].symbol.pin_loc[k]
                        if symbol_angle == 0:
                            pin_loc = pin_loc_unrotated
                        if symbol_angle == 90:
                            pin_loc = (-pin_loc_unrotated[1],pin_loc_unrotated[0])
                        if symbol_angle == 180:
                            pin_loc = (-pin_loc_unrotated[0],-pin_loc_unrotated[1])
                        if symbol_angle == 270:
                            pin_loc = (pin_loc_unrotated[1],-pin_loc_unrotated[0])
                        inst_loc = (round(symbol_loc[0] + pin_loc[0],2),round(symbol_loc[1]-pin_loc[1],2))
                        self.symbolinsts[i].pin_loc.append(inst_loc)

    """
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

    def DumpNets2(self):
        print('Nets')
        for i in range(1,self.num_nets+1):
            print(i,self.net_names[i])
        print('Junctions')
        print(self.junction_nets)
        print('Wires')
        print(self.wire_nets)
        print('Ports')
        print(self.port_nets)
        print(self.port_name)
        print(self.port_loc)
        print('Sheets')
        for sheet in self.sheets:
            print(sheet.instancename)
            print(sheet.pin_nets)
            print(sheet.pin_name)
            print(sheet.pin_loc)
        print('Symbols')
        for symbolinst in self.symbolinsts:
            print(symbolinst.name)
            print(symbolinst.pin_nets)
            print(symbolinst.symbol.pin_num)
            print(symbolinst.symbol.pin_name)
            print(symbolinst.pin_loc)
            
        print()
    """
    
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
        # Go through each junction with unknown net. 
        # Try to propagate this net as far as possible
        for i in range(0,len(self.junction_nets)):
            if self.junction_nets[i] == 0:
                self.junction_nets[i] = current_net
                self.PropagateNet(current_net, self.junctions[i])
                current_net += 1
        # Now go through each wire end and do the same
        for i in range(0,len(self.wire_nets)):
            if self.wire_nets[i] == 0:
                self.wire_nets[i] = current_net
                self.PropagateNet(current_net, self.wire1[i])
                self.PropagateNet(current_net, self.wire2[i])
                current_net += 1
        
        # Use the net number as the name
        self.num_nets = current_net-1
        self.net_names = ['wire_NC']*(self.num_nets+1)
        for i in range(1, self.num_nets+1):
            self.net_names[i] = 'net_'+str(i)
        #self.DumpNets2()
                
    def PropagateNet(self,net,loc):
        # Propagate the current net as far as you can
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
            #baseloc = self.symbolinsts[i].loc
            symbol = self.symbolinsts[i].symbol
            print(name, symbol.name)
            for j in range(0,len(symbolinsts[i].pin_name)):
                print(symbol.pin_name[j], symbol.pin_num[j], symbolinsts[i].pin_name[j])

        print()
        
def ParseFile(path, fname):
    LogMessage('I','Reading '+fname+'...');
    with open(path+fname,'r') as f:
        sexp = f.read()
        return sexpr.parse_sexp(sexp)
    
# Parse schematic files recursively
def PageCreateRecursive(pageNames, pages, path, filename):
    page = Page(path, filename, False)
    pages.append(page)
    pageNames.append(page.filename)

    for sheet in page.Sheets():
        if sheet.filename in pageNames:
            pass
        else:
            PageCreateRecursive(pageNames, pages, path, sheet.filename)
            
# Parse Schematic Files starting with the top one in the heirarchy
def ParseFiles(pages, path, topfilename):
    pageNames = []
    PageCreateRecursive(pageNames, pages, path, topfilename)
    
def LogMessage(typecode, message):
    if typecode == 'E':
        print('Error:   '+message)
    elif typecode == 'W':
        print('Warning: '+message)
    else:
        print('Info:    '+message)
            
######################################################

def KicadToVerilog():
    # Parsing the arguments
    parser = argparse.ArgumentParser(description = 'KiCad to Verilog')
    parser.add_argument('-i','--input',help='Input Schematic File',required=True)
    parser.add_argument('-o','--output',help='Output Directory',required=True)
    #parser.add_argument('-v','--verbose',default=False,help='Verbose Mode',required=False,action="store_true")
    global_args = parser.parse_args()
    
    pages = []
    
    # Parse all the pages
    filename = global_args.input.split('\\')[-1]
    pathparts = global_args.input.split('\\')[0:-1]
    kicadpath = '\\'.join(pathparts)+'\\'
    verilogpath = global_args.output+'\\'
    ParseFiles(pages, kicadpath, filename)
    
    # Create netlists for each page
    LogMessage('I', "Creating netlists...")
    for page in pages:
        page.CreateNets()
        
    # Generate Verilog files
    
    for page in pages:
        #module_name = page.filename.replace('.','_')
        module_name = page.filename.split('.')[0]
        LogMessage('I', 'Writing '+module_name+'.v...')
        with open(verilogpath+module_name+'.v','w') as f:
            f.write('// Generated by kicadtoverilog.py\n\n')
            f.write('module '+ module_name + '(\n')
            for i in range(0,len(page.port_name)):
                if i != 0:
                    f.write(',\n')
                f.write('    '+page.port_type[i]+' '+page.port_name[i])
            f.write(');\n\n')
            
            f.write('    // Net definitions\n')
            wires_written = False
            for i in range(1,page.num_nets+1):
                if page.net_names[i][0:4] == 'net_':
                    f.write('    wire '+page.net_names[i]+';\n')
                    wires_written = True
            if wires_written:
                f.write('\n');
                
            # assign input ports to nets
            f.write('    // Input pins\n')
            ports_written = False
            for i in range(0,len(page.port_name)):
                if page.port_type[i] == 'input':
                    f.write('    assign ' + page.net_names[page.port_nets[i]] + ' = ' + page.port_name[i] + ';\n')
                    ports_written = True
            if ports_written:
                f.write('\n')
                
            f.write('    // Internal blocks\n')
            symbol_pins = False;
            for s in page.symbolinsts:
                f.write('    '+s.symtype+' '+s.name+'(')
                pin_written = False
                for i in range(0,len(s.pin_nets)):
                    if pin_written:
                        f.write(', ');
                    if s.symbol.pin_type[i] != 'no_connect': 
                        f.write('.'+s.symbol.pin_name[i]+'('+page.net_names[s.pin_nets[i]]+')')
                        pin_written = True
                        symbol_pins = True;
                f.write(');\n')
    
            page_pins = False
            for s in page.sheets:
                #sheet_name = s.filename.replace('.','_')
                sheet_name = s.filename.split('.')[0]
                f.write('    '+sheet_name+' '+s.instancename+'(')
                for i in range(0,len(s.pin_nets)):
                    if i!=0:
                        f.write(', ');
                    f.write('.'+s.pin_name[i]+'('+page.net_names[s.pin_nets[i]]+')')      
                    page_pins = True
                f.write(');\n')
                
            if symbol_pins or page_pins:
                f.write('\n')
                
            # assign nets to output ports
            f.write('    // Output pins\n')
            ports_written = False
            for i in range(0,len(page.port_name)):
                if page.port_type[i] == 'output':
                    f.write('    assign ' + page.port_name[i] + ' = ' + page.net_names[page.port_nets[i]] + ';\n')
                    ports_written = True
            #if ports_written:
            #    f.write('\n')
                
            f.write('endmodule\n')
            
    # Copy over synthesis file
    LogMessage('I', "Copying synthesis_defs.v...")
    shutil.copy('synthesis_defs.v',verilogpath+'synthesis_defs.v')
        
    LogMessage('I', "Done!")
        
if __name__ == "__main__":
    KicadToVerilog()

    
    
