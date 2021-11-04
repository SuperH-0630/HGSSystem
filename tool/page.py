from flask import url_for
from tool.type_ import *


def get_page(url, page: int, count: int):
    if count <= 9:
        page_list = [[f"{i + 1}", url_for(url, page=i + 1)] for i in range(count)]
    elif page <= 5:
        """
        [1][2][3][4][5][6][...][count - 1][count]
        """
        page_list = [[f"{i + 1}", url_for(url, page=i + 1)] for i in range(6)]

        page_list += [None,
                      [f"{count - 1}", url_for(url, page=count - 1)],
                      [f"{count}", url_for(url, page=count)]]
    elif page >= count - 5:
        """
        [1][2][...][count - 5][count - 4][count - 3][count - 2][count - 1][count]
        """
        page_list: Optional[list] = [["1", url_for(url, page=1)],
                                     ["2", url_for(url, page=2)],
                                     None]
        page_list += [[f"{count - 5 + i}", url_for(url, page=count - 5 + i), False] for i in range(6)]
    else:
        """
        [1][2][...][page - 2][page - 1][page][page + 1][page + 2][...][count - 1][count]
        """
        page_list: Optional[list] = [["1", url_for(url, page=1)],
                                     ["2", url_for(url, page=2)],
                                     None]
        page_list += [[f"{page - 2 + i}", url_for(url, page=page - 2 + i)] for i in range(5)]
        page_list += [None,
                      [f"{count - 1}", url_for(url, page=count - 1)],
                      [f"{count}", url_for(url, page=count)]]
    return page_list
