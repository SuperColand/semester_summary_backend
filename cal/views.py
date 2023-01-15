import os

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.http import HttpRequest, JsonResponse
import json
import csv
import datetime
# Create your views here.

def reader_to_table(csv_reader):
    table = []
    for line in csv_reader:
        table.append(line)
    return table


def qid_to_question(qid):
    for line in question_id:
        if qid == line[2]:
            return line[3]
    return ''


def timestr_to_time(str):
    '''
    假设时间格式为“年/月/日 时:分”，返回五元组
    '''
    l = 0
    r = 0
    year = 0
    month = 0
    day = 0
    hour = 0
    minute = 0
    print(str)
    while str[r] != '-':
        r += 1
    year = int(str[l:r])
    l = r + 1
    r = r + 1

    while str[r] != '-':
        r += 1
    month = int(str[l:r])
    l = r + 1
    r = r + 1

    while str[r] != ' ':
        r += 1
    day = int(str[l:r])
    l = r + 1
    r = r + 1

    while str[r] != ':':
        r += 1
    hour = int(str[l:r])
    l = r + 1
    r = r + 1

    while str[r] != ':':
        r += 1
    minute = int(str[l:r])
    l = r + 1
    r = r + 1

    return year, month, day, hour, minute


def too_late(t):
    return t[3] >= 23 or t[3] <= 5


print('okok')
question_detail_table = reader_to_table(csv.reader(open('data/答题情况明细.csv', encoding='utf8')))
question_id = reader_to_table(csv.reader(open('data/题目编号名称关系.csv', encoding='utf-8')))
tutorials = {}
for root, ds, fs in os.walk('data/观看教程统计/'):
    for tutorial_name in fs:
        print(tutorial_name)
        # 有的人名字里有生僻字，得用gb18030编码，utf8 gdb gb2312都不行
        tutorials[tutorial_name[:-4]] = reader_to_table(csv.reader(open('data/观看教程统计/'+tutorial_name, encoding='gb18030')))

# 计算每道题的全部提交时间
question_last_submit_time = {}
for l in question_id:
    qid = l[2]
    question_last_submit_time[qid] = []
    for line in question_detail_table:
        if line[3] == qid:
            question_last_submit_time[qid].append(timestr_to_time(line[20]))
    question_last_submit_time[qid].sort()

# for line in table:
#     print(line)

@csrf_exempt
def say(request):
    assert isinstance(request, HttpRequest)
    # body = json.loads(request.body)
    sid = request.POST['ID']
    str_ = request.POST['str']
    t = str(datetime.datetime.now())
    t = t.replace(':', '-')
    with open(f'data/感想/{sid} {t}.txt', 'w') as f:
        f.write(str_)
    return JsonResponse({})

@csrf_exempt
def all_in_one(request):
    assert isinstance(request, HttpRequest)
    # body = json.loads(request.body)
    sid = request.POST['ID']
    number = int(request.POST['number'])
    print(sid)
    print(number)
    if number == 1:
        return cal1(sid)
    elif number == 2:
        return cal2(sid)
    elif number == 3:
        return cal3(sid)
    elif number == 4:
        return cal4(sid)
    elif number == 5:
        return cal5(sid)
    elif number == 6:
        return cal6(sid)
    elif number == 7:
        return cal7(sid)
    elif number == 8:
        return cal8(sid)
    return JsonResponse({})


def cal1(sid):
    '''
    在这半学期, 你在计组上
      进行了xxx次提交
      通过了xxx道题目
      观看了xxx分钟教程
    其中你在xxxx章节的停留时间最长
    看起来你对这一部分知识更感兴趣？
    '''
    # 提交次数
    submit_count = 0
    for line in question_detail_table:
        if line[1] == sid:
            submit_count += int(line[10])
    # 通过题目
    pass_count = 0
    for line in question_detail_table:
        if line[1] == sid and line[8] != '0':
            pass_count += 1
    # 观看教程总时间、章最大时间
    time_sum = 0
    max_time = 0
    max_name = ''
    for k,v in tutorials.items():
        for line in v:
            if line[1] == sid:
                this_time = time_to_minute(line[-2])
                time_sum += this_time
                if this_time >= max_time:
                    max_name = this_time
                    max_name = k
    print('cal1 done')
    return JsonResponse([
        submit_count,
        pass_count,
        time_sum,
        max_name,
    ], safe=False)


def cal2(sid):
    '''
    你提交最多的题目是
    	xxxx
     共提交了 xx 次
    '''
    max_submit_name = ''
    max_submit_count = 0
    for line in question_detail_table:
        if line[1] == sid and int(line[10]) > max_submit_count:
            max_submit_count = int(line[10])
            max_submit_name = qid_to_question(line[3])
    return JsonResponse([
        max_submit_name,
        max_submit_count
    ], safe=False)


def cal3(sid):
    '''
    你在xxxxx题目上
    提交了xxx次完成了首次AC
    （聪明的你很快就完成了它|你百折不挠地解决了它）*
    '''
    # 策略：按以下优先级
    # 最大提交次数超过8次
    # 最小提交次数小于等于2次
    # 最大的提交次数
    submit_counts = []
    for line in question_detail_table:
        if line[1] == sid:
            submit_counts.append((int(line[10]), qid_to_question(line[3])))
    if len(submit_counts) == 0:
        return JsonResponse(['', ''], safe=False)
    submit_counts.sort()
    if submit_counts[-1][0] >= 8:
        return JsonResponse(submit_counts[-1], safe=False)
    if submit_counts[0][0] <= 2:
        return JsonResponse(submit_counts[0], safe=False)
    return JsonResponse(submit_counts[-1], safe=False)


def cal4(sid):
    '''
    你在本学期第一次实验数制基础中
    获得了**分
    '''
    return JsonResponse({})


def time_to_response(t):
    return [
        t[1],
        t[2],
        str(t[3]) + ':' + str(t[4])
    ]

def cal5(sid):
    '''
    在xx月xx日，深夜 XXXX
    你依旧在提交xxxx题
    要好好注意身体(●'◡'●)
    '''
    for line in question_detail_table:
        if line[1] == sid:
            first_submit_time = timestr_to_time(line[19])
            last_submit_time = timestr_to_time(line[20])
            if too_late(first_submit_time):
                result = time_to_response(first_submit_time)
                result.append(qid_to_question(line[3]))
                return JsonResponse(result, safe=False)
            if too_late(last_submit_time):
                result = time_to_response(last_submit_time)
                result.append(qid_to_question(line[3]))
                return JsonResponse(result, safe=False)
    return JsonResponse(['','','',''], safe=False)


def cal6(sid):
    '''
        在MIPS汇编实验中
     你一共完成了xxx行代码
 （汇编写OS指日可期 | 很精简的作风！）
    '''
    result = 0
    for line in question_detail_table:
        if line[1] == sid and line[6] == 'MIPS 汇编':
            result += int(line[16])
    return JsonResponse([result], safe=False)


def cal7(sid):
    '''
    你在这半学期中
    完成了xx%的题目
    后半学期要加油 |下半学期再接再厉
    '''
    pass_count = 0
    for line in question_detail_table:
        if line[1] == sid and line[8] != '0':
            pass_count += 1
    return JsonResponse([pass_count / 19 * 100], safe=False)  # TODO: 以后可能不是16道题


def cal8(sid):
    '''
    你在 xxxx 题目中，
    比 xx% 的同学更x（早或晚）完成提交
    早起的鸟儿有虫吃|你就是ddl战神？
    '''
    # 每个人的每道题完成时间，在所有人当中的比例
    ratio_and_question = []
    for line in question_detail_table:
        if line[1] == sid:
            t = timestr_to_time(line[20])
            qid = line[3]
            i = 0
            for submit_time in question_last_submit_time[qid]:
                if t < submit_time:
                    break
                i += 1
            ratio = i / len(question_last_submit_time[qid])  # 比ratio比例的人提交得更晚
            ratio_and_question.append((ratio,qid_to_question(qid)))
    ratio_and_question.sort()
    if ratio_and_question[0][0] < 0.5:
        return JsonResponse([
            ratio_and_question[0][1],
            (1-ratio_and_question[0][0])*100,
            '早'
        ], safe=False)
    return JsonResponse([
        ratio_and_question[-1][1],
        ratio_and_question[-1][0]*100,
        '晚'
    ], safe=False)


def time_to_minute(time_str):
    print(time_str)
    return 60*int(time_str[0]) + int(time_str[2:3])


