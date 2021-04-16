


class HashGenerator:
    def generateNext(instance_id,latest):
        next_token = ''
        carry = True
        l1 = latest[::-1]
        for i in range(len(l1)):
            if carry:
                if l1[i] == '9':
                    next_token += '0'
                    carry = True
                elif l1[i] == 'z':
                    next_token += '0'
                    carry = False
                else:
                    next_token += chr(ord(l1[i]) + 1)
                    carry = False
            else:
                next_token += l1[i]

        latest = next_token[::-1]

        if 0 <= instance_id < (26 * 2):
            val = chr(ord('a') + instance_id)
        else:
            val = chr(ord('0') + instance_id)

        return val + latest
