from ._main import main
import logging
logging.basicConfig(filename='/home/ccaruser/lidar.log', level=logging.INFO)


try:
    main()
except Exception as e:
    logging.exception(e)
