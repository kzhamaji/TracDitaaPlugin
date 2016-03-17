# encoding:utf-8

import os
import subprocess
import sha
import tempfile

from trac.core import *
from trac.config import Option, IntOption
from trac.wiki.macros import WikiMacroBase
from trac.wiki.api import parse_args
from trac.wiki.formatter import system_message
from trac.attachment import Attachment

from genshi.builder import tag

class DittaMacro (WikiMacroBase):
    u'''
synopsis)
{{{
{{{
#!ditaa key=value
+-----+
| AAA |
+-----+
}}}
 * width=(CSS spec: 50%, 800px, etc)
 * separation=True|False
 * shadow=True|False
 * (scale=float)
}}}
{{{
#!ditaa
+-----+
| AAA |
+-----+
}}}
    '''
    ditaa_jar = Option("ditaa", "ditaa_jar", "")
    cache_dir = Option("ditaa", "cache_dir", "htdocs/ditaa")

    def get_macros (self):
        yield 'ditaa'

    def is_inline (self, content):
        return True

    def expand_macro(self, formatter, name, content, _args={}):
        content, args = parse_args(content)
        args.update(_args)
        content = ''.join(content)

        content, _args = self._parse_content_compat(content)
        args.update(_args)

        content = content.rstrip()
        if not content:
            return ''

        width = args.pop('width', '')

        option_str = '&'.join(["%s=%s" % (k,args[k]) for k in sorted(args.keys())])
        sha_key   = sha.new(content+option_str).hexdigest()
        png_name = sha_key + '.png'

        rsrc = formatter.resource
        cache_dir = os.path.join(self.env.path, self.cache_dir, rsrc.realm, rsrc.id)
        png_path  = os.path.join(cache_dir, png_name)

        if not os.path.exists(png_path):
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)

            fo = tempfile.NamedTemporaryFile(bufsize=0)
            try:
                fo.write(content)

                # txt -> png
                cmd = ["java", "-jar", self.ditaa_jar, "-o", "--encoding", "utf-8"]

                scale = float(args.get('scale', 1.0))
                if scale != 1.0:
                    cmd += ["-s", str(scale)]
                if args.get('separation') is False:
                    cmd += ["--no-separation"]
                if args.get('shadows') is False:
                    cmd += ["--no-shadows"]

                cmd += [fo.name, png_path]
                p = subprocess.Popen(cmd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        env={"LANG":"ja_JP.UTF-8"})
                (stdout, stderr) = p.communicate(input=None)
                if p.returncode != 0:
                    return system_message("Fail to execute ditaa: %s" % stderr)
            finally:
                fo.close()

        png_url = formatter.href.chrome('site', 'ditaa', rsrc.realm, rsrc.id, png_name)
        img = tag.img(src=png_url, class_="ditaa", alt=sha_key)

        if width:
            img(width=width)

        return img

    def _parse_content_compat (self, content):
        args = {}
        lines = []
        for l in content.splitlines():
            if l.startswith(':') or l.startswith('#:'):
                k, v = [e.strip() for e in l.split(':',1)[1].split('=')]
                if k == 'scale':
                    args['scale'] = float(v)
                elif k == 'no-separation':
                    args['separation'] = not (v.lower() != 'false')
                elif k == 'no-shadow':
                    args['shadows'] = not (v.lower() != 'false')
                elif k == 'width':
                    args['width'] = v
                else:
                    raise TracError('invalid option(%s)' % k)
            else:
                lines.append(l)
        return ('\n'.join(lines), args)
