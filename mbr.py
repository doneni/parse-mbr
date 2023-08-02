import sys

def hex2str(hex_value):
        return bytes.fromhex(hex_value).decode('utf-8')

def parse_partition_table(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()

    partition_entries = []

    # MBR partition table
    for i in range(4):
        entry_offset = 446 + i * 16
        partition_entry = data[entry_offset:entry_offset + 16]
        partition_info = parse_partition_entry(partition_entry, data, 0)

        if partition_info and partition_info['partition_type'] == 7:
            partition_entries.append(partition_info)

        if partition_info and partition_info['partition_type'] == 5:
            starting_sector = partition_info['starting_sector']
            extended_partitions = parse_ebr_partition(starting_sector, data)
            partition_entries.extend(extended_partitions)

    return partition_entries


def parse_partition_entry(entry_data, data, base):
    partition_type = entry_data[4]
    starting_lba = int.from_bytes(entry_data[8:12], byteorder='little')
    size_in_lba = int.from_bytes(entry_data[12:16], byteorder='little')

    starting_sector = starting_lba * 512
    filesystem_name = data[starting_sector + 3: starting_sector + 7]
    size = size_in_lba * 512
    if (base != 0):
        starting_sector += base

    return {
        'partition_type': partition_type,
        'filesystem_name': filesystem_name,
        'starting_sector': starting_sector,
        'size': size
    }

def parse_ebr_partition(starting_sector, data):
    extended_partitions = []
    ebr_offset = starting_sector
    done = 0
    while True:
        ebr_data = data[ebr_offset:ebr_offset + 512]
        if (done == 1):
            break

        for i in range(2):
            entry_offset = ebr_offset + 446 + i * 16
            partition_entry = data[entry_offset:entry_offset + 16]
            partition_type = partition_entry[4]

            if partition_type == 7:
                partition_info = parse_partition_entry(partition_entry, data, ebr_offset)
                extended_partitions.append(partition_info)
            elif partition_type == 5:
                next_ebr_lba = int.from_bytes(partition_entry[8:12], byteorder='little') * 512
                if next_ebr_lba == 0:
                    break
                ebr_offset = starting_sector + next_ebr_lba
            else:
                done = 1
                break
                


    return extended_partitions

def main():
    if len(sys.argv) < 2:
        print("Usage: Python3 mbr.py /path/to/image/file")
    else:
        file_path = sys.argv[1]
        print("Parsing MBR...")
        print("file path:", file_path) 
    
    file_path = 'parse-mbr\mbr_128.dd'
    partitions = parse_partition_table(file_path)
    
    # 파싱한 파티션 정보를 출력합니다.
    for i, partition in enumerate(partitions, 1):
        print(f"[Partition {i}]")
        print("filesystem_name:", partition['filesystem_name'])
        print("starting_sector(DEC):", partition['starting_sector'])
        print("size:", partition['size'], "bytes")
        print()

if __name__ == "__main__":
    main()
