# -*- coding: utf-8 -*-
from .exceptions import VkAudioUrlDecodeError

VK_STR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN0PQRSTUVWXYZO123456789+/="

def logical_xor(a, b):
    if bool(a) == bool(b):
        return False
    else:
        return a or b

def splice(l, a, b, c):
    """ JS's Array.prototype.splice

    var x = [1, 2, 3],
        y = x.splice(0, 2, 1337);

    eq

    x = [1, 2, 3]
    x, y = splice(x, 0, 2, 1337)
    """

    return l[:a] + [c] + l[a + b:], l[a:a + b]


def decode_audio_url(string,user_id):
    vals = string.split("?extra=", 1)[1].split("#")

    tstr = vk_o(vals[0])
    ops_list = vk_o(vals[1]).split('\x09')[::-1]

    for op_data in ops_list:
        benis = op_data.split('\x0b')
	if len(benis) == 2:
		cmd = benis[0]
		arg = [benis[1]]
	if len(benis) == 1:
		cmd = benis[0]
		arg = []

        if cmd == 'v':
            tstr = tstr[::-1]

        elif cmd == 'r':
            tstr = vk_r(tstr, arg[0])

        elif cmd == 'x':
            tstr = vk_xor(tstr, arg[0])
        elif cmd == 's':
            tstr = vk_s(tstr, arg[0])
	elif cmd == 'i':
	    tstr = vk_s(tstr, int(arg[0])^user_id)
        else:
            raise VkAudioUrlDecodeError(
                'Unknown decode cmd: "{}"; Please send bugreport'.format(cmd)
            )

    return tstr


def vk_o(string):
    result = []
    index2 = 0

    for s in string:
        sym_index = VK_STR.find(s)

        if sym_index != -1:
            if index2 % 4 != 0:
                i = (i << 6) + sym_index
            else:
                i = sym_index

            if index2 % 4 != 0:
                index2 += 1
                shift = -2 * index2 & 6
                result += [chr(0xFF & (i >> shift))]
            else:
                index2 += 1

    return ''.join(result)


def vk_r(string, i):
    vk_str2 = VK_STR + VK_STR
    vk_str2_len = len(vk_str2)

    result = []

    for s in string:
        index = vk_str2.find(s)

        if index != -1:
            offset = index - int(i)

            if offset < 0:
                offset += vk_str2_len

            result += [vk_str2[offset]]
        else:
            result += [s]

    return ''.join(result)


def vk_xor(string, i):
    xor_val = ord(i[0])

    return ''.join(chr(ord(s) ^ xor_val) for s in string)

def vk_s(t,e):
	leonid = len(t)
	if leonid:
		cursor = abs(e)
		snuff_pos = {}
		for i in reversed(range(0,leonid)):
			cursor = ((leonid * (i + 1)) ^ cursor + i) % leonid
			snuff_pos[i] = cursor
		for i in range(1,leonid):
			offset = snuff_pos[leonid - i - 1]
			prev = t[i]
			t = t[:i]+t[offset]+t[i+1:]
			t = t[:offset] + prev + t[offset+1:]
	return t

