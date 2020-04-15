from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def pagination(currentPage, pageSize, list_data):
    paginator = Paginator(list_data, pageSize)
    total = paginator.count
    pageSize = int(pageSize)
    pageAmount = int((total+pageSize-1)/pageSize)
    try:
        content_list = paginator.page(currentPage)
    except PageNotAnInteger:
        # 如果请求的页数不是整数, 返回第一页。
        content_list = paginator.page(1)
    except EmptyPage:
        # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
        content_list = paginator.page(paginator.num_pages)

    result = []
    for i in content_list:
        result.append(i)
    data = {
        'pageNo': int(paginator.num_pages),  # 当前页
        'pageSize': int(len(paginator.page(paginator.num_pages))),  # 当前页面数据条数
        'total': total,  # 总条数
        'pageAmount': pageAmount,  # 总页数
        'row': result
    }
    return data