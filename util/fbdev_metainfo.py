from . import fbdev_metadata


def getdict(struct):
    result = {}
    for field, _ in struct._fields_:
        value = getattr(struct, field)
        if (type(value) not in [int, float, bool]) and not bool(value):
            value = None
        elif hasattr(value, "_length_") and hasattr(value, "_type_"):
            value = list(value)
        elif hasattr(value, "_fields_"):
            value = getdict(value)
        result[field] = value
    return result


def extract_info(raw_info):
    info = tuple(map(getdict, raw_info))
    extracted = {
        'size': info[0]['smem_len'],
        'line': info[0]['line_length'],
        'real_resolution': (info[1]['xres'], info[1]['yres']),
        'virt_resolution': (info[1]['xres_virtual'], info[1]['yres_virtual']),
        'offset': (info[1]['xoffset'], info[1]['yoffset']),
        'pixel_format': {
            'bits_per_pixel': info[1]['bits_per_pixel'],
            'grayscale': info[1]['grayscale'],
            'channels': {channel:info[1][channel] for channel in ['red', 'green', 'blue', 'transp']}
        },
    }
    return extracted


def extract_pixel_format(raw_pixel_format):
    if raw_pixel_format['grayscale']:
        return 'A'+str(raw_pixel_format['bits_per_pixel'])
    sorted_channels = sorted(raw_pixel_format['channels'].items(), key=lambda item: (-item[1]['length'], item[1]['offset']), reverse=True)
    lens = filter(lambda len_: len_ != 0, map(lambda channel: channel[1]['length'], sorted_channels))
    equal_size = 1 == len(set(lens))
    seq = str.replace(''.join(map(lambda channel: channel[0][0].upper(), sorted_channels)), 'T', 'A')
    return seq + str(raw_pixel_format['bits_per_pixel']) + ('' if equal_size else '_'+''.join(map(str, lens)))


def minimal_info(extracted_info):
    minimal = {
        'resolution': extracted_info['real_resolution'],
        'size': extracted_info['size'],
        'pixel_format': extract_pixel_format(extracted_info['pixel_format'])
    }
    return minimal


def get(fbdev=None):
    info = fbdev_metadata.get(fbdev)
    info = extract_info(info)
    info = minimal_info(info)
    return info
