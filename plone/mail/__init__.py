# Some utilities for mail
from email.Message import Message
from email import Header
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.Charset import add_charset, QP, SHORTEST
from reStructuredText import HTML

# Add a charset for utf8 that should be encoded quopri,
# e.g. we assume mostly latin chars, if not the encoding will
# be very space inefficient
add_charset('utf8', SHORTEST, QP, 'utf8')

def decode_header(value):
    """Converts an encoded header into a unicode string::

        >>> decode_header(
        ...       'Je les =?utf-8?b?ZMODwql0w4PCqHN0ZQ==?= oui?')
        u'Je les d\\xc3\\xa9t\\xc3\\xa8ste oui?'

    """
    encoded_strings = Header.decode_header(value)
    header_val = Header.Header()
    for string, encoding in encoded_strings:
        header_val.append(string, encoding, errors='replace')
    return unicode(header_val)

def construct_simple_encoded_message(from_addr, to_addr, subject, body,
                                  other_headers=None, encoding='utf8'):
    """All inputs to this method are expected to be unicode or ascii.

    We should be able to pass in some arbitrary unicode stuff and get back
    a sensible encoded message:

        >>> m = construct_simple_encoded_message(u'test@example.com',
        ...     u'test@example.com',
        ...     u'Un Subj\xc3\xa9t',
        ...     u'A simple body with some non ascii t\xc3\xa9xt',
        ...     other_headers = {'X-Test': u't\xc3\xa9st'})
        >>> print m.as_string()
        From: test@example.com
        To: test@example.com
        Subject: Un =?utf8?b?U3ViasODwql0?=
        X-Test: =?utf8?b?dMODwqlzdA==?=
        MIME-Version: 1.0
        Content-Type: text/plain; charset="utf8"
        Content-Transfer-Encoding: quoted-printable
        <BLANKLINE>
        A simple body with some non ascii t=C3=83=C2=A9xt
    """
    if other_headers is None:
        other_headers = {}
    m = Message()
    # If from is not in the set of other headers use the from addr
    # otherwise we may be masquerading as someone else
    if 'From' not in other_headers:
        m['From'] = encode_header(from_addr, encoding)
    m['To'] = encode_header(to_addr, encoding)
    m['Subject'] = encode_header(subject, encoding)
    for key, val in other_headers.items():
        m[key] = encode_header(val, encoding)
    body = body.encode(encoding)
    m.set_payload(body, charset=encoding)
    return m

def encode_header(str, encoding):
    """Attempt to encode a unicode header string word by word.  Let's try
    this out::

    ASCII strings should be unchanged::
        >>> encode_header(u'A simple subject', 'utf8')
        'A simple subject'

    Non-ASCII should be encoded::
        >>> encode_header(
        ... u'\\xc3\\xa9\\xc3\\xb8\\xe2\\x88\\x91\\xc3\\x9f\\xcf\\x80\\xc3\\xa5\\xe2\\x80\\xa0',
        ... 'utf8')
        '=?utf8?b?w4PCqcODwrjDosKIwpHDg8Kfw4/CgMODwqXDosKAwqA=?='

    A mix of the two should be nicely mixed::
        >>> encode_header(u'Je les d\\xc3\\xa9t\\xc3\\xa8ste, non?', 'utf8')
        'Je les =?utf8?b?ZMODwql0w4PCqHN0ZSw=?= non?'

    """
    cur_type = None
    last_type = None
    header_val = Header.Header()
    for word in str.split(' '):
        last_type = cur_type
        try:
            enc_word = word.encode('ascii')
            cur_type = 'ascii'
        except UnicodeEncodeError:
            enc_word = word.encode(encoding)
            cur_type = encoding
        header_val.append(enc_word, cur_type)

    return header_val.encode()

def construct_multipart(from_addr, to_addr, subject, body, html_body,
                        other_headers=None, encoding='utf8'):
    """All inputs to this method are expected to be unicode or ascii.

    We should be able to pass in some arbitrary unicode stuff and get back
    a sensible encoded message:

        >>> m = construct_multipart(u'test@example.com',
        ...     u'test@example.com',
        ...     u'Un Subj\xc3\xa9t',
        ...     u'A simple body with some non ascii t\xc3\xa9xt',
        ...     u'<p>A simple body with some non ascii t\xc3\xa9xt</p>',
        ...     other_headers = {'X-Test': u't\xc3\xa9st'})
        >>> print m.as_string() #doctest: +ELLIPSIS
        Content-Type: multipart/alternative; boundary="..."
        MIME-Version: 1.0
        From: test@example.com
        To: test@example.com
        Subject: Un =?utf8?b?U3ViasODwql0?=
        X-Test: =?utf8?b?dMODwqlzdA==?=
        <BLANKLINE>
        --...
        Content-Type: text/plain; charset="utf8"
        MIME-Version: 1.0
        Content-Transfer-Encoding: quoted-printable
        Content-Disposition: inline
        <BLANKLINE>
        A simple body with some non ascii t=C3=83=C2=A9xt
        --...
        Content-Type: text/html; charset="utf8"
        MIME-Version: 1.0
        Content-Transfer-Encoding: quoted-printable
        Content-Disposition: inline
        <BLANKLINE>
        <p>A simple body with some non ascii t=C3=83=C2=A9xt</p>
        --...
    """
    if other_headers is None:
        other_headers = {}
    m = MIMEMultipart('alternative')
    if 'From' not in other_headers:
        m['From'] = encode_header(from_addr, encoding)
    m['To'] = encode_header(to_addr, encoding)
    m['Subject'] = encode_header(subject, encoding)
    for key, val in other_headers.items():
        m[key] = encode_header(val, encoding)
    body = body.encode(encoding)
    txt = MIMEText(body,  _charset=encoding)
    txt['Content-Disposition'] = 'inline'
    m.attach(txt)
    html_body = html_body.encode(encoding)
    html = MIMEText(html_body, _subtype='html', _charset=encoding)
    html['Content-Disposition'] = 'inline'
    m.attach(html)
    return m



def construct_multipart_from_stx(from_addr, to_addr, subject, body,
                        other_headers=None, encoding='utf8'):
    """All inputs to this method are expected to be unicode or ascii.

    This converts the input text to html using the stx converter

        >>> m = construct_multipart_from_stx(u'test@example.com',
        ...     u'test@example.com',
        ...     u'Un Subj\xc3\xa9t',
        ...     u'A simple body with some non ascii t\xc3\xa9xt with "a link":http://www.example.com')
        >>> print m.as_string() #doctest: +ELLIPSIS
        Content-Type: multipart/alternative; boundary="..."
        MIME-Version: 1.0
        From: test@example.com
        To: test@example.com
        Subject: Un =?utf8?b?U3ViasODwql0?=
        <BLANKLINE>
        --...
        Content-Type: text/plain; charset="utf8"
        MIME-Version: 1.0
        Content-Transfer-Encoding: quoted-printable
        Content-Disposition: inline
        <BLANKLINE>
        A simple body with some non ascii t=C3=83=C2=A9xt with "a link":http://www.=
        example.com
        --...
        Content-Type: text/html; charset="utf8"
        MIME-Version: 1.0
        Content-Transfer-Encoding: quoted-printable
        Content-Disposition: inline
        <BLANKLINE>
        <p>A simple body with some non ascii t=C3=83=C2=A9xt with <a href=3D"http:/=
        /www.example.com">a link</a></p>
        <BLANKLINE>
        --...
    """
    if other_headers is None:
        other_headers = {}
    html = HTML(body, level=2, header=0)
    return construct_multipart(from_addr, to_addr, subject, body,
                               html, other_headers, encoding)
