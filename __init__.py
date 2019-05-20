from . import main, __feed__, __feed__ as feed


def start(background_path, feed=__feed__.__drawer__, *argv):
    main.main([background_path] + list(argv), feed)
