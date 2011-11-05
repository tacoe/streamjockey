import logging
import subprocess
import os
import argparse
import tempfile
import sys

__author__ = 'boaz'


spotify_suckc= os.path.normpath(os.path.join(os.path.dirname(__file__), "../bin/spotifysuck_c"))

logger = logging.getLogger("spotisuck")


def suckit(username,password,trackid,output_file):


    tmp_file = os.path.join(tempfile.gettempdir(),"%s.raw" % (os.path.basename(output_file),))

    cmd = "%s -u %s -p %s -l %s -f %s" % (spotify_suckc,username, password,trackid,tmp_file)
    logger.info("Downloading %s, cmd: %s",trackid,cmd)

    return_val = subprocess.call(cmd,shell=True)
    if return_val:
        raise Exception("Spotify suckc failed. Bummer. Cmd %s " % (cmd,))

    cmd = "sox -r 44100 -e signed -b 16 -c 2 -s --endian little %s %s" % \
          (tmp_file,output_file)
    logger.info("Converting %s, cmd: %s",trackid,cmd)
    return_val = subprocess.call(cmd,shell=True)
    if return_val:
       raise Exception("Convertion failed. Bummer. Cmd %s " % (cmd,))

    os.remove(tmp_file)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--user', action="store", dest="username",help="spotify username")
    parser.add_argument('-p','--password', action="store", dest="password",help="spotify password")
    parser.add_argument('-t','--trackid', action="store", dest="trackid",help="spotify trackid")
    parser.add_argument('-o','--output', action="store", dest="output",help="output file")
    arguments = parser.parse_args()

    logger.setLevel(logging.DEBUG)
    ch= logging.StreamHandler(sys.stdout)

    # create formatter
    formatter = logging.Formatter("%(asctime)s | %(process)d|%(thread)d | %(name)s | %(levelname)s | %(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)

    logger.addHandler(ch)


    suckit(arguments.username,arguments.password,arguments.trackid,arguments.output)


if __name__ == "__main__":
    main()