#coding=utf-8
#服务端
from socket import *
from time import  ctime
import threading
import time
HOST="127.0.0.1"
PORT=55555
BUFSIZ=1024
ADDR = (HOST,PORT)
 
tcpSerSock=socket(AF_INET,SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)
socks=[]							 #放每个客户端的socket
ID = set()
color_number = {}
match_list = {}
sock_dict = {}
id_dict = {}
active_which = {}
heart_live={}
 
def handle():
	global ID
	while True:
		for s in socks:
			#print(s)
			try:
				size = s.recv(8).decode("utf-8")
				if(size):
					time.sleep(0.05)
					data = s.recv(int(size))
			except:		   
				continue

				
			try:
				data = data.decode("utf-8")
				order = data.split(",")
				print(order)
				
				if(order[1]=="connect_sever"):
					connect_sever(s,order)
				elif(order[2] in ID):
					if(order[1]=="change_color_number"):
						change_color_number(s,order)
					elif(order[1]=="get_new_list"):
						get_new_list(s,order)
					elif(order[1]=="choose_aim"):
						choose_aim(s,order)
					elif(order[1]=="choose_aim_answer"):
						choose_aim_answer(s,order)
					elif(order[1]=="local_paint"):
						local_paint(s,order)
					elif(order[1]=="send_msg"):
						send_msg(s,order)
					elif(order[1]=="heartbeat_check_ok"):
						heartbeat_check_ok(s,order)	
					elif(order[1]=="restart"):
						restart(s,order)
					elif(order[1]=="close_client"):
						close_client(s)
				else:
					print("ERROR ID")
			except:		   
				print("ORDER ERROR")
			
			#s.send(('[%s],%s' % (ctime(), data)).encode())	

def send_msg_with_len(s,msg):
	global socks,ID
	try:
		print(msg)
		msg = msg.encode("utf-8")
		s.send(("%08d"%len(msg)).encode("utf-8")) 
		s.send(msg)  #发送数据
	except:
		#msg = str(int(time.time()*1000))+",Internet_Error"
		#msg = msg.encode("utf-8")
		#sock_dict[match_list[id_dict[s]]].send(("%08d"%len(msg)).encode("utf-8")) 
		#sock_dict[match_list[id_dict[s]]].send(msg)  #发送数据
		
		#socks.remove(s)
		#ID.remove(id_dict[s])

		print("Internet Error")

def connect_sever(s,order):
	global ID,sock_dict,heart_live
	if order[2] in ID:
		msg = order[0]+",ID_receive,"+"ID_CANNOT_USE"
		send_msg_with_len(s,msg)
		return
	ID.add(order[2])
	heart_live[order[2]] = 2
	sock_dict[order[2]]=s
	id_dict[s] = order[2]
	msg = order[0]+",ID_receive,"+order[2]
	send_msg_with_len(s,msg)

def change_color_number(s,order):
	global color_number,match_list,sock_dict,active_which
	color_number[order[2]] = order[3]
	color_number[match_list[order[2]]] = str(1-int(order[3]))
	msg = order[0]+",color_number_receive,"+order[3]
	send_msg_with_len(s,msg)
	
	msg = order[0]+",color_number_receive,"+color_number[match_list[order[2]]]
	send_msg_with_len(sock_dict[match_list[order[2]]],msg)
	
	active_which[order[2]] = int(color_number[order[2]])
	active_which[match_list[order[2]]] = int(color_number[match_list[order[2]]])
	
	msg = order[0]+",active_which,"+str(active_which[order[2]])
	send_msg_with_len(s,msg)
	
	msg = order[0]+",active_which,"+str(active_which[match_list[order[2]]])
	send_msg_with_len(sock_dict[match_list[order[2]]],msg)

	print(active_which)

def get_new_list(s,order):
	global ID
	msg = order[0]+",get_new_list_receive"
	for i in ID:
		msg += ","+i
	send_msg_with_len(s,msg)
	

def choose_aim(s,order):
	global color_number
	try:
		color_number[order[2]] = order[4]
		msg = order[0]+",choose_aim_receive,"+"waiting"
		send_msg_with_len(s,msg)
		
		msg = order[0]+",choose_aim_sever,"+order[2]
		send_msg_with_len(sock_dict[order[3]],msg)
	except:
		print("choose_aim ERROR")

	
def choose_aim_answer(s,order):
	global match_list,sock_dict,color_number,active_which
	try:
		del match_list[match_list[id_dict[s]]]
	except:
		print("del choose_aim_answer match_list match_list ERROR")
	try:
		del match_list[id_dict[s]]
	except:
		print("del choose_aim_answer match_list ERROR")
		
	if(order[4]=="yes"):
		try:
			match_list[order[2]]=order[3]
			match_list[order[3]]=order[2]
			msg = order[0]+",choose_aim_sucess,"+order[3]
			send_msg_with_len(s,msg)
			msg = order[0]+",choose_aim_sucess,"+order[2]
			send_msg_with_len(sock_dict[order[3]],msg)
			
			color_number[order[2]]=str(1-int(color_number[match_list[order[2]]]))
			
			msg = order[0]+",color_number_receive,"+color_number[order[2]]
			send_msg_with_len(s,msg)
				
			active_which[order[2]] = int(color_number[order[2]])
			active_which[match_list[order[2]]] = int(color_number[match_list[order[2]]])
			
			msg = order[0]+",active_which,"+str(active_which[match_list[order[2]]])
			send_msg_with_len(sock_dict[order[3]],msg)
			
			msg = order[0]+",active_which,"+str(active_which[order[2]])
			send_msg_with_len(s,msg)
		except:
			msg = order[0]+",choose_aim_error"
			send_msg_with_len(s,msg)

	elif(order[4]=="no"):
		msg = order[0]+",choose_aim_denied"
		send_msg_with_len(s,msg)
	
def local_paint(s,order):
	global match_list,sock_dict,color_number,active_which
	msg = order[0]+",internet_paint,"+order[3]+","+order[4]+","+order[5]+","+order[6]+","+order[7]+","+order[8]
	send_msg_with_len(sock_dict[match_list[order[2]]],msg)
	
	active_which[order[2]] = 1-int(active_which[order[2]])
	active_which[match_list[order[2]]] = 1-int(active_which[match_list[order[2]]])
	
	msg = order[0]+",active_which,"+str(active_which[order[2]])
	send_msg_with_len(s,msg)
	
	msg = order[0]+",active_which,"+str(active_which[match_list[order[2]]])
	send_msg_with_len(sock_dict[match_list[order[2]]],msg)
	
def send_msg(s,order):
	try:
		msg = order[0]+",receive_msg,"+order[2]+","+order[3]+","+order[4]
		send_msg_with_len(sock_dict[match_list[order[2]]],msg)
	except:
		print("send_msg ERROR")

def restart(s,order):
	try:
		msg = order[0]+",internet_restart"
		send_msg_with_len(sock_dict[match_list[order[2]]],msg)
	except:
		print("restart ERROR")

def heartbeat():
	global heart_live,socks,id_dict
	while True:
		for s in socks:
			try:
				print("%s heartbeat"%id_dict[s])
				if(heart_live[id_dict[s]]==0):
					close_client(s)
					
				else:
					msg = str(int(time.time()*1000))+",heartbeat_check"
					send_msg_with_len(s,msg)
					heart_live[id_dict[s]]-=1
			except:
				print("heartbeat ERROR")
		time.sleep(10)

def heartbeat_check_ok(s,order):
	global heart_live
	print("%s heartbeat_check_ok"%id_dict[s])
	heart_live[order[2]]=2

def close_client(s):
	try:
		print("%s disconnected"%id_dict[s])
	except:
		print("print ERROR")
	try:
		socks.remove(s)
	except:
		print("del socks ERROR")
	try:
		del color_number[id_dict[s]]
	except:
		print("del color_number ERROR")
	try:
		del sock_dict[id_dict[s]]
	except:
		print("del sock_dict ERROR")
	try:
		del active_which[id_dict[s]]
	except:
		print("del active_which ERROR")
	try:
		del heart_live[id_dict[s]]
	except:
		print("del heart_live ERROR")
	try:
		del match_list[match_list[id_dict[s]]]
	except:
		print("del match_list match_list ERROR")
	try:
		del match_list[id_dict[s]]
	except:
		print("del match_list ERROR")
	try:
		ID.remove(id_dict[s])
	except:
		print("del ID ERROR")
	try:
		del id_dict[s]
	except:
		print("del id_dict ERROR")



t1 = threading.Thread(target=handle)	#子线程
t2 = threading.Thread(target=heartbeat)	#子线程



if __name__ == '__main__':
	t1.start()
	t2.start()
	print  (u'我在%s线程中 ' % threading.current_thread().name )	  #本身是主线程
	print ('waiting for connecting...')
	while True:
		clientSock,addr = tcpSerSock.accept()
		print  ('connected from:', addr)
		clientSock.setblocking(0)
		socks.append(clientSock)

 
 
