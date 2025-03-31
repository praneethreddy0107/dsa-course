from sys import argv
sum=0
args=argv[1:]
for x in args:
    sum=sum+int(x)
print(sum)