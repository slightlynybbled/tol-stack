from datetime import datetime

from fpdf import FPDF

from tol_stack.stack import StackPath


class StackupReport(FPDF):
    def __init__(self, stackpath: StackPath):
        super().__init__()

        self.font_name = 'helvetica'
        self.stackpath = stackpath

        # title page
        self.add_page()
        self.set_font(self.font_name, 'B', 16)
        self.cell(185, 10, f'{stackpath.name}')

        self.set_font(self.font_name, '', 12)
        self.ln(20)
        self.cell(185, 10, f'{datetime.now().date()}')

        if self.stackpath.description is not None:
            self.ln(10)
            self.cell(185, 10, f'{self.stackpath.description}')

        # create a part-by-part max/min length analysis,
        # including comments, pictures, and distributions
        for part in self.stackpath.parts:
            self.add_page()
            self.set_font(self.font_name, "B", 14)
            self.cell(185, 10, f'{part.name}')

            # todo: show distribution
            # todo: show measurements and characteristics

        # todo: create a part-by-part concentricity analysis, including comments, pictures, and distributions

        self.output(f'{self.stackpath.name}.pdf')






