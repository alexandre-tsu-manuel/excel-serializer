from openpyxl.styles import Font
from openpyxl.worksheet.table import TableStyleInfo

SEPARATOR = "."
ROOT_SHEET_NAME = "Root"
LINK_FONT = Font(color="0000FF", underline="single")
TABLE_STYLE_INFO = TableStyleInfo(
    name="TableStyleMedium9",
    showFirstColumn=False,
    showLastColumn=False,
    showRowStripes=True,
    showColumnStripes=False,
)
