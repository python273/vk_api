# -*- coding: utf-8 -*-

VK_STR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN0PQRSTUVWXYZO123456789+/="


def decode_audio_url(string):
    vals = string.split("?extra=", 1)[1].split("#")

    tstr = vk_o(vals[0])
    ops_list = vk_o(vals[1]).split('\x09')[::-1]

    for op_data in ops_list:
        cmd, *arg = op_data.split('\x0b')

        if cmd == 'v':
            tstr = tstr[::-1]

        elif cmd == 'r':
            tstr = vk_r(tstr, arg[0])

        elif cmd == 'x':
            tstr = vk_xor(tstr, arg[0])

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
