class Value:
    all_time = ''
    now_time = ''


def get_seconds(time_str: str):
    time_list = time_str.strip().split(':')
    time_list = [float(i) for i in time_list]
    seconds = 0
    for i, num in enumerate(time_list[::-1]):
        seconds = seconds + 60 ** i * num
    return seconds


def get_extract_voice_progress(input_str: str)->int:
    if 'Duration:' in input_str:
        Value.all_time = input_str[10:21]
        index = input_str.index('Duration:')
        Value.all_time = input_str[index + 10:index + 21]
    if input_str[:5] == 'size=':
        Value.now_time = input_str[21:32]
        # print(Value.now_time, Value.all_time)
        progress = get_seconds(Value.now_time) / get_seconds(Value.all_time) * 100
        return int(progress)
