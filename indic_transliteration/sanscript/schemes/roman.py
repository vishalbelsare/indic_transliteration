import regex
import os
from indic_transliteration.sanscript import Scheme
from indic_transliteration.sanscript.schemes import load_scheme

# Roman schemes
# -------------
HK = 'hk'
IAST = 'iast'
ISO = 'ISO'
ITRANS = 'itrans'
TITUS = 'titus'

"""Optitransv1 is described in https://sanskrit-coders.github.io/input/optitrans/#optitrans-v1 . OPTITRANS, while staying close to ITRANS it provides a more intuitive transliteration compared to ITRANS (shankara manju - शङ्कर मञ्जु)."""
OPTITRANS = 'optitrans'
KOLKATA_v2 = 'kolkata_v2'
SLP1 = 'slp1'
VELTHUIS = 'velthuis'
WX = 'wx'


class RomanScheme(Scheme):
    def __init__(self, data=None, name=None, **kwargs):
        super(RomanScheme, self).__init__(data=data, name=name, is_roman=True)
        self["vowel_marks"] = self["vowels"][1:]
    
    def get_standard_form(self, data):
        """Roman schemes define multiple representations of the same devanAgarI character. This method gets a library-standard representation.
        
        data : a text in the given scheme.
        """
        if self["alternates"] is None:
            return data
        from indic_transliteration import sanscript
        return sanscript.transliterate(data=sanscript.transliterate(_from=self.name, _to=sanscript.DEVANAGARI, data=data), _from=sanscript.DEVANAGARI, _to=self.name)

    @classmethod
    def to_shatapatha_svara(cls, text):
        # References: https://en.wikipedia.org/wiki/Combining_Diacritical_Marks
        text = text.replace("́", "᳘")
        text = text.replace("̀", "᳘")
        text = regex.sub("᳘([ंःँ])", "\\1᳘", text)
        return text

    def get_double_lettered(self, text):
        text = self.get_standard_form(data=text)
        text = text.replace("A", "aa")
        text = text.replace("I", "ii")
        text = text.replace("U", "uu")
        return text

    def mark_off_non_indic_in_line(self, text):
        words = text.split()
        from indic_transliteration import detect
        out_words = []
        for word in words:
            if detect.detect(word).lower() != self.name.lower():
                out_words.append("<%s>" % word)
            else:
                out_words.append(word)
        return " ".join(out_words)


class ItransScheme(RomanScheme):
    def fix_lazy_anusvaara(self, data_in, omit_sam=False, omit_yrl=False, ignore_padaanta=False):
        if ignore_padaanta:
            return self.fix_lazy_anusvaara_except_padaantas(data_in=data_in, omit_sam=omit_sam, omit_yrl=omit_yrl)
        data_out = data_in
        import regex
        if omit_sam:
            prefix = "(?<!sa)"
        else:
            prefix = ""
        data_out = regex.sub('%sM( *)([kgx])' % (prefix), r'~N\1\2',   data_out)
        data_out = regex.sub('%sM( *)([cCj])' % (prefix), r'~n\1\2', data_out)
        data_out = regex.sub('%sM( *)([tdn])' % (prefix), r'n\1\2', data_out)
        data_out = regex.sub('%sM( *)([TDN])' % (prefix), r'N\1\2', data_out)
        data_out = regex.sub('%sM( *)([pb])' % (prefix), r'm\1\2', data_out)
        if not omit_yrl:
            data_out = regex.sub('%sM( *)([yvl])' % (prefix), r'\2.N\1\2', data_out)
        return data_out


class OptitransScheme(RomanScheme):

    def to_lay_indian(self, text, jn_replacement="GY", t_replacement="t"):
        text = self.get_standard_form(data=text)
        text = text.replace('RR', 'ri')
        text = text.replace('R', 'ri')
        text = text.replace('LLi', 'lri')
        text = text.replace('LLI', 'lri')
        text = text.replace('jn', jn_replacement)
        text = text.replace('x', 'ksh')
        if t_replacement != "t":
            text = text.replace("t", t_replacement)
        text = text.lower()
        return text


class CapitalizableScheme(RomanScheme):
    def __init__(self, data=None, is_roman=True, name=None):
        super(CapitalizableScheme, self).__init__(data=data, is_roman=is_roman, name=name)
        # A local function.
        def add_capitalized_synonyms(some_list):
            for x in some_list:
                synonyms = [x.capitalize()]
                if x in self["alternates"]:
                    synonyms = self["alternates"][x] + [y.capitalize() for y in self["alternates"][x]]
                self["alternates"][x] = synonyms
        add_capitalized_synonyms(self["vowels"])
        add_capitalized_synonyms(self["consonants"])
        if "extra_consonants" in self:
            add_capitalized_synonyms(self["extra_consonants"])
        add_capitalized_synonyms(self["accented_vowel_alternates"].keys())
        add_capitalized_synonyms(["oṃ"])

    def get_standard_form(self, data):
        pattern = "([%s])([̥̇¯̄]+)" % ("".join(self["accents"]))
        data = regex.sub(pattern, "\\2\\1", data)
        return super(CapitalizableScheme, self).get_standard_form(data=data)


data_path = os.path.join(os.path.dirname(__file__), "data/roman")

SCHEMES = {
    HK: load_scheme(file_path=os.path.join(data_path, "hk.json"), cls=RomanScheme),
    VELTHUIS: load_scheme(file_path=os.path.join(data_path, "velthuis.json"), cls=RomanScheme),
    OPTITRANS: load_scheme(file_path=os.path.join(data_path, "optitrans.json"), cls=OptitransScheme),
    ITRANS: load_scheme(file_path=os.path.join(data_path, "itrans.json"), cls=ItransScheme),
    IAST: load_scheme(file_path=os.path.join(data_path, "iast.json"), cls=CapitalizableScheme),
    KOLKATA_v2: load_scheme(file_path=os.path.join(data_path, "kolkata_v2.json"), cls=CapitalizableScheme),
    SLP1: load_scheme(file_path=os.path.join(data_path, "slp1.json"), cls=RomanScheme),
    WX: load_scheme(file_path=os.path.join(data_path, "wx.json"), cls=RomanScheme),
    TITUS: load_scheme(file_path=os.path.join(data_path, "titus.json"), cls=RomanScheme)
}

ALL_SCHEME_IDS = SCHEMES.keys()

