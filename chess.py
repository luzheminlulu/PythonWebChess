#-*- coding=utf-8 -*-
from tkinter import *
import tkinter.messagebox
from tkinter import ttk
import socket
from time import  ctime
import threading
import time

client = socket.socket()#声明socket类型，同时生成socket连接对象
color_number = 1 #每次运行都是黑棋先走
size = 16
stop = 0
ID = ""
set_up = {}
running = 0
waiting = 1
match_sucess = 0
me_active = 0

last_chess = [0,0,0,0,0,0]

waiting_msgbox = ""

 
chess = [[0 for i in range(size+1)] for i in range(size+1)]


def send_msg_with_len(msg):
	global client
	try:
		msg = msg.encode("utf-8")
		client.send(("%08d"%len(msg)).encode("utf-8")) 
		client.send(msg)  #发送数据
	except:
		tkinter.messagebox.showinfo("错误", "网络错误")

def handle():
	global client,ping_time_label
	while True:
		try:
			size = client.recv(8)	  #到这里程序继续向下执行
			time.sleep(0.05)
			data = client.recv(int(size.decode("utf-8")))
		except:
			data = "ERROR"
			continue
		if not data:
			print("no data")
			continue
		
		data = data.decode()
		order = data.split(",")
		print(order)
		ping_time_label["text"] = "ping:"+str(int(time.time()*1000)-int(order[0]))
			
		if(order[1]=="ID_receive"):
			ID_receive(order)
		elif(order[1]=="color_number_receive"):
			color_number_receive(order)
		elif(order[1]=="get_new_list_receive"):	
			get_new_list_receive(order)
		elif(order[1]=="choose_aim_receive"):	
			choose_aim_receive(order)	
		elif(order[1]=="choose_aim_sever"):	
			choose_aim_sever(order)	
		elif(order[1]=="choose_aim_sucess"):	
			choose_aim_sucess(order)	
		elif(order[1]=="choose_aim_denied"):	
			choose_aim_denied(order)
		elif(order[1]=="active_which"):	
			active_which(order)
		elif(order[1]=="internet_paint"):	
			internet_paint(order)
		elif(order[1]=="receive_msg"):
			receive_msg(order)
		elif(order[1]=="heartbeat_check"):
			heartbeat_check(order)
		elif(order[1]=="internet_restart"):
			internet_restart(order)
			
			
def heartbeat_check(order):
	msg = order[0]+",heartbeat_check_ok,"+ID
	send_msg_with_len(msg)

			
def ID_receive(order):
	global client,connect_label
	
	if(order[2]=="ID_CANNOT_USE"):
		connect_label["text"]="连接失败"
		tkinter.messagebox.showinfo("错误", "昵称无法使用")
	else:
		connect_label["text"]="连接成功"

def color_number_receive(order):
	global client,color_number
	color_number = int(order[2])
	show_color_number()

def get_new_list_receive(order):
	global comboxlist
		
	if(len(order)>2):
		comboxlist["values"] = ("请选择对手",)
		for i in range(2,len(order)):
			if(order[i] != ID):
				comboxlist["values"] = comboxlist["values"]+(order[i],)
	else:
		comboxlist["values"] = ("请选择对手",)
	
def choose_aim_receive(order):

	print("choose_aim_receive")
	
def choose_aim_sever(order):
	get_new_list()
	ans=tkinter.messagebox.askokcancel('提示', order[2]+"正在请求连接")
	print(ans)
	
	if(ans):
		msg = str(int(time.time()*1000))+",choose_aim_answer,"+ID+","+order[2]+",yes"
	else:
		msg = str(int(time.time()*1000))+",choose_aim_answer,"+ID+","+order[2]+",no"
	send_msg_with_len(msg)
		
def choose_aim_sucess(order):
	global match_sucess,waiting,waiting_msgbox,comboxlist

	waiting_msgbox["text"]="正在对战"
	comboxlist.current(comboxlist["values"].index(order[2]))  #选择第2个
	
	print("match success")
	match_sucess = 1
	waiting =0
	
	
def choose_aim_denied(order):
	global waiting_msgbox
	waiting_msgbox["text"]="对方拒绝了你"
	tkinter.messagebox.showinfo("提示", "对方拒绝了你")


def active_which(order):
	global me_active
	if (order[2]=="1"):
		me_active = 1
	elif (order[2]=="0"):
		me_active = 0
	else:
		print("active ERROR")
	
	
def internet_paint(order):
	global me_active,running,last_chess
	if(me_active==0):
		if(running==1):
			if color_number == 1:
				canvas.create_oval(last_chess[0],last_chess[1],last_chess[2],last_chess[3], fill="black",tags = "oval")
			elif color_number == 0:
				canvas.create_oval(last_chess[0],last_chess[1],last_chess[2],last_chess[3], fill="white",tags = "oval")

		running = 1
		last_chess[0] = int(order[2])
		last_chess[1] = int(order[3])
		last_chess[2] = int(order[4])
		last_chess[3] = int(order[5])
		last_chess[4] = int(order[6])
		last_chess[5] = int(order[7])
		
		if color_number == 1:
			canvas.create_oval(last_chess[0],last_chess[1],last_chess[2],last_chess[3], fill="white",tags = "oval")
			draw_x(last_chess[0],last_chess[1],last_chess[2],last_chess[3],1)
			chess[last_chess[4]][last_chess[5]] = 2
		elif color_number == 0:
			canvas.create_oval(last_chess[0],last_chess[1],last_chess[2],last_chess[3], fill="black",tags = "oval")
			draw_x(last_chess[0],last_chess[1],last_chess[2],last_chess[3],1)
			chess[last_chess[4]][last_chess[5]] = 1
		gameover(last_chess[4],last_chess[5])
	else:
		print("internet_paint ERROR")
	
def receive_msg(order):
	global msg_text
	msg_text.configure(state='normal')
	msg_text.insert('end', order[2]+" "+order[3]+"\n"+order[4]+"\n")
	msg_text.configure(state='disabled')
	msg_text.see("end")




t = threading.Thread(target=handle)				#子线程



def paint(event):
	global color_number,running,waiting,running_2,me_active
	#让棋子下在棋盘点上
	if(waiting==1):
		return
	if(me_active==0):
		return
	if event.x % 30 > 15 :
		event.x = event.x//30 + 1 
	else:
		event.x = event.x // 30
	if event.y % 30 > 15:
		event.y = event.y // 30 + 1
	else:
		event.y = event.y//30
	#边缘检测  
	if((event.x > size+5) | (event.y > size+5) | (event.x < 0) | (event.y < 0)):
		return

	
	if event.x > size:
		event.x = size
	if event.y > size:
		event.y = size
	if event.x < 1:
		event.x = 1
	if event.y < 1:
		event.y = 1
	#确定下棋坐标
	x1, y1 = (event.x*30 - 15), (event.y*30 - 15)
	x2, y2 = (event.x*30 + 15), (event.y*30 + 15)

	if stop == 0:
		print(event.x)
		print(event.y)
		if chess[event.x][event.y] == 0: 
			print(event.x)
			print(event.y)
			if(running==1):
				if color_number == 1:
					canvas.create_oval(last_chess[0],last_chess[1],last_chess[2],last_chess[3], fill="white",tags = "oval")
				elif color_number == 0:
					canvas.create_oval(last_chess[0],last_chess[1],last_chess[2],last_chess[3], fill="black",tags = "oval")
			running = 1
			last_chess[0] = x1
			last_chess[1] = y1
			last_chess[2] = x2
			last_chess[3] = y2
			last_chess[4] = event.x
			last_chess[5] = event.y
			if color_number == 1:
				canvas.create_oval(x1, y1, x2, y2, fill="black",tags = "oval")
				draw_x(x1, y1, x2, y2, 0)
				chess[event.x][event.y] = 1
			elif color_number == 0:
				canvas.create_oval(x1, y1, x2, y2, fill="white",tags = "oval")
				draw_x(x1, y1, x2, y2, 0)
				chess[event.x][event.y] = 2
			me_active=0
			msg = str(int(time.time()*1000))+",local_paint,"+ID+","+str(x1)+","+str(y1)+","+str(x2)+","+str(y2)+","+str(event.x)+","+str(event.y)
			send_msg_with_len(msg)
			gameover(event.x,event.y)
			

def draw_x(x1, y1, x2, y2, which):
	global color_number,canvas
	if((color_number == 0 and which ==0) or  (color_number == 1 and which ==1)): #白棋
		canvas.create_line(x1+10,(y1+y2)/2,x2-10,(y1+y2)/2,fill='black',width=2,tags="xxx")
		canvas.create_line((x1+x2)/2,y1+10,(x1+x2)/2,y2-10,fill='black',width=2,tags="xxx")
	elif((color_number == 1 and which ==0) or  (color_number == 0 and which ==1)): #黑棋
		canvas.create_line(x1+10,(y1+y2)/2,x2-10,(y1+y2)/2,fill='white',width=2,tags="xxx")
		canvas.create_line((x1+x2)/2,y1+10,(x1+x2)/2,y2-10,fill='white',width=2,tags="xxx")
			
def wininfo(chess): #提示窗口
	global stop
	stop = 1
	if(chess==1):
		tkinter.messagebox.showinfo("结束", "黑棋赢啦")
	elif(chess==2):
		tkinter.messagebox.showinfo("结束", "白棋赢啦")
	
			
def gameover(xx, yy):
   
	count = 0
	for i in range(xx + 1, 17):	 #向右搜索
		if chess[i][yy] == chess[xx][yy]:
			count += 1
		else:
			break
	for i in range(xx, 0, -1):	 #向左搜索
		if chess[i][yy] == chess[xx][yy]:
			count += 1
		else:
			break
	if count == 5:
		wininfo(chess[xx][yy])
	count = 0

	for i in range(yy + 1, 17):	 #向下搜索
		if chess[xx][i] == chess[xx][yy]:
			count += 1
		else:
			break
	for i in range(yy, 0, -1):	 #向上搜索
		if chess[xx][i] == chess[xx][yy]:
			count += 1
		else:
			break
	if count == 5:
		wininfo(chess[xx][yy])
	count = 0

	for i, j in zip(range(xx+1, 17), range(yy+1, 17)):	#向右下搜索
		if chess[i][j] == chess[xx][yy]:
			count += 1
		else:
			break
	for i, j in zip(range(xx, 0, -1), range(yy, 0, -1)):#向左上搜索
		if chess[i][j] == chess[xx][yy]:
			count += 1
		else:
			break
	if count == 5:
		wininfo(chess[xx][yy])
	count = 0

	for i, j in zip(range(xx - 1, 0, -1), range(yy + 1, 17)): #向左下搜索
		if chess[i][j] == chess[xx][yy]:
			count += 1
		else:
			break
	for i, j in zip(range(xx, 17), range(yy, 0, -1)):	 #向右上搜索
		if chess[i][j] == chess[xx][yy]:
			count += 1
		else:
			break
	if count == 5:
		wininfo(chess[xx][yy])
	count = 0
	

def restart():
	global canvas,size,stop,running,me_active,last_chess
	msg = str(int(time.time()*1000))+",restart,"+ID
	send_msg_with_len(msg)
	canvas.delete("oval")
	canvas.delete("xxx")
	for i in range(size+1):
		for j in range(size+1):
			chess[i][j] = 0
	stop = 0
	running = 0
	last_chess = [0,0,0,0,0,0]
	change_color_number()
	print(chess)
	
def internet_restart(order):
	global canvas,size,stop,running,me_active,last_chess
	canvas.delete("oval")
	canvas.delete("xxx")
	for i in range(size+1):
		for j in range(size+1):
			chess[i][j] = 0
	stop = 0
	running = 0
	last_chess = [0,0,0,0,0,0]
	print(chess)

def connect_sever():
	global ID,client,connect_label
	connect_label["text"]="连接中"
	try:
		#client.connect(("gn25896538.qicp.vip",51683))
		client.connect(("127.0.0.1",55555))
		#client.connect(("312265bv87.picp.vip",12370))
	except:
		print("Connect Error")
	
	ID = connect_sever_text.get('0.0', 'end')[:-1]
	
	#file = open('dict.txt', 'w') 
	## 遍历字典的元素，将每项元素的key和value分拆组成字符串，注意添加分隔符和换行符
	#for k,v in dict_temp.items():
	#	file.write(str(k)+'='+str(v)+'\n')
	#file.close()
	
	msg = str(int(time.time()*1000))+",connect_sever,"+ID
	send_msg_with_len(msg)
	print(msg)
	get_new_list()
	
	
def change_color_number():
	global running,color_number,match_sucess
	if(match_sucess == 0):
		color_number = 1-color_number
		show_color_number()
	elif(running==0):
		if(color_number==0):
			msg = str(int(time.time()*1000))+",change_color_number,"+ID+","+"1"
		elif(color_number==1):
			msg = str(int(time.time()*1000))+",change_color_number,"+ID+","+"0"
		send_msg_with_len(msg)
		print(msg)
	else:
		print("CANNOT_CHANGE")
		return

def show_color_number():
	global color_number,color_number_label

	if(color_number==0):
		color_number_label["text"] = "白子"
		black_white_button["text"] = "执黑"
	elif(color_number==1):
		color_number_label["text"] = "黑子"
		black_white_button["text"] = "执白"
		
def choose_aim():
	global waiting_msgbox,top
	choose_aim=comboxlist.get()
	if(choose_aim=="请选择对手"):
		tkinter.messagebox.showinfo("", "请选择对手")
		return
	else:
		msg = str(int(time.time()*1000))+",choose_aim,"+ID+","+choose_aim+","+str(color_number)
		send_msg_with_len(msg)
		waiting_msgbox["text"]="正在邀请..."

		print(msg)

def get_new_list():
	msg = str(int(time.time()*1000))+",get_new_list,"+ID
	send_msg_with_len(msg)
	print(msg)

def send_msg():
	global msg_text

	strftime = time.strftime('%H:%M:%S')
	msg_get = send_msg_text.get('0.0', 'end')
	print(msg_get)
	msg = str(int(time.time()*1000))+",send_msg,"+ID+","+strftime+","+msg_get
	send_msg_text.delete('0.0', 'end')
	send_msg_with_len(msg)
	
	msg_text.configure(state='normal')
	msg_text.insert('end', ID+" "+strftime+"\n"+msg_get+"\n")
	msg_text.configure(state='disabled')
	msg_text.see("end")

def close_client():
	client.close()
	stop = 0
	ID = ""
	running = 0
	waiting = 1
	match_sucess = 0
	me_active = 0

if __name__ == '__main__':
	x_start=500
	y_start=5
	top = Tk()
	top.title("五子棋")
	top.geometry("700x525")
	
	t.start()

	## 打开文本文件
	#file = open('setup.ini','r')
	#
	## 遍历文本文件的每一行，strip可以移除字符串头尾指定的字符（默认为空格或换行符）或字符序列
	#for line in file.readlines():
	#    line = line.strip()
	#    k = line.split('=')[0]
	#    v = line.split('=')[1]
	#    set_up[k] = v
	#
	## 依旧是关闭文件
	#f.close()
	#
	##  可以打印出来瞅瞅
	#print(set_up)
	
	
	
	canvas = Canvas(top, width=500, height=500)
	canvas.pack(expand=YES, fill=BOTH)
	canvas.bind("<Button-1>",paint)#每次点击鼠标左键（事件）,触发paint函数
	
	
	
	
	for num in range(1, 17):
		canvas.create_line(num*30, 30, 
							num*30, 480,
							width=2)
							
	for num in range(1, 17):
		canvas.create_line(30, num*30,
							480, num*30, 
							width=2)
							
	restart_button = Button(top,text ="RESTART",command=restart)
	restart_button.place(x=550,y=500)
	
	
	addr_label = Label(top, text='地址:')
	port_label = Label(top, text='端口:')
	addr_text = Text(top,height=1, width=10)
	addr_text.insert('0.0',"gn25896538.qicp.vip")
	port_text = Text(top,height=1, width=10)
	port_text.insert('0.0',"55555")
	addr_label.place(x=500,y=0)
	addr_text.place(x=550,y=0)
	port_label.place(x=500,y=10)
	port_text.place(x=550,y=10)
	
	
	
	#Text服务器地址: text="gn25896538.qicp.vip"
	#Text端口: text="51683"
	
	ping_time_label = Label(top, text='ping:uknow')
	ping_time_label.place(x=x_start,y=y_start+20)
	connect_sever_label = Label(top, text='昵称:')
	connect_sever_text	= Text(top, height=1, width=16)
	connect_sever_text.insert('0.0', "请输入昵称")
	connect_sever_button = Button(top, text='连接服务器', command=connect_sever,bg="red",fg="white")
	
	connect_sever_label.place(x=x_start,y=y_start+40)
	connect_sever_text.place(x=x_start+50,y=y_start+40)
	connect_sever_button.place(x=550,y=70)
	
	connect_label = Label(top, text='')
	connect_label.place(x=500,y=50)

	
	comboxlist=ttk.Combobox(top) #初始化	 
	comboxlist["values"]=("请选择对手",)
	#comboxlist.bind("<<ComboboxSelected>>",change_search_mode)
	comboxlist.current(0)  #选择第0个	
	comboxlist.place(x=500,y=110)
		
	choose_aim_button = Button(top, text='对战', command=choose_aim)
	choose_aim_button.place(x=500,y=130)
	get_new_list_button = Button(top, text='刷新', command=get_new_list)
	get_new_list_button.place(x=550,y=130)
	
	waiting_msgbox = Label(top, text='')
	waiting_msgbox.place(x=500,y=160)
	
	color_number_label = Label(top, text='黑子')
	black_white_button = Button(top, text='执白', command=change_color_number)
	color_number_label.place(x=500,y=180)
	black_white_button.place(x=580,y=180)
	
	show_color_number()
	
	msg_text = Text(top,height=15, width=25)
	msg_text.configure(state='disabled')
	msg_text.place(x=500,y=220)
	
	send_msg_text = Text(top,height=2, width=20)
	send_msg_text.place(x=500,y=450)
	
	send_msg_button = Button(top, text='发送', command=send_msg)
	send_msg_button.place(x=620,y=450)
	
	close_button = Button(top, text='断开', command=close_client)
	close_button.place(x=600,y=130)
	
	top.mainloop()








