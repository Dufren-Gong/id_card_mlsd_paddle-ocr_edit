class Ui_Shapes():
    def __init__(self,
                 start_width = 0,
                 start_height = 0,
                 button_between = 4,
                 line_height_gap = 10,
                 round_gap = 30,
                 lineedit_hight = 20,
                 label_height = 20,
                 button_height = 20,
                 combobox_height = 20) -> None:
        self.start_width = start_width
        self.start_height = start_height
        self.button_between = button_between
        self.line_height_gap = line_height_gap
        self.round_gap = round_gap
        #设置不同label的高度
        self.lineedit_hight = lineedit_hight
        self.label_height = label_height
        self.button_height = button_height
        self.combobox_height = combobox_height

    def layout(self, line_heights, widths):
        assert len(line_heights) == len(widths)
        self.calculate_start_heights(line_heights)
        self.calculate_start_widths(widths)
        self.shape_tuples = self.get_template_shape_tuple()

    def calculate_start_heights(self, line_heights):
        self.line_heights = line_heights
        start_heights = []
        current_height = self.round_gap
        for line_height in line_heights:
            start_heights.append(current_height + self.start_height)
            current_height += (line_height + self.line_height_gap)
        self.start_heights = start_heights
        #添加窗口高度
        self.height = current_height - self.line_height_gap + self.round_gap

    def calculate_start_widths(self, widths):
        self.widths = widths
        start_widths = []
        all_end_widths = []
        for width in widths:
            current_width = self.round_gap
            this_start_widths = []
            for this_width in width:
                this_start_widths.append(current_width + self.start_width)
                current_width += (this_width + self.button_between)
            #获取该行最宽宽度
            all_end_widths.append(current_width + self.round_gap - self.button_between)
            start_widths.append(this_start_widths)
        self.start_widths = start_widths
        #获取窗口宽度
        self.width = max(all_end_widths)

    def get_template_shape_tuple(self):
        tuples = []
        for line_index, line_widths in enumerate(self.widths):
            line_tuples = []
            for column_index, width in enumerate(line_widths):
                line_tuples.append((self.start_widths[line_index][column_index],
                                    self.start_heights[line_index],
                                    width,
                                    self.line_heights[line_index]))
            tuples.append(line_tuples)
        return tuples
        

