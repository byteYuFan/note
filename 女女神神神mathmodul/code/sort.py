with open('data.txt', 'r') as f:
    lines = f.readlines()
    data = []
    for line in lines:
        line = line.strip()
        parts = line.split(')')
        tup = tuple(parts)
        data.append(tup)

sorted_data = sorted(data, key=lambda x: float(x[1]) if len(x) > 1 else 0)


with open('sorted_data.txt', 'w') as f:
    for line in sorted_data:
        if len(line) > 1:
            f.write(str(line[0]) + ')' + line[1] + '\n')
        else:
            f.write(str(line[0]) + '\n')
