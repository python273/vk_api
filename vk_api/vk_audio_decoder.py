# -*- coding: utf-8 -*-
vk_str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN0PQRSTUVWXYZO123456789+/="


def decode(string):
    vals = string.split("?extra=")[1].split("#")
    tstr = vk_o(vals[0])
    ops = vk_o(vals[1])
    ops_arr = ops.split(chr(9))
    llen = len(ops_arr)
    i = llen - 1
    while i >= 0:
        args_arr = ops_arr[i].split(chr(11))
        op_ind = args_arr.pop(0)
        if op_ind == 'v':
            tstr = vk_v(tstr)
        elif op_ind == 'r':
            tstr = vk_r(tstr, args_arr[0])
        elif op_ind == 'x':
            tstr = vk_x(tstr, args_arr[0])
        i -= 1
    return tstr


def vk_o(string):
    global vk_str
    llen = len(string)
    result = ""
    s = 0
    index2 = 0
    while s < llen:
        sym_index = vk_str.find(string[s])
        if sym_index != -1:
            if index2 % 4 != 0:
                i = (i << 6) + sym_index
            else:
                i = sym_index
            if index2 % 4 != 0:
                index2 += 1
                shift = -2 * index2 & 6
                result += chr(0xFF & (i >> shift))
            else:
                index2 += 1
        s += 1
    return result


def vk_v(string):
    return string[::-1]


def vk_r(string, i):
    global vk_str
    vk_str2 = vk_str + vk_str
    vk_str2_len = len(vk_str2)
    llen = len(string)
    result = ""
    s = 0
    while s < llen:
        index = vk_str2.find(string[s])
        if index != -1:
            offset = index-int(i)
            if offset < 0:
                offset += vk_str2_len
            result += vk_str2[offset]
        else:
            result += string[s]
        s += 1
    return result


def vk_x(string, i):
    xor_val = ord(i[0])
    str_len = len(string)
    result = ""
    i = 0
    while i < str_len:
        result += chr(ord(string[i]) ^ xor_val)
        i += 1
    return result
