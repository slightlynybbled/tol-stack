from io import BytesIO
from datetime import datetime

from fpdf import FPDF
from PIL import Image

from tol_stack.stack import StackPath
from tol_stack.version import __version__


class StackupReport(FPDF):
    _heading_font_sizes = [16, 14, 12, 10]
    _font_size = 10

    def __init__(self, stackpath: StackPath):
        super().__init__()

        self.font_name = 'helvetica'
        self.stackpath = stackpath

        # title page
        self.add_page()
        self.set_font(self.font_name, 'B', self._heading_font_sizes[0])
        self.multi_cell(185, 10, f'{stackpath.name}')

        self.set_font(self.font_name, '', self._font_size)
        self.ln()
        self.multi_cell(185, 10, f'Report generated by Tolerence Stack Analyzer v{__version__} on {datetime.now()}', ln=2)

        if self.stackpath.description is not None:
            self.ln()
            self.multi_cell(185, 10, f'{self.stackpath.description}', ln=1)

        if self.stackpath.images is not None:
            for image in self.stackpath.images:
                self.image(image)

        # create a part-by-part max/min length analysis,
        # including comments, pictures, and distributions
        for part in self.stackpath.parts:
            self.add_page()
            self.set_font(self.font_name, "B", self._font_size)
            self.cell(185, 10, f'{part.name}', ln=1)

            self.set_font(self.font_name, "", self._font_size)
            if part.nominal_length is not None:
                self.cell(185, 10, f'nominal length: {part.nominal_length}', ln=1)
            if part.tolerance is not None:
                self.cell(185, 10, f'tolerance: {part.tolerance}', ln=1)

            if part.images is not None:
                for image in part.images:
                    width, height = image.size
                    max_height = 180
                    if height > max_height:
                        new_width = width * max_height // height
                        new_height = max_height
                        image.thumbnail((new_width, new_height), Image.ANTIALIAS)
                    self.image(image)

            if part.comment is not None:
                self.cell(185, 10, f'{part.comment}', ln=1)

            # show part distribution
            buffer = BytesIO()
            fig = part.show_length_dist()
            fig.savefig(buffer, format='png')
            self.image(buffer, w=self.epw)

        # create stack path analysis
        buffer = BytesIO()
        fig = self.stackpath.show_length_dist()
        fig.savefig(buffer, format='png')
        self.image(buffer, w=self.epw)

        self.output(f'{self.stackpath.name}.pdf')






