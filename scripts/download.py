# this script downloads a benchmarksgame report page and 
# installs it locally.

# NAME="nbody-gpp-0"

# URL=https://benchmarksgame-team.pages.debian.net/benchmarksgame/program/${NAME}.html
# PAGE=$(wget ${URL} -q -O -)

# echo $PAGE

def download(name: str):
    pass


if __name__=='__main__':
    download("nbody-gpp-0")