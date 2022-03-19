struct msg
{
	bool updated;
	char content[256];
}

def send(content):
	mine.msg.content=content
	mine.msg.updated=true #send
	while(mine.msg.updated): #check if received
		delay
		detect time out:
			return false
	return true

def check():
	if(peer.msg.updated):
		ret=peer.msg.content
		peer.msg.updated=false #receive
		return ret
	else:
		return false

def listen():
	while(true):
		ret=check()
        if(ret!=false):
            return ret
        delay
		detect time out:
			return false

def get(content):
	if(not send(content)):
        return false
	return listen()

