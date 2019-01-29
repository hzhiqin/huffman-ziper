from hufftree import HuffTree
from sys import byteorder


class Controller:
    @classmethod
    def start(cls):
        print("[mode, input file, output file]")
        print("1-compress 2-decompress 3-exit")
        args = input().split()
        if len(args) == 3:
            mode, file1, file2 = args[0], args[1], args[2]
        else:
            mode = args[0]
        if mode == "1":
            cls._compress(file1, file2)
        elif mode == "2":
            cls._decompress(file1, file2)
        elif mode == "3":
            exit(0)

    @staticmethod
    def _compress(infile, outfile):
        with open(infile, "rb") as file:
            freq_table = {}
            abyte = file.read(1)
            while abyte != b"":
                freq_table[abyte] = freq_table.get(abyte, 0) + 1
                abyte = file.read(1)

            total = file.tell()
            file.seek(0)
            data = file.read(total - 1)  # streaming improvement
        if freq_table[b"\n"] > 1:
            freq_table[b"\n"] = freq_table[b"\n"] - 1
        else:
            del freq_table[b"\n"]
        hufftree = HuffTree.build_tree(freq_table)
        codebook = hufftree.get_codebook()

        with open(outfile, "wb") as out:
            # number of characters in file
            out.write((len(codebook) - 1).to_bytes(1, byteorder))
            for bin_key, times in freq_table.items():  # times supports only 32-bit large
                out.write(bin_key)
                out.write(times.to_bytes(4, byteorder))
            code = "".join([codebook[ch.to_bytes(1, byteorder)] for ch in data])
            last = 0
            for i in range(8, len(code), 8):
                out.write(int(code[i - 8:i], 2).to_bytes(1, byteorder))
                last = i
            if last < len(code):
                remain = code[last:]
                out.write(len(remain).to_bytes(1, byteorder))
                remain = remain.rjust(8, "0")
                out.write(int(remain, 2).to_bytes(1, byteorder))
            else:
                out.write((0).to_bytes(2, byteorder))

    @staticmethod
    def _decompress(infile, outfile):
        freq_table = {}
        with open(infile, "rb") as compressed:
            ch_num = ord(compressed.read(1)) + 1
            for _ in range(ch_num):
                ch = compressed.read(1)
                num = int.from_bytes(compressed.read(4), byteorder)
                freq_table[ch] = num
            hufftree = HuffTree.build_tree(freq_table)
            data = compressed.read()

        bin_data = ["{0:b}".format(abyte).rjust(8, "0") for abyte in data]
        if int(bin_data[-2], 2) == 0:
            del bin_data[-1]
            del bin_data[-1]
        else:
            bits_num = int(bin_data[-2], 2)
            last = bin_data[-1][(8 - bits_num):]
            del bin_data[-1]
            del bin_data[-1]
            bin_data.append(last)
        bin_data = "".join(bin_data)

        # recover
        cur = hufftree.root
        with open(outfile, "wb") as recover_out:
            for bit in bin_data:
                if bit == "0":
                    cur = cur.left
                else:
                    cur = cur.right
                if cur.is_leaf:
                    recover_out.write(cur.value)
                    cur = hufftree.root


if __name__ == "__main__":
    Controller.start()
