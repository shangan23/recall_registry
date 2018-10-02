import csv,re,time,sys,xlrd,os
skip_lines = range(1, 12)  # the range is zero-indexed
page = re.compile(r'\page\s[0-9]')
zipcode9 = re.compile(r'(\d{5}(:?[-\s]?)\d{4})')
zipcode5 = re.compile(r'(\d{5}(\-\d{4})?)')
filepath = '/opt/recall_registry/fileupload/'
filename = sys.argv[1]
ngname = sys.argv[2]

print "xls file :" + filename
print "csv file :" + ngname

xlsfilepath = filepath + filename
basename = os.path.splitext(os.path.basename(xlsfilepath))[0]

"""
Generating csv from XLS
"""
wb = xlrd.open_workbook(xlsfilepath)
sh = wb.sheet_by_index(0)
csvfile = open(filepath + basename +'.csv','wb')
wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

for rownum in xrange(sh.nrows):
    wr.writerow(sh.row_values(rownum))

csvfile.close()

filename = basename +'.csv'

outfilename = 'output_' + filename
infilepath = filepath + filename
outfilepath = filepath + outfilename
ngfilepath = filepath + ngname

emptyline = ["","","","","","","","","","","","","",""]
pat = {}
addr = {}
addrlist = []
patlist = []
final = []
downloadfilepath = filepath + 'final_' + filename

print 'input file --> ' + infilepath
print ''
print 'processed file --> ' + outfilepath
print ''
print 'final file --> ' + downloadfilepath
print ''
"""
Cleansing the CSV input file
"""

with open(infilepath) as f_in, open(outfilepath, "w") as f_out:
    current_line = 0  # keep a line counter
    for line in f_in:  # read the input file line by line
        if current_line not in skip_lines:
            if "Recall Report" not in line and "Last Name" not in line and "First Name" not in line and "Total Patients:" not in line:
                if len(page.findall(line.strip().replace(",",""))) == 0:
                    if line.strip() != '"","","","","","","","","","","","","",""': # ignore empty line
                        f_out.write(line)  # not in our skip range, write the line
        current_line += 1  # increase the line counter


"""
Add empty line if address line and address are empty
"""
with open(outfilepath) as fin:
    c_line = 1  # keep a line counter
    emptyfound = False
    red = list(csv.reader(fin))
    for rd in red:  # read the input file line by line
        if c_line % 2 == 0 and rd[3] != '':
            red.insert(c_line-1, emptyline)
            emptyfound = True
        c_line += 1  # increase the line counter

if emptyfound == True:
    with open(outfilepath, 'w') as outfile:
        wrt = csv.writer(outfile)
        for line in red:
            wrt.writerow(line)

fileo =  open(outfilepath, 'rb')
reader = csv.reader(fileo)
i = 1
for l in reader:
    if i % 2 == 0:
        #''.join(l[0:8]) == '' and ''.join(l[10:12]) == '':
        zipcode = ''
        address = l[9]

        if address.find(',') != -1:
            address = address.split(',')
            addr['city'] = address[0].strip()
            state_zip = address[1]
        else:
            addr['city'] = ' '
            state_zip = address

        zipcode5check =  zipcode5.findall(state_zip)[0][0] if len(zipcode5.findall(state_zip))>0 else ''
        zipcode9check = zipcode9.findall(state_zip)[0][0] if len(zipcode9.findall(state_zip))>0 else ''

        if zipcode5check != '':
            zipcode = zipcode5check
        
        if zipcode9check !='':
            zipcode = zipcode9check
            #zipcode = zipcode9check[:5]

        if zipcode != '':
            state = state_zip.replace(zipcode,'')
        else:
            state = state_zip.strip()

        addr['state'] = state
        addr['zipcode'] = zipcode[:5] if zipcode != '' else zipcode
        if address == '':
            addr = {'city':' ','state':' ','zipcode':' '}
        addrlist.append(dict(addr))
    else:
        pat['name'] = l[5] + ' ' + l[3]
        pat['phone']  =  l[11].strip().replace(' ','') if l[11] != '' else l[11].strip().replace(' ','')
        pat['address_line'] = l[9]
        pat['mrn'] = l[13]
        patlist.append(dict(pat))
    i += 1

"""
Final output csv with desired output
"""

with open(downloadfilepath, 'w') as csvfile:
    fieldnames = ['name','address_line', 'city', 'state', 'zipcode','phone','age_in_month','msg_name','mrn']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    k = 0
    for r in patlist:
        mrn_found = 0
        if r['mrn'] != '':
            with open(ngfilepath) as ng:
                for mrn in csv.reader(ng):
                    if mrn[0] == r['mrn']:
                        mrn_found = 1
                        break
        if mrn_found == 1 or r['mrn'] == '':
            writer.writerow({'name': r['name'], 'address_line': r['address_line'], 'city': addrlist[k]['city'], 'state': addrlist[k]['state'], 'zipcode': addrlist[k]['zipcode'], 'phone': r['phone'], 'age_in_month': 8, 'msg_name':'Missed Dose','mrn':r['mrn']})
            k += 1

skprecord = len(addrlist) - k

print 'Processing completed'
print 'address'
print  len(addrlist)
print 'patient'
print len(patlist)
print 'processed record'
print k
print 'skipped record'
print skprecord
print '------------- end -------------'
print ''
