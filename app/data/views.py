import pyecharts
from flask import render_template, Blueprint, Flask, abort
from jinja2 import Markup
import datetime

from tool.color import random_color
from tool.typing import Optional
from core.garbage import GarbageType

from app import views

data = Blueprint("data", __name__)
app: Optional[Flask] = None
init_opts = pyecharts.options.InitOpts(page_title="HGSSystem-统计",
                                       width="1000px",
                                       height="500px")


@data.route('/')
def index():
    return render_template("data/data.html")


@data.route('/pyecharts/count_by_day')
def count_by_days():
    """
    时段统计分析
    """
    db_data = views.website.count_by_days()
    if db_data is None:
        abort(500)

    bar = pyecharts.charts.Bar(init_opts=init_opts)

    res = {}
    loc_type = []
    count_data = [0] * 24
    for i in db_data:
        name = GarbageType.GarbageTypeStrList_ch[int(i[0].decode('utf-8'))]
        if name not in loc_type:
            loc_type.append(name)
        lst = res.get(name, list())
        lst.append(i[2])
        count_data[int(i[1])] += i[2]
        res[name] = lst

    (bar.add_xaxis(xaxis_data=[f"{i}h" for i in range(24)])
     .set_global_opts(xaxis_opts=pyecharts.options.AxisOpts(type_="category"),
                      title_opts=pyecharts.options.TitleOpts(title="时段统计")))

    for i in res:
        bar.add_yaxis(series_name=i, y_axis=res[i], color=random_color())
    bar.add_yaxis(series_name="合计", y_axis=count_data, color=random_color())

    return Markup(bar.render_embed())


def count_by_date__(days):
    """
    日期统计分析
    :param days: 7日 30日
    :return:
    """
    if days != 7 and days != 30:
        abort(404)

    db_data = views.website.count_by_times(days)
    if db_data is None:
        abort(500)

    line = pyecharts.charts.Line(init_opts=init_opts)
    res = {}
    loc_type = []
    count_data = [0] * days
    for i in db_data:
        name = GarbageType.GarbageTypeStrList_ch[int(i[0].decode('utf-8'))]
        if name not in loc_type:
            loc_type.append(name)
        lst = res.get(name, [0] * days)
        lst[int(i[1])] = i[2]
        count_data[int(i[1])] += i[2]
        res[name] = lst

    x_label = []
    end_time = datetime.datetime.now()
    for i in range(days - 1, -1, -1):
        d = end_time - datetime.timedelta(days=i)
        x_label.append(d.strftime("%Y-%m-%d"))

    (line.add_xaxis(xaxis_data=x_label)
     .set_global_opts(xaxis_opts=pyecharts.options.AxisOpts(type_="category"),
                      title_opts=pyecharts.options.TitleOpts(title=f"{days}日统计")))

    for i in res:
        y_data = res[i][::-1]  # 反转数据
        line.add_yaxis(series_name=i, y_axis=y_data, color=random_color())
    line.add_yaxis(series_name="合计", y_axis=count_data[::-1], color=random_color())
    return line


@data.route('/pyecharts/count_by_date/<int:days>')
def count_by_date(days):
    if days == 307:
        """
        将30日和7日统计汇聚在一张表中
        """
        line7 = count_by_date__(7)
        line30 = count_by_date__(30)
        chart = pyecharts.charts.Tab("时间统计")
        chart.add(line7, "7日统计")
        chart.add(line30, "30日统计")
    else:
        chart = count_by_date__(days)
    return Markup(chart.render_embed())


@data.route('/pyecharts/count_passing_rate')
def count_passing_rate():
    """
    通过率统计
    """
    rate_list = views.website.count_passing_rate()
    if rate_list is None:
        abort(500)

    page = pyecharts.charts.Tab("通过率")
    xaxis_opts = pyecharts.options.AxisOpts(type_="category")

    rate_global = 0
    for i in rate_list:
        name = GarbageType.GarbageTypeStrList_ch[int(i[0].decode("utf-8"))]
        pie = pyecharts.charts.Pie(init_opts=init_opts)
        pie.set_global_opts(xaxis_opts=xaxis_opts, title_opts=pyecharts.options.TitleOpts(title=f"{name}-通过率"))
        pie.add(series_name=name, data_pair=[("通过", i[1]), ("不通过", 1 - i[1])])
        page.add(pie, f"{name}-通过率")
        rate_global += i[1]

    rate_global = rate_global / 4
    pie = pyecharts.charts.Pie(init_opts=init_opts)
    pie.set_global_opts(xaxis_opts=xaxis_opts, title_opts=pyecharts.options.TitleOpts(title="平均-通过率"))
    pie.add(series_name="平均", data_pair=[("通过", rate_global), ("不通过", 1 - rate_global)])
    page.add(pie, "平均-通过率")

    return Markup(page.render_embed())


def creat_data_website(app_: Flask):
    global app
    if app is None:
        app = app_
        app.register_blueprint(data, url_prefix="/data")
