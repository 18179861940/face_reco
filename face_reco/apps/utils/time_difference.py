
def minNums(e_time, n_time):
    '''计算两个时间点之间的分钟数'''
    # 来获取时间差中的秒数。注意，seconds获得的秒只是时间差中的小时、分钟和秒部分的和，并没有包含时间差的天数（既是两个时间点不是同一天，失效）
    total_seconds = (n_time - e_time).total_seconds()
    # 来获取准确的时间差，并将时间差转换为秒
    mins = int(total_seconds / 60)
    return mins


def houNums(e_time, n_time):
    total_seconds = (n_time - e_time).total_seconds()
    # 来获取准确的时间差，并将时间差转换为秒
    hous = int(total_seconds / 60 / 60)
    return hous