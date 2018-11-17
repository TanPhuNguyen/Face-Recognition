# file = open("ID_Name.txt", "r") 
# id= "5g5g"
# for line in file:
#     if line== id:
#         print(2)
#     else:
#         print(line[0])
 
filepath = 'ID_Name.txt'
id= "1512489"  
with open(filepath) as fp:  
   line = fp.readline()
   #cnt = 1
   #print(line)
   while line:
        #print("Line {}: {}".format(cnt, line.strip()))
        ID= line.strip()
        if ID == id:

            name= fp.readline()
            print(name.strip())
        else:
            pass
        line = fp.readline()
        #cnt += 1

