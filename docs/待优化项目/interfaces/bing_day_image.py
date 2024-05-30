# @Version        : 1.0
# @Create Time    : 2024/4/29 14:09
# @File           : bing_day_image.py
# @IDE            : PyCharm
# @Desc           : Bing 每日一图


"""
必应官方接口：可以通过简单的API调用获取必应的每日一图。
API的地址是 https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1，
这里idx=0代表今日图片，n=1表示获取一张图片

在必应每日一图的API中，idx 参数用来指定从当前日期往回数的天数，用于获取过去的图片。
参数的值是一个整数，其中 0 表示当前日期的图片，1 表示昨天的图片，依此类推。这个参数允许你访问到过去一定天数内的图片。
例如，如果你设置 idx=3，API将返回从今天起往回数的第三天的图片。
"""
