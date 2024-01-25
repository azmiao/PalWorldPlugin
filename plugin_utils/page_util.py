
class Pagination:
    def __init__(self, data, page_size):
        self.data = data
        self.page_size = page_size

    def get_num_pages(self):
        return (len(self.data) + self.page_size - 1) // self.page_size  # 计算总页数

    def get_page(self, page_num):
        start_index = (page_num - 1) * self.page_size
        end_index = start_index + self.page_size
        return self.data[start_index:end_index]
