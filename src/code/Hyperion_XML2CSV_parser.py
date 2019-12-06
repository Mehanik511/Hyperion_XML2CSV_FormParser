#author: v_volk594@mail.ru
#importing system lib for argument passing
import sys
#importing lib for encoding
import io
import encodings
#importing regexp lib
import re
#----------

#TODO: [done] Ability to read several files
#TODO: Create short code (functions and less variables)

#----------
for varFileInputFullPath in sys.argv[1:]:
    varDelimiterCSV         = ';'
    #----------
    #def WriteFile(argFileNamePostfix, argData):
    #    if not argData is None:
    #        varFileOutputName = re.split('.xml', varFileInputFullPath)[0] + '_' + argFileNamePostfix + '.xml'
    #        varFileWriteStream = open(varFileOutputName, 'w')
    #        varFileWriteStream.write(argData.group())
    #        varFileWriteStream.close()
    #        print('Data saved to ' + varFileOutputName)
    #    else:
    #        print('Data <' + argFileNamePostfix + '> doesn\'t found')
    #----------
    
    #Get file content
    with io.open(varFileInputFullPath, 'r', encoding='utf8') as f:
        varFileBody = f.read()
    
    #re.S means include newline characters in '.'
    varSearchFormBlock      = re.search('<form(.*?)>'              , varFileBody, re.S)
    varSearchColumnsBlock   = re.search('<columns(.*?)</columns>'  , varFileBody, re.S)
    varSearchRowsBlock      = re.search('<rows(.*?)</rows>'        , varFileBody, re.S)
    varSearchPagesBlock     = re.search('<pages(.*?)</pages>'      , varFileBody, re.S)
    varSearchPOVBlock       = re.search('<pov(.*?)</pov>'          , varFileBody, re.S)
    
    #WriteFile('Form'    , varSearchFormBlock)
    #WriteFile('Columns' , varSearchColumnsBlock)
    #WriteFile('Rows'    , varSearchRowsBlock)
    #WriteFile('Pages'   , varSearchPagesBlock)
    #WriteFile('POV'     , varSearchPOVBlock)
    
    
    #Getting Form name and directory
    varFormName             = re.findall(' name=\"(.*?)\"' , varSearchFormBlock.group(), re.S)[0]
    varFormDir              = re.findall(' dir=\"(.*?)\"'  , varSearchFormBlock.group(), re.S)[0]
    
    #Getting POV elements
    varArraySearchDimBlocks = re.findall('(<dimension.*?</dimension>)', varSearchPOVBlock.group(), re.S)
    
    varResultPOVString1     = ""
    varResultPOVString2     = ""
    varFoundedNameBlocks    = None
    
    for arrItem in varArraySearchDimBlocks:
        varFoundedNameBlocks = re.findall(' name=\"(.*?)\"', arrItem, re.S)
        varIndex = 0
        while varIndex < len(varFoundedNameBlocks):
            temp = varFoundedNameBlocks[varIndex].replace('&amp;','&')
            if varIndex%2 == 0:
                varResultPOVString1 += temp + varDelimiterCSV
            else:
                varResultPOVString2 += temp + varDelimiterCSV
            varIndex += 1
    del varFoundedNameBlocks
    
    varResultPOVString1 = varResultPOVString1[:-1]
    varResultPOVString2 = varResultPOVString2[:-1]
    
    
    #Getting Pages elements
    varResultPagesString1   = ""
    varResultPagesString2   = ""
    
    varArraySearchDimBlocks = re.findall('(<dimension.*?</dimension>)', varSearchPagesBlock.group(), re.S)
    
    for block in varArraySearchDimBlocks:
        varFoundedDimLine           = re.findall('<dimension(.*?) >', block, re.S)
        varFoundedDimName           = re.findall('name=\"(.*?)\"', varFoundedDimLine[0], re.S)
        varArrayFoundedFuncMembers  = re.findall('(<function.*?</function>)|(<member.*?/>)', block, re.S)
        varResultPagesString1       += varFoundedDimName[0] + varDelimiterCSV
        del varFoundedDimLine
        del varFoundedDimName
        
        #Find all members with their functions if exist
        for arrItem in varArrayFoundedFuncMembers:
            varFoundedMembers = re.findall('<member name=\"(.*?)\"', ''.join(arrItem))
            if not re.search('function', ''.join(arrItem)) is None:
                if not re.search('include', ''.join(arrItem)) is None:
                    varFoundedFunctions     = re.findall('<function include=\"true\" name=\"(.*?)\"', ''.join(arrItem))
                    varResultPagesString2   += 'I' + varFoundedFunctions[0] + '(' +  varFoundedMembers[0] + ')'
                else:
                    varFoundedFunctions     = re.findall('<function name=\"(.*?)\"', ''.join(arrItem))
                    varResultPagesString2   += varFoundedFunctions[0] + '(' +  varFoundedMembers[0] + ')'
            else:
                varResultPagesString2 += varFoundedMembers[0]
            varResultPagesString2 +=  ','
        varResultPagesString2 = varResultPagesString2[:-1] + varDelimiterCSV
    del varArraySearchDimBlocks
    varResultPagesString2 = varResultPagesString2.replace('&amp;','&')
    varResultPagesString1 = varResultPagesString1[:-1]
    varResultPagesString2 = varResultPagesString2[:-1]
    
    #Getting Rows elements
    varResultRowsString1    = ""
    varResultRowsString2    = ""
    
    varArraySearchSegmentBlocks = re.findall('(<segment>.*?</segment>)', varSearchRowsBlock.group(), re.S)
    for segment in varArraySearchSegmentBlocks:
        varArraySearchDimBlocks = re.findall('(<dimension.*?</dimension>)', segment, re.S)
        for block in varArraySearchDimBlocks:
            varFoundedDimLine           = re.findall('<dimension(.*?) >', block, re.S)
            varFoundedDimName           = re.findall('name=\"(.*?)\"', varFoundedDimLine[0], re.S)
            varArrayFoundedFuncMembers  = re.findall('(<function.*?</function>)|(<member.*?/>)', block, re.S)
            
            #IF current dimension name doesn't exist in string DO set dim name and delimiter
            if re.search(varFoundedDimName[0], varResultRowsString1) is None:
                varResultRowsString1 += varFoundedDimName[0] + varDelimiterCSV
            del varFoundedDimLine
            del varFoundedDimName
            
            #Find all members with their functions if exist
            for arrItem in varArrayFoundedFuncMembers:
                varFoundedMembers = re.findall('<member name=\"(.*?)\"', ''.join(arrItem))
                
                if not re.search('function', ''.join(arrItem)) is None:
                    if not re.search('include', ''.join(arrItem)) is None:
                        varFoundedFunctions     = re.findall('<function include=\"true\" name=\"(.*?)\"', ''.join(arrItem))
                        varResultRowsString2    += 'I' + varFoundedFunctions[0] + '(' +  varFoundedMembers[0] + ')'
                    else:
                        varFoundedFunctions     = re.findall('<function name=\"(.*?)\"', ''.join(arrItem))
                        varResultRowsString2    += varFoundedFunctions[0] + '(' +  varFoundedMembers[0] + ')'
                else:
                    varResultRowsString2 += varFoundedMembers[0]
                varResultRowsString2 +=  ','
            varResultRowsString2 = varResultRowsString2[:-1] + varDelimiterCSV
        #IF index of current item is not the last element in array DO return
        if varArraySearchSegmentBlocks.index(segment) != varArraySearchSegmentBlocks.index(varArraySearchSegmentBlocks[-1]):
            varResultRowsString2 += '\n'
    del varArraySearchSegmentBlocks
    varResultRowsString2 = varResultRowsString2.replace('&amp;','&')
    varResultRowsString1 = varResultRowsString1[:-1]
    varResultRowsString2 = varResultRowsString2[:-1]
    
    varRowItemsNumber = len(re.split(varDelimiterCSV, varResultRowsString1))
    
    
    #Getting Columns elements
    varArrayColumnsDimRows  = []
    varColumnsDimString     = ""
    varResultColumnsString  = ""
    
    varArraySearchSegmentBlocks = re.findall('(<segment>.*?</segment>)', varSearchColumnsBlock.group(), re.S)
    for segment in varArraySearchSegmentBlocks:
        varArraySearchDimBlocks = re.findall('(<dimension.*?</dimension>)', segment, re.S)
        for block in varArraySearchDimBlocks:
            varFoundedDimLine           = re.findall('<dimension(.*?) >', block, re.S)
            varFoundedDimName           = re.findall('name=\"(.*?)\"', varFoundedDimLine[0], re.S)
            varArrayFoundedFuncMembers  = re.findall('(<function.*?</function>)|(<member.*?/>)', block, re.S)
            
            #IF current dimension name doesn't exist in string DO set dim name and delimiter
            if re.search(varFoundedDimName[0], varColumnsDimString) is None:
                varColumnsDimString += varFoundedDimName[0] + varDelimiterCSV + '\n'
                varArrayColumnsDimRows.append(varFoundedDimName[0] + varDelimiterCSV)
            del varFoundedDimLine
            del varFoundedDimName
            
            #Find all members with their functions if exist
            for arrItem in varArrayFoundedFuncMembers:
                varFoundedMembers = re.findall('<member name=\"(.*?)\"', ''.join(arrItem))
                
                if not re.search('function', ''.join(arrItem)) is None:
                    if not re.search('include', ''.join(arrItem)) is None:
                        varFoundedFunctions     = re.findall('<function include=\"true\" name=\"(.*?)\"', ''.join(arrItem))
                        varResultColumnsString    += 'I' + varFoundedFunctions[0] + '(' +  varFoundedMembers[0] + ')'
                    else:
                        varFoundedFunctions     = re.findall('<function name=\"(.*?)\"', ''.join(arrItem))
                        varResultColumnsString    += varFoundedFunctions[0] + '(' +  varFoundedMembers[0] + ')'
                else:
                    varResultColumnsString += varFoundedMembers[0]
                varResultColumnsString +=  ','
            varResultColumnsString = varResultColumnsString[:-1] + varDelimiterCSV
        varResultColumnsString += varDelimiterCSV
    del varArraySearchSegmentBlocks
    varResultColumnsString = varResultColumnsString.replace('&amp;','&')
    
    #There is ';;' chars in the result string, so it's need to split string by it
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
    
    #Returns keys array from dictionary
    def DictGetKeys(dict, val):
        arr = []
        for k, v in dict.items():
            if v == val:
                arr.append(k)
        return arr
    
    varArrayResultColumns = []
    #For each dimension create result string
    for item in varArrayColumnsDimRows:
        varArrayRes = (DictGetKeys(varDictColumns, item))
        varStringRes = ""
        for x in varArrayRes:
            varStringRes += x + varDelimiterCSV
        varArrayResultColumns.append(str(item + varStringRes).replace(varDelimiterCSV+varDelimiterCSV,varDelimiterCSV))
    
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
    
    for item in varArrayResultColumns:
        for dim in re.split(varDelimiterCSV, varResultRowsString1):
            varStringResultCSV += varDelimiterCSV
        varStringResultCSV += item + '\n'
    
    varStringResultCSV += varResultRowsString1 + '\n'
    varStringResultCSV += varResultRowsString2 + '\n'
    #print('[' + varStringResultCSV + ']')
    
    varFileOutputName = re.split('.xml', varFileInputFullPath)[0] + '_parsed' + '.csv'
    #varFileWriteStream = open(varFileOutputName, 'w')
    #varFileWriteStream.write(varStringResultCSV)
    #varFileWriteStream.close()
    with io.open(varFileOutputName, 'w', encoding='cp1251') as f:
        f.write(varStringResultCSV)
    print('Data saved to ' + varFileOutputName)
    #print('Data:')
    #print(varStringResultCSV)
print('Press any key to exit...')
input()