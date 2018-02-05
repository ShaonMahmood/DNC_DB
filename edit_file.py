f = open('in.txt','r')
message = f.read()
message = message.split()
for i in range(len(message)):
    message[i] += "\n"
print(message)
f.close()

message = "".join(message)
print(message)
f=open('out.txt','w')
f.write(message)
f.close()