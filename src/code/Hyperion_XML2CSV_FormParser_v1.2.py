#author: v_volk594@mail.ru
#importing system lib for argument passing
import sys
#importing lib for encoding
import io
#import encodings
#importing regexp lib
import re
#importing lib for creating XLSX-files (MS Excel)
import xlsxwriter
#----------
#Changelog
#v1.2   - Added generating output XLSX-file.
#v1.1   - Added ability to process several files; added some optimization.
#v1     - Created main functional.

#----------
#Defining global variables
varDelimiterCSV = ';'
#----------
#Defining functions
#Returns keys array from dictionary
def DictGetKeys(dict, val):
    arr = []
    for k, v in dict.items():
        if v == val:
            arr.append(k)
    return arr
#----------

for varFileInputFullPath in sys.argv[1:]:
    
    #Defining local common variables
    
    #Get file content
    with io.open(varFileInputFullPath, 'r', encoding='utf8') as f:
        varFileBody = f.read()
    
    #----- Getting main blocks of XML-file -----
    varSearchFormBlock      = ""
    varSearchColumnsBlock   = ""
    varSearchRowsBlock      = ""
    varSearchPagesBlock     = ""
    varSearchPOVBlock       = ""
    
    #re.S means include newline characters in '.'
    varSearchFormBlock      = re.search('<form.*? name=(.*?)>'          , varFileBody           , re.S)[0]
    varSearchColumnsBlock   = re.search('<columns(.*?)</columns>'       , varFileBody           , re.S)[0]
    varSearchRowsBlock      = re.search('<rows(.*?)</rows>'             , varFileBody           , re.S)[0]
    varSearchPagesBlock     = re.search('<pages(.*?)</pages>'           , varFileBody           , re.S)[0]
    varSearchPOVBlock       = re.search('<pov(.*?)</pov>'               , varFileBody           , re.S)[0]
    
    #----- Getting Form name and directory -----
    varFormName             = ""
    varFormDir              = ""
    varFormName             = re.findall(' name=\"(.*?)\"'              , varSearchFormBlock    , re.S)[0]
    varFormDir              = re.findall(' dir=\"(.*?)\"'               , varSearchFormBlock    , re.S)[0]
    
    #----- Getting POV elements -----
    varResultPOVString1     = ""
    varResultPOVString2     = ""
    varArraySearchDimBlocks = []
    varArraySearchDimBlocks = re.findall('(<dimension.*?</dimension>)'  , varSearchPOVBlock     , re.S)
    
    varFoundedNameBlocks    = []
    for block in varArraySearchDimBlocks:
        varFoundedNameBlocks = re.findall(' name=\"(.*?)\"', block, re.S)
        varIndex = 0
        while varIndex < len(varFoundedNameBlocks):
            #temp = varFoundedNameBlocks[varIndex].replace('&amp;','&')
            if varIndex%2 == 0:
                varResultPOVString1 += varFoundedNameBlocks[varIndex] + varDelimiterCSV
            else:
                varResultPOVString2 += varFoundedNameBlocks[varIndex] + varDelimiterCSV
            varIndex += 1
    del varFoundedNameBlocks
    del varArraySearchDimBlocks
    
    varResultPOVString1 = varResultPOVString1.replace('&amp;','&')
    varResultPOVString2 = varResultPOVString2.replace('&amp;','&')
    #Delete last char - delimiter
    varResultPOVString1 = varResultPOVString1[:-1]
    varResultPOVString2 = varResultPOVString2[:-1]
    
    #----- Getting Pages elements -----
    varResultPagesString1   = ""
    varResultPagesString2   = ""
    varArraySearchDimBlocks = []
    varArraySearchDimBlocks = re.findall('(<dimension.*?</dimension>)', varSearchPagesBlock, re.S)
    
    for block in varArraySearchDimBlocks:
        varFoundedDimLine           = ""
        varFoundedDimName           = ""
        varArrayFoundedFuncMembers  = []
        varFoundedDimLine           = re.findall('<dimension(.*?) >'                        , block             , re.S)[0]
        varFoundedDimName           = re.findall('name=\"(.*?)\"'                           , varFoundedDimLine , re.S)[0]
        varArrayFoundedFuncMembers  = re.findall('(<function.*?</function>)|(<member.*?/>)' , block             , re.S)
        varResultPagesString1       += varFoundedDimName + varDelimiterCSV
        del varFoundedDimLine
        del varFoundedDimName
        
        #Find all members with their functions if exist
        for arrItem in varArrayFoundedFuncMembers:
            varFoundedMembers   = ""
            varFoundedFunctions = ""
            varFoundedMembers   = re.findall('<member name=\"(.*?)\"', ''.join(arrItem))[0]
            
            #IF there is 'function' keyword
            if not re.search('function', ''.join(arrItem)) is None:
                #IF there is 'include' keyword
                if not re.search('include', ''.join(arrItem)) is None:
                    varFoundedFunctions     = re.findall('<function include=\"true\" name=\"(.*?)\"', ''.join(arrItem))[0]
                    varResultPagesString2   += 'I' + varFoundedFunctions + '(' +  varFoundedMembers + ')'
                else:
                    varFoundedFunctions     = re.findall('<function name=\"(.*?)\"', ''.join(arrItem))[0]
                    varResultPagesString2   += varFoundedFunctions + '(' +  varFoundedMembers + ')'
            else:
                varResultPagesString2 += varFoundedMembers
            varResultPagesString2 +=  ','
        varResultPagesString2 = varResultPagesString2[:-1] + varDelimiterCSV
    del varArraySearchDimBlocks
    
    varResultPagesString2 = varResultPagesString2.replace('&amp;','&')
    #Delete last char - delimiter
    varResultPagesString1 = varResultPagesString1[:-1]
    varResultPagesString2 = varResultPagesString2[:-1]
    
    #----- Getting Rows elements -----
    varResultRowsString1        = ""
    varResultRowsString2        = ""
    varArraySearchSegmentBlocks = []
    varArraySearchSegmentBlocks = re.findall('(<segment>.*?</segment>)', varSearchRowsBlock, re.S)
    
    for segment in varArraySearchSegmentBlocks:
        varArraySearchDimBlocks = []
        varArraySearchDimBlocks = re.findall('(<dimension.*?</dimension>)', segment, re.S)
        
        for block in varArraySearchDimBlocks:
            varFoundedDimLine           = ""
            varFoundedDimName           = ""
            varArrayFoundedFuncMembers  = []
            varFoundedDimLine           = re.findall('<dimension(.*?) >'                        , block             , re.S)[0]
            varFoundedDimName           = re.findall('name=\"(.*?)\"'                           , varFoundedDimLine , re.S)[0]
            varArrayFoundedFuncMembers  = re.findall('(<function.*?</function>)|(<member.*?/>)' , block             , re.S)
            
            #IF current dimension name doesn't exist in string DO set dim name and delimiter
            if re.search(varFoundedDimName, varResultRowsString1) is None:
                varResultRowsString1 += varFoundedDimName + varDelimiterCSV
            del varFoundedDimLine
            del varFoundedDimName
            
            #Find all members with their functions if exist
            for arrItem in varArrayFoundedFuncMembers:
                varFoundedMembers   = ""
                varFoundedFunctions = ""
                varFoundedMembers = re.findall('<member name=\"(.*?)\"', ''.join(arrItem))[0]
                
                #IF there is 'function' keyword
                if not re.search('function', ''.join(arrItem)) is None:
                    #IF there is 'include' keyword
                    if not re.search('include', ''.join(arrItem)) is None:
                        varFoundedFunctions     = re.findall('<function include=\"true\" name=\"(.*?)\"', ''.join(arrItem))[0]
                        varResultRowsString2    += 'I' + varFoundedFunctions + '(' +  varFoundedMembers + ')'
                    else:
                        varFoundedFunctions     = re.findall('<function name=\"(.*?)\"', ''.join(arrItem))[0]
                        varResultRowsString2    += varFoundedFunctions + '(' +  varFoundedMembers + ')'
                else:
                    varResultRowsString2 += varFoundedMembers
                varResultRowsString2 +=  ','
            #Delete last comma and add delimiter
            varResultRowsString2 = varResultRowsString2[:-1] + varDelimiterCSV
        #IF index of current item is not the last element in array DO return
        if varArraySearchSegmentBlocks.index(segment) != varArraySearchSegmentBlocks.index(varArraySearchSegmentBlocks[-1]):
            varResultRowsString2 += '\n'
    del varArraySearchSegmentBlocks
    
    varResultRowsString2 = varResultRowsString2.replace('&amp;','&')
    #Delete last char - delimiter
    #varResultRowsString1 = varResultRowsString1
    #varResultRowsString2 = varResultRowsString2
    
    #----- Getting Columns elements -----
    varArrayColumnsDimRows      = []
    varColumnsDimString         = ""
    varResultColumnsString      = ""
    varArraySearchSegmentBlocks = []
    varArraySearchSegmentBlocks = re.findall('(<segment>.*?</segment>)', varSearchColumnsBlock, re.S)
    
    for segment in varArraySearchSegmentBlocks:
        varArraySearchDimBlocks = []
        varArraySearchDimBlocks = re.findall('(<dimension.*?</dimension>)', segment, re.S)
        
        for block in varArraySearchDimBlocks:
            varFoundedDimLine           = ""
            varFoundedDimName           = ""
            varArrayFoundedFuncMembers  = []
            varFoundedDimLine           = re.findall('<dimension(.*?) >'                        , block             , re.S)[0]
            varFoundedDimName           = re.findall('name=\"(.*?)\"'                           , varFoundedDimLine , re.S)[0]
            varArrayFoundedFuncMembers  = re.findall('(<function.*?</function>)|(<member.*?/>)' , block             , re.S)
            
            #IF current dimension name doesn't exist in string DO set dim name and delimiter
            if re.search(varFoundedDimName, varColumnsDimString) is None:
                varColumnsDimString += varFoundedDimName + varDelimiterCSV + '\n'
                varArrayColumnsDimRows.append(varFoundedDimName + varDelimiterCSV)
            del varFoundedDimLine
            del varFoundedDimName
            
            #Find all members with their functions if exist
            for arrItem in varArrayFoundedFuncMembers:
                varFoundedMembers   = ""
                varFoundedFunctions = ""
                varFoundedMembers   = re.findall('<member name=\"(.*?)\"', ''.join(arrItem))[0]
                
                #IF there is 'function' keyword
                if not re.search('function', ''.join(arrItem)) is None:
                    #IF there is 'include' keyword
                    if not re.search('include', ''.join(arrItem)) is None:
                        varFoundedFunctions     = re.findall('<function include=\"true\" name=\"(.*?)\"', ''.join(arrItem))[0]
                        varResultColumnsString  += 'I' + varFoundedFunctions + '(' +  varFoundedMembers + ')'
                    else:
                        varFoundedFunctions     = re.findall('<function name=\"(.*?)\"', ''.join(arrItem))[0]
                        varResultColumnsString  += varFoundedFunctions + '(' +  varFoundedMembers + ')'
                else:
                    varResultColumnsString += varFoundedMembers
                varResultColumnsString +=  ','
            #Delete last comma and add delimiter
            varResultColumnsString = varResultColumnsString[:-1] + varDelimiterCSV
        varResultColumnsString += varDelimiterCSV
    del varArraySearchSegmentBlocks
    varResultColumnsString = varResultColumnsString.replace('&amp;','&')
    
    #There is ';;' chars in the result string, so it's need to split string by it
    varArrayColumnsSplit = []
    varArrayColumnsSplit = re.split(varDelimiterCSV + varDelimiterCSV, varResultColumnsString)
    
    #Create reversed dictionary with (VALUE:KEY)
    varDictColumns = {}
    for arrItem in varArrayColumnsSplit:
        #Create small version of original array with split by ';'
        varArrayColumnsSplitMini = []
        varArrayColumnsSplitMini = re.split(varDelimiterCSV, arrItem)
        #For each dimension names
        for dim in varArrayColumnsDimRows:
            #For each element (dimension block in each segments)
            for item in varArrayColumnsSplitMini:
                #IF index of current item equals to dimension index DO update reversed dictionary
                if varArrayColumnsSplitMini.index(item) == varArrayColumnsDimRows.index(dim):
                    varDictColumns.update({item: dim})
    del varArrayColumnsSplit
    
    #For each dimension create result string as array
    varArrayResultColumns = []
    for item in varArrayColumnsDimRows:
        varArrayKeys    = []
        varStringKeys   = ""
        varArrayKeys    = (DictGetKeys(varDictColumns, item))
        for key in varArrayKeys:
            varStringKeys += key + varDelimiterCSV
        varArrayResultColumns.append(str(item + varStringKeys).replace(varDelimiterCSV+varDelimiterCSV,varDelimiterCSV))
    
    #----- Forming result CSV-format string -----
    varStringResultCSV = varFormName + '\n'
    varStringResultCSV += varFormDir + '\n'
    varStringResultCSV += '\n'
    varStringResultCSV += '<Измерения среза>' + '\n'
    varStringResultCSV += varResultPOVString1 + '\n'
    varStringResultCSV += varResultPOVString2 + '\n'
    varStringResultCSV += '\n'
    varStringResultCSV += '<Измерения страниц>' + '\n'
    varStringResultCSV += varResultPagesString1 + '\n'
    varStringResultCSV += varResultPagesString2 + '\n'
    varStringResultCSV += '\n'
    varStringResultCSV += '<Измерения cтолбцов и строк>' + '\n'
    
    #Generate column paddings equal rows length
    for item in varArrayResultColumns:
        for dim in re.split(varDelimiterCSV, varResultRowsString1):
            if dim != '':
                varStringResultCSV += varDelimiterCSV
        varStringResultCSV += item + '\n'
    
    varStringResultCSV += varResultRowsString1 + '\n'
    varStringResultCSV += varResultRowsString2 + '\n'
    
    #----- Writing result CSV-file -----
    varFileOutputName = ""
    varFileOutputName = re.split('.xml', varFileInputFullPath)[0] + '_parsed' + '.csv'
    with io.open(varFileOutputName, 'w', encoding='cp1251') as f:
        f.write(varStringResultCSV)
    print('Data saved to ' + varFileOutputName)
    
    #----- Create result XLS-file -----
    varFileOutputName = ""
    varFileOutputName = re.split('.xml', varFileInputFullPath)[0] + '_parsed' + '.xlsx'
    
    #Create a workbook and add a worksheet
    xlsxWorkbook = xlsxwriter.Workbook(varFileOutputName)
    xlsxWorksheet = xlsxWorkbook.add_worksheet()
    
    #Some data we want to write to the worksheet
    varArrayCSVStrings = []
    #expenses = (
    #    ['Rent', 1000],
    #    ['Gas',   100],
    #    ['Food',  300],
    #    ['Gym',    50],
    #)
    
    #print('['+varStringResultCSV+']')
    varArrayCSVStrings = re.split('\n', varStringResultCSV)
    
    #Start from the first cell. Rows and columns are zero indexed.
    row = 0
    col = 0
    
    #Add a bold and italic format to use to highlight cells.
    format_Bold         = xlsxWorkbook.add_format({'bold': True})
    format_BoldItalic   = xlsxWorkbook.add_format({'bold': True, 'italic': True})
    format_ColorGray    = xlsxWorkbook.add_format({'font_color': '#808080'})
    
    #Set column width (1-50 columns has width=25)
    xlsxWorksheet.set_column(0, 50, 25)
    
    while row < len(varArrayCSVStrings):
        #print(str(row) + ':['+varArrayCSVStrings[row]+']')
        varCharIndex = 0
        col = 0
        varTemp = ""
        
        if re.search(';', str(varArrayCSVStrings[row])) is None:
            if row == 0 or row == 1:
                xlsxWorksheet.write(row, col, str(varArrayCSVStrings[row]), format_BoldItalic)
            elif row == 3 or row == 7 or row == 11:
                xlsxWorksheet.write(row, col, str(varArrayCSVStrings[row]), format_Bold)
            else:
                xlsxWorksheet.write(row, col, str(varArrayCSVStrings[row]))
        else:
            while varCharIndex < len(varArrayCSVStrings[row]):
                
                varTemp += str(varArrayCSVStrings[row])[varCharIndex]
                
                if str(varArrayCSVStrings[row])[varCharIndex] == varDelimiterCSV:
                    varTemp = varTemp.replace(varDelimiterCSV, '')
                    
                    #Set gray color to POV, Page and Rows dimensions; 12 + len = Rows dims after Columns dims (in rows)
                    if row == 4 or row == 8 or row == 12 + len(varArrayResultColumns):
                        xlsxWorksheet.write(row, col, varTemp, format_ColorGray)
                    #Set gray color to Columns dimensions
                    elif col == len(re.split(varDelimiterCSV,varResultRowsString1[:-1])) and row >= 12 and row < 12 + len(varArrayResultColumns):
                        xlsxWorksheet.write(row, col, varTemp, format_ColorGray)
                    else:
                        xlsxWorksheet.write(row, col, varTemp)
                    
                    varTemp = ""
                    col += 1
                varCharIndex += 1
        row += 1
    
    print('Data saved to ' + varFileOutputName)
    xlsxWorkbook.close()
    
print('Press any key to exit...')
input()
