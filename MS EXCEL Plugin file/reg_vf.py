# !/usr/bin/env python3
# -*- coding: latin-1 -*-

# Importing Libraries
import string
import os
import time
import sys
from struct import *
import pdb
import socket
import xlwings as xw
#####################################################

class APB(object):
	WRITE=0
	READ=1	
	IDLE=2
	DONE=3
	WRITE_RSP=4
	READ_RSP=5
	IDLE_RSP=6
	DONE_RSP=7
	ids = []
	HOSTPy2D = '192.168.1.41'
	PORT_APB= 4201

# Passing data to APB testbench
	def __init__(self,address = 0,data = 0,id = 0, version = 1):
		self.id=id
		self.version=version
		self.address = address
		self.data = data

# Establishing TCP IP connection
	def open_socket_conn(self):
		global SOCKETPY2D
		global conn_PY2D
		SOCKETPY2D = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		SOCKETPY2D.bind((self.HOSTPy2D,self.PORT_APB))
		SOCKETPY2D.listen(5)
		conn_PY2D, addr_PY2D = SOCKETPY2D.accept()

# Writing data to fifo and sending to TB
	def write(self,address,data):
		# pdb.set_trace()
		address = int(str(address))
		pkt_len = 16
		endian = 0x0f
		op = self.WRITE
		data_len = 4
		request = pack("=BIHIBIIQI",endian,pkt_len,self.version,self.id,op,0,data_len,address,data)
		request = request.decode(encoding='Latin-1')
		request = bytes(request,'Latin-1')
		conn_PY2D.sendall(request)
		self.id += 1
		time.sleep(1)
		read_value = conn_PY2D.recv(1024)
		read_value = str(hex(data))
		return read_value

# Reading data from fifo
	def read(self,address):
		address = int(str(address))
		pkt_len=12
		endian=0x0f
		op =self.READ
		data_len =0
		request = pack("=BIHIBIIQ",endian,pkt_len,self.version,self.id,op,0,data_len,address)
		request = request.decode(encoding='Latin-1')
		request = bytes(request,'Latin-1')
		conn_PY2D.sendall(request)
		self.id += 1
		time.sleep(1)
		read_value = conn_PY2D.recv(16)
		endian, pkt_len, self.version, self.id, op, status = unpack("=BIHIBI",read_value)
		read_value = conn_PY2D.recv(16)
		# read_value = read_value.encode(encoding='Latin-1')
		data_len, address, data = unpack("=IQI",read_value)
		read_value = str(hex(data))
		return read_value

# Exiting Simulation and Closing fifos
	def ctrl_command(self):
		pkt_len = 0;
		endian=0x0f;
		op = self.DONE;
		request = pack("=BIHIB",endian,pkt_len,self.version,self.id, op)
		request = request.decode(encoding='Latin-1')
		request = bytes(request,'Latin-1')
		conn_PY2D.sendall(request)
		SOCKETPY2D.close()
		self.id += 1
flag = True

# Writing Value
def write_val(addr,data):
	global flag
	mm = APB()
	if flag == True:
		mm.open_socket_conn()
		flag = False
	data = mm.write(addr,data)
	return data

# Reading Value
def read_val(addr):
	global flag
	mm = APB()
	if flag == True:
		mm.open_socket_conn()
		flag = False
	data = mm.read(addr)
	return data
@xw.func
#Exiting Simulation
def exit_sim():
	mm = APB()
	mm.ctrl_command()
	mm.ctrl_command()

#Getting the currently referenced field
def get_field():
	ar = []
	for val in range(m1,m2+1):
		cell = tuple((n1,val))
		num = xw.Range(cell).value
		ar.append(num)
	return ar

#Getting all the fields of Register
def get_fields(ar):	
	field_ar = []
	rw = n1+1
	fg =True
	while fg == True:
		f_cell = tuple((rw,m1))
		f_name = xw.Range(f_cell).value
		field_temp = []
		if f_name != None:
			f_name = f_name.lower()
			if f_name[0:5] == 'field':
				for v in range(m1,m2+1):
					f_cell_temp = tuple((rw,v))
					f_data = xw.Range(f_cell_temp).value
					field_temp.append(f_data)
				field_ar.append(field_temp)	
			else: 
				fg = False
			rw += 1
		else:
			fg = False
	return field_ar
@xw.func
#Function for writing data to a register or field
def reg_write(cell_range,caller):
	global n1,m1,m2,wb,s
	wb = xw.Book()
	s = wb.sheets.active  # in active book
	n1 = caller.row
	m1 = 1
	m2 = 8
	ar = get_field()
	#################################################
	# Checking if cell is valid
	if ar[0] == None:
		return 'INVALID FIELD'
	else:
		if ar[0].lower()[0:8] == 'register':
			field_ar = get_fields(ar)
			a = 'RO' in str(field_ar)
			if a == True:
				return 'RO fields present, write to reg not permitted'
			else:
				addr = int(str(ar[2]),16)
				data  = int(ar[7])
				write_data = write_val(addr,data)
				if write_data == str(hex(data)):
					return 'DONE' 
				else:
					return "Data Write Failed" 
		#############################################
		elif ar[0].lower()[0:5] == 'field':
			a = 'RO' in  str(ar)
			if a == True:
				return 'RO field, cannot write'
			else:
				data  = int(ar[7])
				fg = True
				i = n1-1
				while fg == True:
					# pdb.set_trace()
					cell = tuple((i,m1+2))
					val = xw.Range(cell).value
					reg_cell = tuple((i,m1))
					reg_name = xw.Range(reg_cell).value
					if (val != None and reg_name.lower() == 'register'):
						addr = int(val,16)
						fg = False
					else:
						i -= 1
				read_data = read_val(addr)
				read_data = "{0:032b}".format(int(read_data, 16))
				if len(str(ar[4])) <= 4 :
					end = 32 - int(ar[4])
					data = list(bin(data).lstrip('0b'))
					temp_data = list(read_data)
					if len(data) == 0:
						temp_data[end-1] = '0'
					else:
						temp_data[end-1] = data[0]
					read_data = "".join(temp_data)
					read_data = int(read_data,2)
					write_data = write_val(addr,read_data)
					if write_data == str(hex(read_data)):
						return 'DONE'
					else:
						return "Write Failed"

				else:
					st1 = (ar[4].strip('[]')).split(':')
					start = 32 - int(st1[0])
					end = 32 - int(st1[1])
					data_bin = bin(data).lstrip('0b')
					data_bin = '0'*(end-start+1-len(data_bin)) + data_bin
					data = list(data_bin)
					temp_data = list(read_data)
					temp_data[start-1:end] = data
					read_data = "".join(temp_data)
					read_data = int(read_data,2)
					write_data = write_val(addr,read_data)
					if write_data == str(hex(read_data)):
						return 'DONE'
					else:
						return "Write Failed"
		else:
			return "INVALID FIELD"
@xw.func
#Function for reading data from a register or field
def reg_read(cell_range,caller):
	global n1,m1,m2,wb,s
	wb = xw.Book()
	s = wb.sheets.active  # in active book
	n1 = caller.row
	m1 = 1
	m2 = 8
	ar = get_field()
	####################################################
	#checking if field is valid
	if ar[0] == None:
		return 'INVALID FIELD'
	else:
		if ar[0].lower()[0:8] == 'register':
			field_ar = get_fields(ar)
			a = 'WO' in str(field_ar)
			if a == True:
				return 'WO fields present, read not permitted'
			else:
				addr = int(str(ar[2]),16)
				read_data = read_val(addr)
				return 'DATA: ' + str(int(read_data,16))
		################################################
		elif ar[0].lower()[0:5] == 'field':
			a = 'WO' in  str(ar)
			if a == True:
				return 'WO field, cannot read'
			else:
				fg = True
				i = n1-1
				while fg == True:
					cell = tuple((i,m1+2))
					val = xw.Range(cell).value
					reg_cell = tuple((i,m1))
					reg_name = xw.Range(reg_cell).value
					if (val != None and reg_name.lower() == 'register'):
						addr = int(val,16)
						fg = False
					else:
						i -= 1
				read_data = read_val(addr)
				read_data = "{0:032b}".format(int(read_data, 16))
				# Getting the data in the given field
				if len(str(ar[4])) <= 4 :
					end = 32 - int(ar[4])
					temp_data = list(read_data)
					data = temp_data[end-1] 
					read_data = "".join(data)
					read_data = int(read_data,2)
					return 'DATA: '+str(read_data)

				else:
					st1 = (ar[4].strip('[]')).split(':')
					start = 32 - int(st1[0])
					end = 32 - int(st1[1])
					# print start, end
					temp_data = list(read_data)
					data = temp_data[start-1:end]
					read_data = "".join(data)
					read_data = int(read_data,2)
					return 'DATA: '+ str(read_data)
		else:
			return 'INVALID FIELD'