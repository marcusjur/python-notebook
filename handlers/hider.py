from PIL import Image
import string
import colorama

startingPixel = (10, 10, 255)
endingPixel = (255, 255, 255)
lettersToPixels = {}
pixelsToLetters = {}


def init_dictionaries():
    for i, letter in enumerate(string.ascii_letters + string.digits + ' '):
        lettersToPixels[letter] = i
        pixelsToLetters[i] = letter


def hide_key(photo_path, key):
    """
    Hide the given key within the image located at the specified photo_path.

    :param photo_path: The file path of the image.
    :param key:
    :return:
    """
    init_dictionaries()

    # AST100: Asserts should only be used in tests. Asserts are typically bypassed in a production environment.
    assert len(key) == 43, "Key must be 128-bit long."
    image = Image.open(photo_path)
    width, height = image.size
    assert len(key) < width, "Key length exceeds image width."

    image.putpixel((0, 0), startingPixel)

    for index, char in enumerate(key):
        image.putpixel((index + 1, 0), (11, lettersToPixels[char], 11))

    image.putpixel((len(key) + 1, 0), endingPixel)

    image.save(photo_path)

    print(colorama.Fore.RED + "The night has thousands of eyes." + colorama.Style.RESET_ALL)


def read_key(photo_path):
    """
    Reads the key from the given photo_path.

    :param photo_path: Path to the photo.
    :return: The key read from the photo
    """
    init_dictionaries()

    image = Image.open(photo_path)
    key = ''
    index = 1

    while True:
        pixel = image.getpixel((index, 0))
        if pixel == endingPixel:
            break
        try:
            key += pixelsToLetters[pixel[1]]
        except KeyError:
            pass
        index += 1

    print(colorama.Fore.RED + "If you want to go unnoticed, be in plain sight!" + colorama.Style.RESET_ALL)

    return key + '='


# Example usage
# hide_key("../key.png", "9P18b4PIOJRvHusXxKSppGJlxVhH1LSlM6nVC8eLzn8")
# print(read_key("../key.png"))
# assert read_key("../key.png") == "9P18b4PIOJRvHusXxKSppGJlxVhH1LSlM6nVC8eLzn8="
