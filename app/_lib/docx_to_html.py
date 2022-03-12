#TODO still needs tweaking, not entirely integratable into website yet
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx import Document
import os

WORKING_DIR = os.getcwd()
#using Pt(font.size)px as font size is way too small. Tweak this value to increase it.
_FONT_SCALING = 2

DEFAULT = {
    "font": "calibri",
    "fontsize": 11,
    "align": "left",
    "color": "#000000"
}


# these variables store how the html file surrounding its content looks like. (#TODO not hardcode placeholders)
__BEGINFILE__ = """
{% extends "article.html" %}
{% block title %}{{ db_entry.title }}{% endblock %}
{% block article %}
"""
__ENDFILE__ = """
{% endblock %}
"""


"""
@param doc_source: the location of the word document (#TODO able to pass on as file?)
@return completely functional html file containing document content
"""
def convert(doc_source: str) -> str:
    html = __BEGINFILE__ + get_content_as_html(Document(doc_source)) + __ENDFILE__
    return html
    

"""
#TODO include placeholders etc. (-> reincarnate create_html()?)
@param document: docx.document.Document

Converts a given word document into html to suit the means of the website. This means excluded are:
    images,
    links
Very basic CSS (text-align, font-size, font-family, color) is recognized.

@return content of document converted to html
"""
def get_content_as_html(document) -> str:
    global DEFAULT

    tag = Tag()
    HTML_CONTENT = ""

    for paragraph in document.paragraphs:
        #stores the content of the current paragraph to pass on to Tag.paragraph(); is already html-formatted
        par_content = ""
        try:
            attr = {
                "font": get_font(paragraph.runs[0].font, handleNone=True),
                "fontsize": get_fontsize(paragraph.runs[0].font.size, handleNone=True),
                "align": get_textalign(paragraph.alignment, handleNone=True),
                "color": get_color(paragraph.runs[0].font.color.rgb.__str__())
            }

        except IndexError:
            attr["fontsize"] = DEFAULT["fontsize"]
            attr["font"] = DEFAULT["font"]
            attr["align"] = DEFAULT["align"]

            par_content = tag.linebreak()

        for run in paragraph.runs:
            font = run.font
            font_size = get_fontsize(font.size)
            #when only one word is coloured (without any additional decoration), it will not be detected as a run, so this is only effective
            #to a certain extend, but still, I tried
            run_color = get_color(font.color.rgb.__str__())
            content = run.text

            #checking for text decorations and surrounding the content accordingly
            if font.italic:content = tag.italic(content, font=font.name, fontsize=font_size, color=run_color)
            if font.bold:content = tag.bold(content, font=font.name,fontsize=font_size, color=run_color)
            if font.underline:content = tag.underline(content, font=font.name, fontsize=font_size, color=run_color)

            if content == "":
                par_content += tag.linebreak()
            else:
                par_content += content
        par_content = tag.paragraph(par_content, font=attr["font"], fontsize=attr["fontsize"], textalign=attr["align"])
        HTML_CONTENT += f"{par_content}\n"

    return HTML_CONTENT


#--------------------------------------------------------------------------------------------------------------------------


# i don't know why i thought this little syntactic sugar was worth an entire own class
class Tag:
    def __init__(self):
        pass

    def header(self, hierarchy: int, content: str, style=()) -> str:
        pass

    #TODO put style definition into its own function
    def paragraph(self, content: str, font=None,  fontsize=None, textalign=None, color=None) -> str:
        style = " style='{0}{1}{2}{3}'".format(self.set_font(font), self.set_fontsize(fontsize),
                                               self.set_textalign(textalign), self.set_color(color))

        #if style looks like this, every style is the same as the default, making specifying it unecessary
        if style == " style=''":
            style = ""
        tag_open = "<p{}>".format(style)
        return "{0}{1}</p>".format(tag_open, content)

    #TODO how much work is it to find out where image is located -> simply but images in between linebreaks?
    def image(self, source: str) -> str:
        pass

    #TODO instead of creating blank line, this function creates a line with only a ">" in it
    def linebreak(self) -> str:
        return "<br>"

    def italic(self, content: str, font=None,  fontsize=None, textalign=None, color=None) -> str:
        style = " style='{0}{1}{2}'".format(self.set_font( font), self.set_fontsize(fontsize), self.set_color(color))
        if style == " style=''":
            style = ""
        tag_open = "<i{}>".format(style)
        return "{0}{1}</i>".format(tag_open, content)

    def bold(self, content: str, font=None,  fontsize=None, textalign=None, color=None) -> str:
        style = " style='{0}{1}{2}'".format(self.set_font(font), self.set_fontsize(fontsize), self.set_color(color))
        if style == " style=''":
            style = ""
        tag_open = "<b{}>".format(style)
        return "{0}{1}</b>".format(tag_open, content)

    def underline(self, content: str, font=None,  fontsize=None, textalign=None, color=None) -> str:
        style = " style='{0}{1}{2}'".format(self.set_font(font), self.set_fontsize(fontsize), self.set_color(color))
        if style == " style=''":
            style = ""
        tag_open = "<u{}>".format(style)
        return "{0}{1}</u>".format(tag_open, content)

    #--------------------------------------------------
    #absolutely necessary functions

    def set_font(self, font: str) -> str:
        if not font:
            return ""
        return "font-family: {};".format(font)

    def set_fontsize(self, size: int) -> str:
        if not size:
            return ""
        return "font-size: {}px;".format(size * _FONT_SCALING)

    def set_textalign(self, align: str) -> str:
        if not align:
            return ""
        return "text-align: {};".format(align)

    def set_color(self, color: str) -> str:
        if not color:
            return ""
        return "color: {};".format(color)

    def tab():
        return "&#9"


#--------------------------------------------------------------------------------------------------------------------------

"""
@return: text alignment formatted as CSS
"""
def get_textalign(alignment: WD_ALIGN_PARAGRAPH, default=DEFAULT["align"], handleNone=False) -> str:
    if alignment == WD_ALIGN_PARAGRAPH.CENTER: return "center"
    if alignment == WD_ALIGN_PARAGRAPH.LEFT: return "left"
    if alignment == WD_ALIGN_PARAGRAPH.RIGHT: return "right"
    if handleNone: return default
    return None


def get_font(font, default=DEFAULT["font"], handleNone=False) -> str:
    if not font.name:
        if handleNone:
            return default
        return None
    return font.name.lower()


"""
run.font.size returns a very high number -> Pt(font.size) returns actual font-size
@param size: run.font.size
@param default: size of the run befor, in case run.font.size is None
"""
def get_fontsize(size: int, default=DEFAULT["fontsize"], handleNone=False) -> int:
    if not size:
        if handleNone:
            return default
        return None
    for i in range(64):
        if size == Pt(i):
            return i
    return None


"""
@return color as hex code, if color is None, the default is used
"""
def get_color(hex: str, default=DEFAULT["color"]) -> str:
    if not hex or hex == "None":  # for some reason `font.color.rgb.__str__()` returns "None" instead of actual None
        return default
    return "#{}".format(hex)


if __name__ == "__main__":
    html = convert("{0}/test.docx".format(WORKING_DIR))
    name = input("enter name (with .html extension): ")
    with open("html_pages/" + name, "w+", encoding="utf-8") as new_file:
        new_file.write(html)
