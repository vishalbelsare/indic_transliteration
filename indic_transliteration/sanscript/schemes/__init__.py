import json
import os.path


class Scheme(dict):
    """Represents all of the data associated with a given scheme. In addition
    to storing whether or not a scheme is roman, :class:`Scheme` partitions
    a scheme's characters into important functional groups.
  
    :class:`Scheme` is just a subclass of :class:`dict`.
  
    :param data: a :class:`dict` of initial values. Note that the particular characters present here are also assumed to be the _preferred_ transliterations when transliterating to this scheme. 
    :param alternates: A map from keys appearing in `data` to lists of symbols with equal meaning. For example: M -> ['.n', .'m'] in ITRANS. This alternates is not used in transliterating to this scheme.
    :param is_roman: `True` if the scheme is a romanization and `False`
                     otherwise.
    """

    def __init__(self, data=None, is_roman=True, name=None):
        super(Scheme, self).__init__(data or {})
        self.is_roman = is_roman
        self.name = name


    def fix_lazy_anusvaara_except_padaantas(self, data_in, omit_sam, omit_yrl):
        lines = data_in.split("\n")
        lines_out = []
        for line in lines:
            words = line.split()
            ## We don't want ग्रामं गच्छ to turn into ग्रामङ् गच्छ or ग्रामम् गच्छ 
            words = [self.fix_lazy_anusvaara(word[:-1], omit_sam, omit_yrl) + word[-1] for word in words]
            lines_out.append(" ".join(words))
        return "\n".join(lines_out)

    def fix_lazy_anusvaara(self, data_in, omit_sam=False, omit_yrl=False, ignore_padaanta=False):
        from indic_transliteration import sanscript
        if ignore_padaanta:
            return self.fix_lazy_anusvaara_except_padaantas(data_in=data_in, omit_sam=omit_sam, omit_yrl=omit_yrl)
        data_out = sanscript.transliterate(data=data_in, _from=self.name, _to=sanscript.DEVANAGARI)
        data_out = sanscript.SCHEMES[sanscript.DEVANAGARI].fix_lazy_anusvaara(data_in=data_out, omit_sam=omit_sam, omit_yrl=omit_yrl)
        return sanscript.transliterate(data=data_out, _from=sanscript.DEVANAGARI, _to=self.name)
    
    def from_devanagari(self, data):
        """A convenience method"""
        from indic_transliteration import sanscript
        return sanscript.transliterate(data=data, _from=sanscript.DEVANAGARI, _to=self.name)


def load_scheme(file_path, cls, **kwargs):
  import codecs
  is_roman = "roman" in file_path
  name = os.path.basename(file_path).replace(".json", "")
  def scheme_maker(data):
    if "vowels" not in data:
        return data
    return cls(data=data, name=name, is_roman=is_roman, **kwargs) 
  with codecs.open(file_path, "r", 'utf-8') as file_out:
    scheme = json.load(file_out, object_hook=scheme_maker)
    return scheme