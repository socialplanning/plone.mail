# Some utilities for mail
from email.Message import Message
from email import Header
from email.MIMEText import MIMEText
from email.quopriMIME import body_encode

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
                                  other_headers=None, encoding='utf-8'):
    """The python email package makes it very difficult to send quoted-printable
    messages for charsets other than ascii and selected others.  As a result we
    need to do a few things manually here.  All inputs to this method are
    expected to be unicode or ascii.

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
        Subject: Un =?utf-8?b?U3ViasODwql0?=
        Content-Transfer-Encoding: quoted-printable
        Content-Type: text/plain; charset="utf-8"
        X-Test: =?utf-8?b?dMODwqlzdA==?=
        <BLANKLINE>
        A simple body with some non ascii t=C3=83=C2=A9xt
    """
    if other_headers is None:
        other_headers = {}
    m = Message()
    if 'From' in other_headers:
        m['From'] = encode_header(other_headers['From'], encoding)
    else:
        m['From'] = encode_header(from_addr, encoding)
    m['To'] = encode_header(to_addr, encoding)
    m['Subject'] = encode_header(subject, encoding)
    # Normally we wouldn't try to set these manually, but the email module
    # tries to be a little too smart here.
    m['Content-Transfer-Encoding'] = 'quoted-printable'
    m['Content-Type'] = 'text/plain; charset="%s"'%encoding
    for key, val in other_headers.items():
        m[key] = encode_header(val, encoding)
    body = body.encode(encoding)
    body = body_encode(body, eol="\r\n")
    m.set_payload(body)
    return m

def encode_header(str, encoding):
    """Attempt to encode a unicode header string word by word.  Let's try
    this out::

    ASCII strings should be unchanged::
        >>> encode_header(u'A simple subject', 'utf-8')
        'A simple subject'

    Non-ASCII should be encoded::
        >>> encode_header(
        ... u'\\xc3\\xa9\\xc3\\xb8\\xe2\\x88\\x91\\xc3\\x9f\\xcf\\x80\\xc3\\xa5\\xe2\\x80\\xa0',
        ... 'utf-8')
        '=?utf-8?b?w4PCqcODwrjDosKIwpHDg8Kfw4/CgMODwqXDosKAwqA=?='

    A mix of the two should be nicely mixed::
        >>> encode_header(u'Je les d\\xc3\\xa9t\\xc3\\xa8ste oui?', 'utf-8')
        'Je les =?utf-8?b?ZMODwql0w4PCqHN0ZQ==?= oui?'

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
        header_val.append(word, cur_type)

    return header_val.encode()
